Предваритльная настройка сервера 
=================================
Для предварительной настройки сервиса потребуется:
- Добавить служебного пользователя базы данных Oracle "flask" (данная инструкция не описывает этот шаг)
- Настроить Linux сервер приложений (последовательность описана в данной интсрукции)

Для настройки Linux сервера потребуется создать системного пользователя, установить python 3 , 
установить и настроить Oracle client, утсановить Nginx.

Последовательность установки. 
============================
Создать системного пользователя flask
```shell script
$ adduser flask
$ passwd flask
$ gpasswd -a flask wheel
```
--------------------------------------------------------
Установить python 3
```shell script
$ su flask
$ cd ~/
$ sudo yum install python3-pip
$ sudo yum install gcc
$ python3 -m pip install --upgrade pip
$ pip3 install wheel
$ sudo yum install nano
```
--------------------------------------------------------
Настроить окружение python для сервисов 
```shell script
$ mkdir ~/api
$ mkdir ~/api/socket
$ cd ~/api
$ python3.6 -m venv python-api-env
```
--------------------------------------------------------
Установить клиент Oracle

- [загрузить на сервер Basic Package (RPM)](https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html)
```shell script
$ sudo yum install libaio
$ sudo yum install oracle-instantclient19.8-basic-19.8.0.0.0-1.x86_64
$ export LD_LIBRARY_PATH=/usr/lib/oracle/19.8/client64/lib/${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
$ sudo ldconfig
```

- создать файл
```shell script
$ sudo nano /etc/profile.d/oracle.sh && sudo chmod o+r /etc/profile.d/oracle.sh
```
добавить в него две записи и сохранить
```
export ORACLE_HOME=/usr/lib/oracle/19.8/client64
export PATH=$PATH:$ORACLE_HOME/bin
```

- выполнить команды
```shell script
$ sudo ln -s /usr/include/oracle/19.8/client $ORACLE_HOME/include
$ sudo mkdir  -p /etc/orcale
```

- создать файл

```shell script
$ sudo nano /etc/orcale/sqlnet.ora
```
добавить одну строку и сохранить
```
SQLNET.OUTBOUND_CONNECT_TIMEOUT = 5000 ms
```

--------------------------------------------------------
[Установить Nginx] (https://nginx.org/ru/linux_packages.html)

- создать файл

```shell script
$ sudo nano /etc/yum.repos.d/nginx.repo
```
добавить строки и сохранить

```
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/mainline/centos/7/$basearch/
gpgcheck=0
enabled=1
```
```shell script
$ sudo yum install nginx
$ sudo setsebool httpd_can_network_connect on -P
$ sudo systemctl start nginx
$ sudo systemctl enable nginx
$ sudo systemctl status nginx
$ sudo gpasswd -a flask nginx
$ sudo gpasswd -a nginx flask
$ sudo mkdir /etc/nginx/sites-available
$ sudo usermod -a -G flask nginx
$ sudo chmod 770 /home/flask
```

скопировать файлы ./centos7_semodule/mynginx.pp , ./centos7_semodule/mynginx.te на сервер и выполнить команду из каталога с этими файлами

````shell script
$ sudo semodule -i mynginx.pp
````

добавить строку  в конец секции http "include /etc/nginx/sites-available/*;"
```shell script
$ sudo nano /etc/nginx/nginx.conf
```
```
...
include /etc/nginx/sites-available/*;
```

поменять настройки логирования access_log для исключения из лога успешно проведенных операций
заменить
```
access_log /path/to/access.log
```
на

```
map $status $loggable {
    ~^[23]  0;
    default 1;
}

access_log /var/log/nginx/access.log combined if=$loggable;
```
проверить конфигурацию nginx

```shell script
$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

```
--------------------------------------------------------
В случае получения 403 ошибки при запуске сервиса и наличия ошибок failed (13: Permission denied) while connecting to upstream
в логе /var/log/nginx/error.log

```shell script
$ sudo cat /var/log/audit/audit.log | grep nginx | grep denied | audit2allow -M mynginx
$ sudo semodule -i mynginx.pp
```

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

Примеры команд приведены из 
[для Centos](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-centos-7)

[cx-oracle.readthedocs.io](https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html])**

**При отладке конфигурации использовались только 64 битные компоненты**
