
Simple service
=============

Проект для создания REST сервисов интеграции с процессинговой системой. 
Основные возможности:
- Конфигурация SQL запроса, полей запросов и ответов
- Атодокументирование swagger 
- Количество потоков/воркеров задается в конфигурации
- Автоматическое переподключение к базе данных
- Автоматический старт и рестарт приложения
- Дополнительный REST запрос для получения информации о работе сервиса и встраивания в системы мониторинга


Compatibility
=============

Проект построен на open sourse стеке: 
- Nginx для проксирования запросов
- Gunicorn в качестве апликационного сервиса
- Flask и Flask-Restplus для описания формата запроса
- Cx-Oracle для подключения к базе данных


Technical Requirements
============

Аппаратные: 
- процессорныя ядра из расчета 1 ядро на два потока (базовая конфигурация 2ядра).
- оперативная память 2Gb

Программные:
- Операционная система Ubuntu 18 (CentOS 7)
- Nginx
- python 3.6 (текущая стабильная версия из репозитория) 
- пакеты python перечислены в /install/requirements.txt
- Oracle Instant Client
- systemd

Installation
============

Предварительная настройка сервера описана в каталоге /install/readme.md
Процедура настройки нового сервиса описана в /template/readme.md


Resources
=============

- /install : инструкции по предварительной настройки сервера
- /template : интструкции по конфигурации нового сервиса
- /service : готовые конфигурации для сервисов могут быть использованы при настройки нового сервиса


URLs
====
<host>:<port>/<service name> - адрес вызова сервиса
<host>:<port>/<service name>/status - проверка состояния сервиса (рандомного воркера)
<host>:<port>/<service name>/swagger - html страница с документацией и возможностью пробного вызова сервиса 
<host>:<port>/<service name>/swagger.json - машиночитаемая документация сервиса
