#!/usr/bin/env bash

su - postgres -c '/usr/lib/postgresql/10/bin/pg_ctl -D /app/pgdata start'
python /app/server.py
