#!/bin/bash
# $0 is the script name, $1 id the first ARG
if [ -z "$1" ]
  then
    echo "No New Service Name argument supplied -- ./setup.sh <newServiceName>"
    exit
fi

serviceName="$1"
source /home/flask/api/python-api-env/bin/activate
cd /home/flask/api/$serviceName
pwd
cwd=$(pwd)
python3 $cwd/template/setup_new_service.py --newName $serviceName --tempName "+-template-+" || { echo '!!!Finish with ERROR: checks and rename failed' ; exit 1; }
mkdir -p /home/flask/api/socket
mkdir -p /home/flask/api/nginx
echo "{'rc': 500, 'message': 'Internal server error'}" > /home/flask/api/nginx/500.json
echo "{'rc': 404, 'message': 'Can not find resources'}" > /home/flask/api/nginx/404.json
chown -R flask:nginx /home/flask/api/
chmod +x run.sh
sudo cp ./template/systemd/api-template.service ./template/systemd/api-$serviceName.service || { echo '!!!Finish with ERROR: service move failed' ; exit 1; }
sudo cp ./template/systemd/api-$serviceName.service /etc/systemd/system || { echo '!!!Finish with ERROR: service copy failed' ; exit 1; }
sudo chmod 775 /etc/systemd/system/api-$serviceName.service
sudo systemctl daemon-reload || { echo '!!!Finish with ERROR: systemd comand failed' ; exit 1; }
sudo systemctl enable api-$serviceName

sudo cp ./template/nginx/api-config /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/api-config /etc/nginx/sites-enabled

echo '--- Nginx conf test'
sudo nginx -t || { echo '!!!Finish with ERROR: Nginx conf test' ; exit 1; }
echo '---'

echo '-------------------------'
echo '-- Setup has completed --'
echo '-------------------------'