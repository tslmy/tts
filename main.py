#!flask/bin/python

from newspaper import Article
from textblob import TextBlob
import io
import os
from tqdm import tqdm
from flask import Flask, request, send_file
from pydub import AudioSegment
from flask_caching import Cache
import asyncio
import aiohttp

app = Flask(__name__)
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': 'cache',
})

silence = AudioSegment.silent(duration=400)  # in ms


def getTextFromUrl(url: str) -> str:
    '''
    Retrieves text of an article at the given URL.
    '''
    article = Article(url)
    article.download()
    article.parse()
    return article.text


@cache.memoize()
async def getAudioForSentence(sentence: str, client,
                              mozillatts_api_url=os.environ.get(
                                  'MOZILLATTS_API_URL',
                                  'http://localhost:5002/api/tts')):
    async with client.post(mozillatts_api_url, data=sentence) as resp:
        assert resp.status == 200
        # Get WAV as binary.
        wave_bytes = await resp.content.read()
        # Convert to Segment.
        wave_file_io = io.BytesIO(wave_bytes)
        segment = AudioSegment.from_file(wave_file_io, format="wav")
        return sentence, segment


def sanitize(sentence) -> str:
    return str(sentence).replace('\n', '. ').encode('utf-8')


async def getAudioForBlob(blob: TextBlob):
    '''
    Takes a TextBlob object.
    Returns a dictionary from each sentence (TextBlob) to a Pydub Segment.
    '''
    async with aiohttp.ClientSession() as client:
        futures = []
        for sentence in blob.sentences:
            sentence_str = sanitize(sentence)
            future = getAudioForSentence(sentence_str, client)
            futures.append(future)
        responses = await asyncio.gather(*futures)
        sent_to_segments = {sent: seg for sent, seg in responses}
        return sent_to_segments


def combineSegmentsForBlobIntoWav(sent_to_segments, blob) -> AudioSegment:
    playlist = AudioSegment.empty()
    for sentence in blob.sentences:
        segment = sent_to_segments[sanitize(sentence)]
        playlist += segment + silence
    return playlist


def convertSegmentToWavBytes(segment: AudioSegment):
    # Convert to an in-memory WAV file:
    out_bytes = io.BytesIO()
    segment.export(out_bytes, format='wav')
    # return its content:
    out_bytes.seek(0)
    return out_bytes


@app.route('/', methods=['GET'])
def tts():
    url = request.args.get('url')
    print(f"URL input: {url}")

    text = getTextFromUrl(url)
    blob = TextBlob(text)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sent_to_segments = loop.run_until_complete(getAudioForBlob(blob))

    playlist = combineSegmentsForBlobIntoWav(sent_to_segments, blob)
    wav_bytes = convertSegmentToWavBytes(playlist)
    return send_file(wav_bytes, mimetype='audio/wav')


if __name__ == '__main__':
    app.run(host='127.0.0.1')
