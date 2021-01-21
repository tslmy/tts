# A patch to `synesthesiam/docker-mozillatts`

This is my patched version of the Docker Image [`synesthesiam/docker-mozillatts`](https://github.com/synesthesiam/docker-mozillatts). It replaces the Flask HTTP server with Gunicorn.

A side effect is that I had to bypass the Argument Parser, because it attempts to parse the arguments intended for the `gunicorn` command and will fail.

I'm considering making a pull request to the original repo. I've filed a [tracking issue](https://github.com/synesthesiam/docker-mozillatts/issues/15) for that.