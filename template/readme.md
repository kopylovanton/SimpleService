### Запуск и остановку рекомендуется производить с помощью сервиса 
Файлы .service и .socket необходимы для настройки запуска и 
рутинга трафика с Nginx на новый сервис. Для каждого нового 
сервиса требуется создать новые копии файла изменив наименование 
файла и содержимое на действительное имя сервиса 
(изменить template на новое действительное имя сервиса). Это имя должно 
быть одинаково с настройками конфигурации сервиса и
каталогом размещения.

Общие сведения более подробно можно получить например из этих статей
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04-ru 
https://www.8host.com/blog/obsluzhivanie-prilozhenij-flask-s-pomoshhyu-gunicorn-i-nginx-v-ubuntu-16-04/

### serviced install

- переименовать файл api-<service_name>.socket и api-<service_name>.socket
отредактировать файл. Заменить template на действительное 
уникальное имя сервиса (например authlist)
и отредактировать файлы 

service:
> change path !!!!
>
>WorkingDirectory=/home/flask/api/authlist

socket:
> Change name template -> ??? !!!
ListenStream=/home/flask/api/socket/authlist.sock

- выполнить команды (примеры приведены для сервиса с названием authlist)

> sudo cp api-authlist.service /etc/systemd/system
> 
> sudo cp api-authlist.socket /etc/systemd/system
>
> sudo chmod 755 /etc/systemd/system/api-authlist.service
> 
> sudo chmod 755 /etc/systemd/system/api-authlist.socket
>
> sudo systemctl daemon-reload
> 
> systemctl start api-authlist.socket
>
> systemctl enable api-authlist.socket

### Проверка
> sudo systemctl status api-authlist.socket

> sudo file /home/flask/api/socket/authlist.sock
>
>Output - /home/flask/api/socket/authlist.sock: socket

Если команда systemctl status указывает на ошибку, или если 
в каталоге отсутствует файл gunicorn.sock, это означает, что 
сокет Gunicorn не удалось создать. Проверьте журналы сокета 
Gunicorn с помощью следующей команды:

> sudo journalctl -u api-authlist.socket

Еще раз проверьте файл /etc/systemd/system/api-authlist.socket и 
устраните любые обнаруженные проблемы, прежде чем продолжить

# Тестирование активации сокета
Если вы запустили только api-authlist.socket, 
служба api-authlist.service не будет активна в связи с 
отсутствием подключений к совету. Для проверки можно ввести 
следующую команду:

> sudo systemctl status api-authlist

>Output

>> api-authlist.service - api-authlist daemon
   
>>Loaded: loaded (/etc/systemd/system/api-authlist.service; disabled; vendor preset: enabled)
  
>> Active: inactive (dead)

Чтобы протестировать механизм активации сокета, установим соединение с сокетом через curl с помощью следующей команды:

> sudo curl --unix-socket /home/flask/api/socket/authlist.sock localhost/service1/status

Выводимые данные приложения должны отобразиться в терминале 
в формате JSON. Это показывает, что Gunicorn 
запущен и может обслуживать ваше приложение. 
Вы можете убедиться, что служба Gunicorn работает, 
с помощью следующей команды:

>systemctl status api-authlist


## Добавить для первого сервиса или изменить конфигурацию nginx при добавлении нового 
> sudo cp ./nginx/api-config /etc/nginx/sites-available/

> sudo ln -s /etc/nginx/sites-available/api-config /etc/nginx/sites-enabled

> sudo nano /etc/nginx/sites-available/api-config
 
 изменить для первого сервиса или 
 добавить блок заменив два раза template на имя нового сервиса,
 например authlist
 
    location /authlist {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Host $http_host;
      # we don't want nginx trying to do something clever with
      # redirects, we set the Host: header above already.
      proxy_redirect off;
      proxy_pass http://unix:/home/flask/api/socket/authlist.sock;
    }

Протестируйте конфигурацию Nginx на ошибки синтаксиса:

> sudo nginx -t

Если ошибок не будет найдено, перезапустите Nginx с помощью следующей команды:

> sudo systemctl restart nginx

## Примеры команды управления сервисом

### Start your service
systemctl start api-authlist
systemctl start api-authlist.socket

### Obtain your services' status
systemctl status api-authlist

### Stop your service
systemctl stop api-authlist
systemctl stop api-authlist.socket

