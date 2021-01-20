#!flask/bin/python

from newspaper import Article
from textblob import TextBlob
import io
import requests
from tqdm import tqdm
from flask import Flask, request, send_file
from pydub import AudioSegment


def getTextFromUrl(url: str) -> str:
    '''
    Retrieves text of an article at the given URL.
    '''
    article = Article(url)
    article.download()
    article.parse()
    return article.text


def getAudioForBlob(blob: TextBlob):
    '''
    Takes a TextBlob object.
    Returns a dictionary from each sentence (TextBlob) to a Pydub Segment.
    '''
    sent_to_segments = dict()
    with tqdm(blob.sentences, desc='Sentences') as pbar:
        for sentence in pbar:
            resp = requests.post(
                'http://localhost:5002/api/tts',
                data=str(sentence).replace('\n', '. ').encode('utf-8'))
            if resp.status_code != requests.codes.ok:
                print(f'Failed at "{sentence}": {resp.status_code}: {resp.reason}')
                continue
            # else:
            wave_bytes = resp.content

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


app = Flask(__name__)
silence = AudioSegment.silent(duration=400)  # in ms


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


def main():
    '''
    To test, use:
    curl -G --output - \
        --data-urlencode 'url=https://sjmulder.nl/en/' \
        'http://localhost:5000/' | \
        play -
    '''
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
