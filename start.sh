#!/bin/sh

gunicorn \
  -k uvicorn.workers.UvicornWorker \
  -w ${WORKERS:-4} \
  app.main:app \
  -b 0.0.0.0:8000