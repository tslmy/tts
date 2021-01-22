FROM condaforge/mambaforge
MAINTAINER tslmy
COPY . ~/
WORKDIR ~/
RUN mamba install --file conda-requirements.txt -y && \
    pip install -r pip-requirements.txt && \
    python -m textblob.download_corpora
EXPOSE 80
CMD gunicorn main:app --bind 0.0.0.0:80 --timeout 3600 --worker-class sanic.worker.GunicornWorker