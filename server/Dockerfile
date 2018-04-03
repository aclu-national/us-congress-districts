FROM mdillon/postgis

WORKDIR /app

RUN apt-get update
RUN apt-get install -y python python-pip
RUN pip install flask flask_cors psycopg2-binary

ADD server.py server.py
ADD pgdata pgdata
ADD start.sh start.sh

RUN chown -R postgres pgdata
RUN chmod 700 pgdata

EXPOSE 5000
ENV PGDATA /app/pgdata

CMD /app/start.sh
