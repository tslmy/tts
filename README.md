# My TTS Service

This is my own scrambled-up TTS Service.


## Usage

Assuming you are using macOS,

1. Make sure that you have `sox` installed: `brew install sox`. This provides the playback command `play`. If you are on Linux, `aplay` should do.
2. Create a conda env: `conda env create -n tts -f conda-requirements.txt -y`.
3. Activate the env: `conda activate tts`.
4. Start the Flask server: `FLASK_APP=main.py FLASK_ENV=development flask run`.

Now, in another terminal, use:

```shell
curl -G --output - \
    --data-urlencode 'url=https://sjmulder.nl/en/' \
    'http://localhost:5000/' | \
    play -
```
