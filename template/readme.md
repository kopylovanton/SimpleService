Конфигурирование нового сервиса
===============================
В данном разделе представлена конфигурации базового сервиса 
на основе select * from dual запроса.

Предусловие: выполнены настройки сервера из описание /install/readme.md
Предполагается, что все сервисы подключаются к базе данных Oracle под одним служебным пользователем flask.

При разворачивании очередного сервиса на сервере необходимо:

- придумать уникальной имя сервиса, например getAuthList
- скопировать базовую конфигурацию на Linux сервер под пользователем flask по пути ~/api/<service name>/
- сконфигурировать согласно инструкции новый сокет и сервис для службы serviced
- произвести настройку межкомпонентного взаимодействия  
- провести настройку или скопировать готовую конфигурацию сервиса
- предоставить пользователю flask базы данных права на select/execute для объектов из Select выражения

Перечень файлов
---------------
- /config/config_get.yaml  - конфигурации сервиса
- /config/configdb.yaml - параметры доступа к базе данных. Пароль указаывается в открытом виде и автоматически шифруется и заменяется в файле при первом запуске
- /config/gunicorn.py - параметры аппликационного сервера. Тут можно конфигурировать количество потоков/воркеров (не более 2хКоличество ядер +1)
- /logs/ - сюда будут сохранены логи после старта сервиса 
- /nginx/ - конфигурация Nginx
- /resources/ - исполняемый код 
- /systemd/ - шаблоны конфигураций сервиса и сокета
- run.sh - скрипт запуска (его использует сервис systemd для запуска приложения) 
- wsgi_get.py - базовый wsgi исполняемый файл



Конфигурирование сервиса /config
------------------------

- скопировать содержимое /template в ~/api/<service name>/
- выполнить 
```
sudo chown -R flask:www-data ~/api/
sudo chmod +x run.sh 
```

### Редактирование /config/config_get.yaml

**если вы устанавливаете заранее подготовленную конфигурацию просто замените этот файле**

```
nano config/config_get.yaml
```
Параметр|Назначенение
--------|------------
URL| базовый адрес для сервиса `<host>:<port>/<url>` . Замените на уникальное значение
LOG_LEVEL| 10-Debug, 20-Info production level
SQL_GET| запрос для GET метода сервиса. Начинается с управляющего символа `>` который указывает в yaml натации на многострочный параметр. Не удаляйте этот символ для избежании ошибок парсера. Имена возвращаемых полей и входящих параметров должно быть согласовано с секцией `SPECIFICATIONS`. Не забудьте предоставить права на вызываемые объекты Oracle для пользователя flask
MAX_FETCH_ROWS| максимальное количество строк, которое будет обработано. Защищает от не правильных SQL
SPECIFICATIONS| описание входящих и исходящих полей в yaml синтексисе. Сохраняйте отсутпы так как это указано в примере для избежания ошибок парсера

### Редактирование /config/configdb.yaml

```
nano config/configdb.yaml
```
параметры подключения к базе данных. Необходимо указать актуальные параметры

Параметр|Назначенение
--------|------------
DB_CONN_STRING|строка подключения
DB_ENCODING|кодировка базы данных
DB_USER_NAME| имя пользователя
DB_USER_PASSWORD| пароль, после первого запуска пароль автоматически шифруется и перезаписывается в файл в шифрованном виде
CURRENT_SCHEMA|имя пользователя владельца схемы по умолчанию 

### Редактирование /config/gunicorn.yaml
```
nano config/gunicorn.py
```
параметры аппликационного сервера описаны в [документации gunicorn](http://docs.gunicorn.org/en/latest/configure.html#framework-settings).
Можно не редактировать параметры. колчиство воркеров по умолчанию 4ре (параметр workers)

Настройка межкомпонентного взаимодействия
-----------------------------------

- переименовать файл api-<service_name>.socket и api-<service_name>.socket
отредактировать файл. Заменить template на действительное 
уникальное имя сервиса (например getauthlist)
```
sudo mv api-template.service api-<service_name>.service
sudo mv api-template.socket api-<service_name>.socket
```

и отредактировать файлы 


```
nano api-<service_name>.service
```

```
Description=Service1 api daemon
Requires=api-service1.socket
#change path !!!!
WorkingDirectory=/home/flask/api/<service_name>
```

```
sudo nano api-<service_name>.socket
```
> Change name template -> ??? !!!
ListenStream=/home/flask/api/socket/<service_name>.sock

- выполнить команды (примеры приведены для сервиса с названием <service_name>=getauthlist)
```
sudo cp api-getauthlist.service /etc/systemd/system
sudo cp api-getauthlist.socket /etc/systemd/system
sudo chmod 755 /etc/systemd/system/api-getauthlist.service
sudo chmod 755 /etc/systemd/system/api-getauthlist.socket
sudo systemctl daemon-reload
sudo systemctl start api-getauthlist.socket
sudo systemctl enable api-getauthlist.socket
```

Проверка
--------
```
sudo systemctl status api-getauthlist.socket
sudo file /home/flask/api/socket/getauthlist.sock
```

>Output - /home/flask/api/socket/getauthlist.sock: socket

Если команда systemctl status указывает на ошибку, или если 
в каталоге отсутствует файл <service_name>.sock, это означает, что 
сокет не удалось создать. Проверьте журналы сокета с помощью следующей команды:

```
sudo journalctl -u api-<service_name>.socket
```

Еще раз проверьте файл /etc/systemd/system/api-getauthlist.socket и 
устраните любые обнаруженные проблемы, прежде чем продолжить


Настройка конфигурации Nginx
----------------------------
Скопировать **только** для первого сервиса 
```
sudo cp nginx/api-config /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/api-config /etc/nginx/sites-enabled
```

Изменить конфигурацию
```
sudo nano /etc/nginx/sites-available/api-config
```
укзать корректное имя сервера и/или ip адрес
```
# set the correct host(s) for your server
server_name api-flask 192.168.1.38;
``` 
    
 изменить для первого сервиса или 
 добавить блок заменив два раза template на имя нового сервиса,
 например getauthlist
 
 ```
    location /getauthlist {
      proxy_redirect   off;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_pass http://unix:/home/flask/api/socket/service1.sock;
    }
```
Протестируйте конфигурацию Nginx на ошибки синтаксиса:
```
sudo nginx -t
```

Если ошибок не будет найдено, перезапустите Nginx с помощью следующей команды:
```
sudo systemctl restart nginx
```
Примеры команды управления сервисом
----------------------------------
### Start your service
```
systemctl start api-authlist
systemctl start api-authlist.socket
```

### Obtain your services' status
```
systemctl status api-authlist
```
### Stop your service
```
systemctl stop api-authlist
systemctl stop api-authlist.socket
```

----------------------
Общие сведения по установке и настройки более подробно можно получить например из этих статей
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04-ru 
https://www.8host.com/blog/obsluzhivanie-prilozhenij-flask-s-pomoshhyu-gunicorn-i-nginx-v-ubuntu-16-04/
