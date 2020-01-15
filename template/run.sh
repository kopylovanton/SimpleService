#!/bin/bash
export TNS_ADMIN=/etc/oracle
source ~/api/python-api-env/bin/activate
gunicorn -c ./config/gunicorn.py wsgi_get:app