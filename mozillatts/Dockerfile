FROM synesthesiam/mozillatts

RUN bin/python3 -m pip install -f download/ 'gunicorn'
COPY __init__.py tts_web/
ENTRYPOINT ["bin/gunicorn", "--bind", "0.0.0.0:5002", "--timeout", "3600", "tts_web:app"]
