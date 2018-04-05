#!/usr/bin/env bash

/usr/lib/postgresql/10/bin/pg_ctl -D /app/pgdata start
gunicorn -c gunicorn.py server:app
