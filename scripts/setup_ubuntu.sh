#!/bin/bash

if [ "$EUID" -ne 0 ]
	then echo "Please run with admin privs: sudo ./scripts/setup_ubuntu.sh"
	exit
fi

PROJECT="/usr/local/aclu/us-congress-district-shapes"
POSTGRES_VERSION="9.5"
POSTGRES_MAIN="/etc/postgresql/$POSTGRES_VERSION/main"

apt update
apt upgrade -y

apt install -y fail2ban ufw htop emacs24-nox postgresql postgresql-contrib \
               build-essential gdal-bin python python-pip python-gevent

ufw allow 5000
ufw allow 22
yes | ufw enable

add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable

apt update
apt install -y postgis

pip install --upgrade pip
pip install flask flask_cors psycopg2-binary gunicorn bs4 urllib3 certifi arrow

if [ -f "$POSTGRES_MAIN/postgresql.conf" ] ; then
	mv "$POSTGRES_MAIN/postgresql.conf" "$POSTGRES_MAIN/postgresql.conf.bak"
fi

cp "$PROJECT/server/postgresql.conf" "$POSTGRES_MAIN/postgresql.conf"
service postgresql restart

sudo -u postgres createuser --superuser ubuntu
sudo -u ubuntu createdb us_congress
sudo -u ubuntu psql -d us_congress -c "CREATE EXTENSION postgis;"
