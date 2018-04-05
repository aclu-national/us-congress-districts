#!/usr/bin/env bash

gunicorn -D -c gunicorn.py server:app
postgres -D /app/pgdata
