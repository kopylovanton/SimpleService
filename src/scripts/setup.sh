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
cp ./template/systemd/api-template.service ./template/systemd/api-$serviceName.service || { echo '!!!Finish with ERROR: service move failed' ; exit 1; }
cp ./template/systemd/api-template.socket ./template/systemd/api-$serviceName.socket || { echo '!!!Finish with ERROR: socket move failed' ; exit 1; }
cp ./template/systemd/api-$serviceName.service /etc/systemd/system || { echo '!!!Finish with ERROR: service copy failed' ; exit 1; }
cp ./template/systemd/api-$serviceName.socket /etc/systemd/system || { echo '!!!Finish with ERROR: socket move failed' ; exit 1; }
chmod 755 /etc/systemd/system/api-$serviceName.service
chmod 755 /etc/systemd/system/api-$serviceName.socket
systemctl daemon-reload || { echo '!!!Finish with ERROR: systemd comand failed' ; exit 1; }
systemctl start api-$serviceName.socket
systemctl enable api-$serviceName.socket
systemctl enable api-$serviceName
echo 'Wait 3 sec'
sleep 3
echo 'Check service status'
systemctl status api-$serviceName.socket || { echo '!!!Finish with ERROR: Socket file check failed' ; exit 1; }
file /home/flask/api/socket/$serviceName.sock || { echo '!!!Finish with ERROR: Socket check failed' ; exit 1; }

cp ./template/nginx/api-config /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/api-config /etc/nginx/sites-enabled

echo '--- Nginx conf test'
sudo nginx -t || { echo '!!!Finish with ERROR: Nginx conf test' ; exit 1; }
echo '---'

echo '-------------------------'
echo '-- Setup has completed --'
echo '-------------------------'