#!flask/bin/python

from newspaper import Article
from textblob import TextBlob
import io
import os
import requests
from tqdm import tqdm
from flask import Flask, request, send_file
from pydub import AudioSegment
from flask_caching import Cache


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
def getAudioForSentence(sentence,
                        mozillatts_api_url=os.environ.get(
                            'MOZILLATTS_API_URL',
                            'http://localhost:5002/api/tts')):
    sentence_str = str(sentence).replace('\n', '. ').encode('utf-8')
    resp = requests.post(
        mozillatts_api_url,
        data=sentence_str)
    assert resp.status_code == requests.codes.ok
    # print(f'Failed at "{sentence}": {resp.status_code}: {resp.reason}')
    # else:
    return resp.content


def getAudioForBlob(blob: TextBlob):
    '''
    Takes a TextBlob object.
    Returns a dictionary from each sentence (TextBlob) to a Pydub Segment.
    '''
    sent_to_segments = dict()
    with tqdm(blob.sentences, desc='Sentences') as pbar:
        for sentence in pbar:
            wave_bytes = getAudioForSentence(sentence)

            # Convert to Segment.
            wave_file_io = io.BytesIO(wave_bytes)
            segment = AudioSegment.from_file(wave_file_io, format="wav")
            sent_to_segments[str(sentence)] = segment
    return sent_to_segments


def combineSegmentsForBlobIntoWav(sent_to_segments, blob) -> AudioSegment:
    playlist = AudioSegment.empty()
    for sentence in blob.sentences:
        segment = sent_to_segments[str(sentence)]
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
    sent_to_segments = getAudioForBlob(blob)
    playlist = combineSegmentsForBlobIntoWav(sent_to_segments, blob)
    wav_bytes = convertSegmentToWavBytes(playlist)
    return send_file(wav_bytes, mimetype='audio/wav')


if __name__ == '__main__':
    app.run(host='127.0.0.1')
