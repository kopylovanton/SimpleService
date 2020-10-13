Предваритльная настройка сервера 
=================================
Для предварительной настройки сервиса потребуется:
- Добавить служебного пользователя базы данных Oracle "flask" (данная инструкция не описывает этот шаг)
- Настроить Linux сервер приложений (последовательность описана в данной интсрукции)

Для настройки Linux сервера потребуется создать системного пользователя, установить python 3 и необходимые пакеты, 
установить и настроить Oracle client, утсановить Nginx.

Последовательность установки. 
============================
Создать системного пользователя flask
```shell script
$ adduser flask
$ usermod -aG sudo flask
```
--------------------------------------------------------
Установить python 3.6
```shell script
su flask
cd ~/
sudo apt update
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install python3-venv
sudo apt install python-pip
```
--------------------------------------------------------
Настроить окружение python для сервисов 
```shell script
mkdir ~/api
cd ~/api
mkdir ~/socket
python3.6 -m venv python-api-env
```
--------------------------------------------------------
Установить клиент Oracle

Рекомендации приведены на основе материалов:
**[cx-oracle.readthedocs.io](https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html])**
и **[help.ubuntu.com](https://help.ubuntu.com/community/Oracle%20Instant%20Client])**

- [загрузить на сервер Basic клиент](https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html)
```shell script
sudo apt-get install alien
sudo alien -i oracle-instantclient19.5-basic-19.5.0.0.0-1.x86_64.rpm 
sudo apt-get install libaio1
export LD_LIBRARY_PATH=/usr/lib/oracle/19.5/client64/lib/${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
sudo ldconfig
```

- создать файл, добавить в него две записи и сохранить
```shell script
sudo nano /etc/profile.d/oracle.sh && sudo chmod o+r /etc/profile.d/oracle.sh
export ORACLE_HOME=/usr/lib/oracle/19.5/client64
export PATH=$PATH:$ORACLE_HOME/bin
```

- выполнить команды
```shell script
sudo ln -s /usr/include/oracle/19.5/client $ORACLE_HOME/include
sudo mkdir  -p /etc/orcale
```

- создать файл, добавить одну строку и сохранить

```shell script
sudo nano /etc/orcale/sqlnet.ora

SQLNET.OUTBOUND_CONNECT_TIMEOUT = 5000 ms
```

--------------------------------------------------------
[Установить Nginx] (https://nginx.org/ru/linux_packages.html)

```shell script
sudo apt install nginx
sudo systemctl enable nginx
systemctl status nginx
```

--------------------------------------------------------
Настройка файревола
```shell script
sudo ufw app list
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx HTTP'
sudo ufw allow 'Nginx HTTPS'
sudo ufw enable
```

--------------------------------------------------------
Добвить пользователя flask в группу www-data
```shell script
sudo usermod -a -G nginx flask
```
--------------------------------------------------------
после установке Nginx с помощью браузера по IP адресу сервера можно увидеть стандартное приветственное окно 

--------------------------------------------------------

примеры команд администрирование Nginx
1. Управление Nginx
* Запуск
```shell script
sudo systemctl stop nginx
```

* Остановка
```shell script
sudo systemctl start nginx
```

* Статус
```shell script
systemctl status nginx
```

--------------------------------------------------------

Примеры команд приведены для Ubuntu из [www.digitalocean.com](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)

[Анологичный пример для Centos](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-centos-7)

**При отладке конфигурации использовались только 64 битные компоненты**
