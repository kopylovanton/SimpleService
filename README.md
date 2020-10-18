
Simple service V2
=============

Проект для создания REST сервисов интеграции с легаси (например процессинговой) системой. 
Основные возможности:
- Конфигурация GET (SQL) и/или POST (PLSQL) полей запросов и ответов
- Атодокументирование в формате swagger (openapi 3) 
- Автоматическое переподключение к базе данных 
- Автоматический старт и рестарт приложения
- Дополнительный REST статус запрос для получения информации о работе сервиса и встраивания в системы мониторинга
- Ротация и архивирование логов с заданной глубиной


Compatibility
=============

Проект построен на компонентах: 
- [Nginx](https://nginx.org/ru/) 
- [aiohttp](https://docs.aiohttp.org/en/stable/index.html)
- [loguru](https://loguru.readthedocs.io/en/stable/) 
- [Cx-Oracle](https://oracle.github.io/python-cx_Oracle/) 
- [sytemd](https://ru.wikipedia.org/wiki/Systemd)

Installation
============

Предварительная настройка (установка python3.6+, nginx, установка драйвера Oracle и создание пользователя) сервера описана в каталоге /docs/readme_<os_type>.md
Навстройка нового сервиса на основе шаблона описана /docs/readme.md
Для установки сервиса нужно скопировать на сервер файл `simpleservice_linux.tar.gz`

Technical Requirements
============

Рекомендуемы аппаратные требования 2Gb/2Cpu/64Gb  (достаточно для запуска нескольких сервисов)

Программные требования:
- Операционная система Ubuntu 18 или CentOS 7
- Nginx
- python 3.6+ 
- Oracle Instant Client
- systemd

Нагрузка на сервер (1CPU/2GB) при обработке (~100 запросов в секунду при длительности одного запросо 200-300мс):

[htop]: https://i.ibb.co/7kJKTQF/htop.png
![image][htop] 

Детали по нагрузке:

[wrk]: https://i.ibb.co/0KVf3ZV/wrk.png
![image1][wrk] 




Resources
=============

- /docs : инструкции  предварительной настройки сервера
- /src : код программы и скрипты утановки
- /dist : подготовленный архив для установки на сервере со всеми необходимыми python зависимостями


URLs
====
```
- <host>:<port>/<service name>/<VERSION> - адрес вызова сервиса

- <host>:<port>/<service name>/<VERSION>/status - проверка состояния сервиса (рандомного воркера)

- <host>:<port>/<service name>/swagger - html страница с документацией и возможностью пробного вызова сервиса 
```
