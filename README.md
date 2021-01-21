# My TTS Service

This is my own scrambled-up TTS Service.


## Deployment

### To run locally

1. Ensure that you have `conda` ready. If not, may I suggest [Mambaforge][mf]?
1. Run [synesthesiam/docker-mozillatts][mz]: `docker run -it -p 5002:5002 synesthesiam/mozillatts`.
2. Create a conda env: `conda env create -n tts -f conda-requirements.txt -y`.
3. Activate the env: `conda activate tts`.
4. Start the server. There are different ways to do it:
 - Using the **dev** server from [Flask][fl]: `FLASK_APP=main.py FLASK_ENV=development flask run`.
   - Note: Although Flask does have a production mode, it is still [not recommended][nr] for production use. For that, we use...
 - Using the **prod** server from [Gunicorn][gu]: `gunicorn main:app --bind 0.0.0.0:80 --timeout 3600`.
   - 
   - As seen in the `--timeout` option, a request allowed to run for 1h only. Very large text, therefore, may fail.

[mf]: https://github.com/conda-forge/miniforge#mambaforge
[mz]: https://github.com/synesthesiam/docker-mozillatts
[fl]: https://flask.palletsprojects.com/en/1.1.x/
[nr]: https://flask.palletsprojects.com/en/1.1.x/deploying/
[gu]: https://gunicorn.org/

### To run with Docker

Simply do:

```shell
docker-compose up --build
```

Something to note:

- The Dockerfile in this repo is for the URL-to-audio web server only. It still requires the [synesthesiam/docker-mozillatts][mz] image to be running in a container. Therefore, although you can manually set up the 2 containers, the Docker Compose way is always going to be easier.
- It uses Gunicorn instead of the vanilla Flask server.


## Usage

To hear the playback, 
- If you are on macOS, ensure that `sox` is installed: `brew install sox`. This provides the playback command `play`. 
- If you are on Linux, `aplay` should do.

Now, you can convert a webpage (using `https://sjmulder.nl/en/` as an example) into audio using:

```shell
curl -G --output - \
    --data-urlencode 'url=https://sjmulder.nl/en/' \
    'http://localhost:80/' | \
    play -
```
