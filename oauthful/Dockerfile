FROM foundries/ota-api

ENV PYTHONPATH=/srv/oauthful:/srv/ota-api

COPY ./app.py /srv/oauthful/oauthful/
COPY ./user.py /srv/oauthful/oauthful/

EXPOSE 8000

CMD ["/usr/bin/gunicorn", "-w4", "-b", "0.0.0.0:8000", "oauthful.app:app"]
