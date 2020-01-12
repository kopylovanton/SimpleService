#!/bin/bash
source ~/api/python-api-env/bin/activate
gunicorn -c ./config/gunicorn.py wsgi_get:app