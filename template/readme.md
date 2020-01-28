Конфигурирование нового сервиса
===============================
В данном разделе представлена конфигурации базового сервиса 
на основе select * from dual запроса.

Предусловие: 
- выполнены настройки сервера из описание /install/readme.md
- заведен пользователь базы данных Oracle для сервиса (в текущей конфигурации предполагается имя пользователя`flask`) 

При разворачивании очередного сервиса на сервере необходимо:

- придумать уникальной имя сервиса, например getAuthList и создать каталог ```~/api/<service name>/```
- скопировать базовую конфигурацию из каталога ```/template```на Linux сервер под пользователем flask по пути ```~/api/<service name>/```
- Запустить установочный скрипт ```./setup.sh``` для конфигурирования нового системного сокета и сервиса для службы serviced и настройки взаимодействия с nginx  
- провести настройку или скопировать готовую конфигурацию сервиса
- предоставить пользователю flask базы данных права на ``select/execute``` для объектов из Select выражения

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



## Конфигурирование сервиса 

скопировать содержимое /template в ~/api/<new_service_name>/

### Редактирование /config/configdb.yaml

```shell script
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


### Выпонить setup.sh указав в качестве параметра имя нового сервиса

**имя нового сервиса должно совпадать с каталогом в котором располагаются файлы**

```shell script
cd ~/api/<new_service_name>
sudo chmod +x setup.sh 
sudo ./setup.sh <new_service_name>
```

Проверка
--------
```shell script
sudo systemctl status api-<new_service_name>.socket
```

Если команда systemctl status указывает на ошибку проверьте журналы сокета с помощью следующей команды:

```shell script
sudo journalctl -u api-<new_service_name>.socket
```

Еще раз проверьте прежде чем продолжить


Настройка конфигурации Nginx при настройке первого сервиса на этом сервере
----------------------------
Изменить конфигурацию
```shell script
sudo nano /etc/nginx/sites-available/api-config
```
укзать корректное имя сервера и/или ip адрес
```shell script
# set the correct host(s) for your server
server_name api-flask 192.168.1.38;
``` 

Протестируйте конфигурацию Nginx на ошибки синтаксиса:
```shell script
sudo nginx -t
```

Первый запуск
-------------

Если ошибок не будет найдено, перезапустите Nginx с помощью следующей команды:
```shell script
sudo systemctl restart nginx
```
Запустите сервис
```shell script
sudo systemctl start api-<new_service_name>
```
**проверьте логи на наличие ошибок**

```shell script
cat logs/<new_service_name>_main.log
```

в браузере наберите 
```
<host>/<new_service_name>/swagger
```

**Должна отобразиться документация по шаблонному сервису на основе запроса `select from dual`**

Далее необходимо сконфигурировать SQL запрос нового сервиса

## Сконфигурируйте или скопируйте готовую конфигурацию нового сервиса /config/config_get.yaml

- детали по параметрам конфигураиционных файлов смотри в [/template/config](https://github.com/kopylovanton/SimpleService/tree/master/template/config)

Примеры команды управления сервисом
----------------------------------
### Start your service
```shell script
systemctl start api-<new_service_name>.socket
systemctl start api-<new_service_name> 
```
Сервис сокет активируется и стартует в случае перезагрузки сервера. 
После запуска службы socket приложение будет запущено автоматически при попытке  отправке запроса для сервиса.
Иначе говоря для того чтобы гарантировано остановить сервис нужно остановить и сервис api-<new_service_name>  и сервис сокета api-<new_service_name>.socket
При этом первый раз лучше запускать приложение самостоятельно и проверять логи на наличие ошибок

### Obtain your services' status
```shell script
systemctl status api-<new_service_name>
```
### Stop your service
```shell script
systemctl stop api-<new_service_name>
systemctl stop api-<new_service_name>.socket
```

нужно останавливать две службы, т.к. socket автоматически запустит приложение при полчении запроса

----------------------
Общие сведения по установке и настройки более подробно можно получить например из этих статей
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04-ru 
https://www.8host.com/blog/obsluzhivanie-prilozhenij-flask-s-pomoshhyu-gunicorn-i-nginx-v-ubuntu-16-04/
