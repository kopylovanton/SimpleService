# Предвариетльная настройка сервера 
Требуется создать пользователя, установить python 3 и необходимые пакеты (в том числе апликационный сервер Gunicorn) , 
установить и настроить Oracle client, утсановить Nginx.

Разработкчики апликационного сервера Gunicorn строго рекомендуют 
(http://docs.gunicorn.org/en/latest/deploy.html) 
использовать его в связке с Nginx для защиты от возможных ddos атак и защиты от медленных подключений.

### Последовательность установки. 
Примеры команд приведены для Ubuntu из https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04
Анологичный пример для Centos https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-centos-7

1. Создать пользователя flask
> adduser flask
> usermod -aG sudo flask

5. Установить python 3.6
> sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
> sudo apt install python3-venv
> sudo apt install python-pip

6. Настроить окружение python для сервисов 
> mkdir ~/api
> cd ~/api
> python3.6 -m venv python-api-env

7. Установить пакеты python перечисленные в requirements.txt 
> source ~/api/python-api-env/bin/activate
> (python-api-env) $ sudo -H pip install wheel
> (python-api-env) $ sudo -H pip install -r requirements.txt

8. Установить клиент Oracle
https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html
https://help.ubuntu.com/community/Oracle%20Instant%20Client

- загрузить на сервер Basic клиент https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html
> sudo apt-get install alien
> sudo alien -i oracle-instantclient19.5-basic-19.5.0.0.0-1.x86_64.rpm 
> sudo apt-get install libaio1
> export LD_LIBRARY_PATH=/usr/lib/oracle/19.5/client64/lib/${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
> sudo ldconfig

- создать файл, добавить в него две записи и сохранить
> sudo vi /etc/profile.d/oracle.sh && sudo chmod o+r /etc/profile.d/oracle.sh
export ORACLE_HOME=/usr/lib/oracle/19.5/client64
export PATH=$PATH:$ORACLE_HOME/bin

> sudo ln -s /usr/include/oracle/19.5/client $ORACLE_HOME/include

2. Уствновить Nginx https://nginx.org/ru/linux_packages.html 
> sudo apt update
> sudo apt install nginx
> sudo systemctl enable nginx
> systemctl status nginx

4. настройка файревола
> sudo ufw app list
> sudo ufw allow OpenSSH
> sudo ufw allow 'Nginx HTTP'
> sudo ufw allow 'Nginx HTTPS'
> sudo ufw enable

5. Добвить пользователя flask в группу www-data
> sudo usermod -a -G www-data flask

# Администрирование
1. Управление Nginx
* Запуск
>sudo systemctl stop nginx
* Остановка
>sudo systemctl start nginx
* Перечитать конфигурацию
>sudo systemctl reload nginx
* Статус
> systemctl status nginx

