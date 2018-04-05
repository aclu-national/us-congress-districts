FROM mdillon/postgis

WORKDIR /app

RUN apt-get update
RUN apt-get install -y python python-pip python-gevent
RUN pip install flask flask_cors psycopg2-binary gunicorn

ADD server.py server.py
ADD gunicorn.py gunicorn.py
ADD pgdata pgdata
ADD start.sh start.sh

RUN adduser app
RUN chown -R app pgdata
RUN chmod 700 pgdata
USER app

CMD /app/start.sh
