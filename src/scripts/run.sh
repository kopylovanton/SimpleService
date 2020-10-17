#!/bin/bash
export TNS_ADMIN=/etc/oracle
source ~/api/python-api-env/bin/activate
python3 /home/flask/api/+-template-+/start_server.py --path=/home/flask/api/socket/+-template-+.sock
