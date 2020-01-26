Настройки системных сервисов
============================

В этом каталоге находяться шаблоны настроек системных сервисов, которые копируют и активируются при первичной настройке сервиса скриптом ```./setup.sh```
Ниже описаны назначения скриптов и системные катологи в которых будут размещены финальные конфигурационные файлы

Наменование файла   |Назначение конфигурационного файла  |Системный путь конфигурационного файла
--------------------|------------------------------------|--------------------------------------
api-template.socket | Конфигурация сервиса сокета        | systemd/api-$serviceName.socket 
api-template.service| Конфигурация сервиса приложения    | systemd/api-$serviceName.service 
logrotate.conf      | Конфигурация сервиса ротации логов | /etc/logrotate.d/$serviceName

по умолчанию ротация логов настроена на 14 дней 
конфигурацию ротации логов nginx добавляется при установке nginx

Cтатьи по конфигурированию системных сервисов
---------------------------------------------
[systemd](https://ru.wikipedia.org/wiki/Systemd)

[logrotate](https://wiki.archlinux.org/index.php/Logrotate)

[howto systemd](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04-ru#%D1%88%D0%B0%D0%B3-4-%E2%80%94-%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0-gunicorn)

[howto logrotate](https://www.digitalocean.com/community/tutorials/how-to-manage-logfiles-with-logrotate-on-ubuntu-16-04)
