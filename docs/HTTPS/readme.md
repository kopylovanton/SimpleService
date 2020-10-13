Защита трафика с помощью SSL соединения
========================================

Для этого необходимо настроить HTTPS подключения для nginx 

Есть множество пошаговых инструкций по настройке HTTPS подключений Nging. Например, [это](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-18-04#step-2-%E2%80%93-configuring-nginx-to-use-ssl) или [это](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04-ru#%D1%88%D0%B0%D0%B3-6-%E2%80%94-%D0%B7%D0%B0%D1%89%D0%B8%D1%82%D0%B0-%D0%BF%D1%80%D0%B8%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%B8%D1%8F)

Настройки лучше делать предварительно настроив НЕ шифрованное соединение и работу сервиса. Затем уже настроить шифрованное и отключить НЕ шифрованное.

Кратко список команд (для варианта создания самоподписанного сертификата из первой ссылки)

```shell script
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
sudo openssl dhparam -out /etc/nginx/dhparam.pem 4096
```

```shell script
sudo nano /etc/nginx/snippets/self-signed.conf
```

```buildoutcfg
# /etc/nginx/snippets/self-signed.conf 
# -------------------------------------
ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
```
 
```shell script
sudo nano /etc/nginx/snippets/ssl-params.conf
```
 
```buildoutcfg
#/etc/nginx/snippets/ssl-params.conf
ssl_protocols TLSv1.2;
ssl_prefer_server_ciphers on;
ssl_dhparam /etc/nginx/dhparam.pem;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
ssl_ecdh_curve secp384r1; # Requires nginx >= 1.1.0
ssl_session_timeout  10m;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off; # Requires nginx >= 1.5.9
ssl_stapling on; # Requires nginx >= 1.3.7
ssl_stapling_verify on; # Requires nginx => 1.3.7

# Disable strict transport security for now. You can uncomment the following
# line if you understand the implications.
# add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";

```

```
sudo nano /etc/nginx/sites-available/api-config
```
нужно добавить секцию ssl и закомментировать http

```buildoutcfg
#/etc/nginx/sites-available/api-config
    listen 443 ssl;
    listen [::]:443 ssl;
    include snippets/self-signed.conf;
    include snippets/ssl-params.conf;

    listen 80;
```

тест конфигурации nginx
```shell script
sudo nginx -t
nginx: [warn] "ssl_stapling" ignored, issuer certificate not found for certificate "/etc/ssl/certs/nginx-selfsigned.crt"
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

```shell script
sudo systemctl restart nginx
```
проверить отображение https://<host>/<service_name>/<version>/swagger

При переходе через браузер на https страницу браузер выдаст предупреждение, что подключение не безопасно так как сертификат сервера не находится в списке известных браузеру доверенных сертификатов
Поэтому в списке команд нет запрета http на файрволе так как это описано в базовой статье.
При данной конфигурации важно направлять запросы на 443 порт для шифрования трафика. При этом запросы по 80 HTTP порту также будут проходить.
При необходимости можно закомментировать 80 порт в конфигурации nginx и запретить его на файрволе командой 

```shell script
sudo ufw delete allow 'Nginx HTTP'
```
