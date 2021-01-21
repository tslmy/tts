FROM condaforge/mambaforge
MAINTAINER tslmy
COPY . ~/
WORKDIR ~/
RUN mamba install --file conda-requirements.txt -y
RUN python -m textblob.download_corpora
EXPOSE 80
CMD gunicorn main:app --bind 0.0.0.0:80 --timeout 3600