###  /config/config_get.yaml

**если вы устанавливаете заранее подготовленную конфигурацию просто замените этот файле**

Параметр|Назначенение
--------|------------
URL| базовый адрес для сервиса `<host>:<port>/<url>` . Замените на уникальное значение
LOG_LEVEL| 10-Debug, 20-Info production level
SQL_GET| запрос для GET метода сервиса. Начинается с управляющего символа `>` который указывает в yaml натации на многострочный параметр. Не удаляйте этот символ для избежании ошибок парсера. Имена возвращаемых полей и входящих параметров должно быть согласовано с секцией `SPECIFICATIONS`. Не забудьте предоставить права на вызываемые объекты Oracle для пользователя flask
MAX_FETCH_ROWS| максимальное количество строк, которое будет обработано. Защищает от не правильных SQL
SPECIFICATIONS| описание входящих и исходящих полей в yaml синтексисе. Сохраняйте отсутпы так как это указано в примере для избежания ошибок парсера

###  /config/configdb.yaml

параметры подключения к базе данных. Необходимо указать актуальные параметры

Параметр|Назначенение
--------|------------
DB_CONN_STRING|строка подключения
DB_ENCODING|кодировка базы данных
DB_USER_NAME| имя пользователя
DB_USER_PASSWORD| пароль, после первого запуска пароль автоматически шифруется и перезаписывается в файл в шифрованном виде
CURRENT_SCHEMA|имя пользователя владельца схемы по умолчанию 
DB_EXECUTE_TIMEOUT| таймаут выполнения запроса в милисекундах

### Редактирование /config/gunicorn.yaml

параметры аппликационного сервера описаны в [документации gunicorn](http://docs.gunicorn.org/en/latest/configure.html#framework-settings).
Можно не редактировать параметры. Колчиство воркеров по умолчанию 5 (`workers = 5`) - рекомендованная конфигурация для двух ядер, которая может обрабатывать 20 одновременных запросов для SQL который выполняется 0,3-0,5 секунд (с производительностью 15TPS)
Нагрузочные тесты показали, что увеличение воркеров до 10 в два раза ускоряло производительность на той же (2ядра 2Гб) конфигурации сервера
Нагрузка процессора при этом была не большой - не более 10 процентов. 