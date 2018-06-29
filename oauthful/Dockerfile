FROM alpine

ENV PYTHONPATH=/srv/

COPY ./app.py /srv/oauthful/app.py

RUN apk --no-cache add py3-flask py3-gunicorn

EXPOSE 8000

CMD ["/usr/bin/gunicorn", "-w4", "-b", "0.0.0.0:8000", "oauthful.app:app"]
