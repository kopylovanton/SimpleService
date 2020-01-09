# Предвариетльная настройка сервера 
Требуется создать пользователя, установить Nginx, установить python 3 и необходимые пакеты.

### Последовательность самостоятельной установки. 
Примеры команд приведены для Ubuntu из https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04

Анологичный пример для Centos https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-centos-7

1. Создать пользователя flask
> adduser flask
> usermod -aG sudo flask

2. Уствновить Nginx https://nginx.org/ru/linux_packages.html 
> sudo apt update
> sudo apt install nginx
> sudo systemctl enable nginx

3. Настройка файрвола для HTTP
> sudo ufw app list
> sudo ufw allow 'Nginx HTTP'


4. Проверить, что Nginx запущен
> systemctl status nginx

2. Установить python 3.6(7).*
> sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
> sudo apt install python3-venv
> sudo apt install python-pip

3. Настроить окружение python для сервисов 
> mkdir ~/api
> cd ~/api
> python3.6 -m venv python-api-env
2. Установить пакеты python перечисленные в requirements.txt 
> source python-api-env/bin/activate
> (python-api-env) $ sudo -H pip install wheel
> (python-api-env) $ sudo -H pip install -r requirements.txt

# Администрирование
1. Управление Nginx
* Запуск
>sudo systemctl stop nginx
* Остановка
>sudo systemctl start nginx
* Перечитать конфигурацию
>sudo systemctl reload nginx


### Последовательность установки с использованием Docker

