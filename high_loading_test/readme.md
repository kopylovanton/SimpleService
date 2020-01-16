Нагрузочное тестирование
========================

Приведены результаты нагрузочного тестирования базовой конфигурации

Сервер
-------


- Апликационный сервер 2ядра 2Gb оперативной памяти. Операционная система Ubuntu 18:

[server]: https://i.ibb.co/TrprGCj/App-Server-Conf.png

![image][server] 

Методика нагрузочного тестирования
----------------------------------

В мок базе Oracle 19 была создана процедура (код процедуры есть [тут](https://github.com/kopylovanton/SimpleService/blob/master/high_loading_test/mockdb/sleep.sql)) , которая эмитирует случайное время исполнение запроса в заданном временном интервале. Для тестирования использовалась задержка от 0.1 до 0.5 секунды. Общее время вызова при этом составило 0.15 до 0.65 секунды. 

Базовая конфигурация сервиса запускает 5ть потоков/воркеров на выполнение, что на данном стенде обеспечивало нормальную (время ответа сервиса в пределах одной секунды) обработку одновременно 20 потоков с примерной скоростью обработки 15 запросов в секунду.

На стенде было сконфигурировано три сервиса

Нагрузочное тестирование производилось из SoapUI c различными профилями нагрузки:
- 20 потоков на один сервис с длительностью 10 минут
- 60 потоков на один сервис с длительностью 10 минут
- 60 потоков на три сервиса с длительностью 10 минут
- 60 потоков на один сервис с увеличенным количеством воркеров с 5 до 15 с длительностью 10 минут


Резульаты для коротких запусков
-------------------------------
во время запусков ошибок выполнения запросов не происходило


- 20 потоков на один сервис с длительностью 5 минут

[r20x1]: https://i.ibb.co/tHWG4yq/20-Threads-5workers-soap-ui.png

![image][r20x1]

- 60 потоков пиковой нагрузки на один сервис с длительностью 5 минут

Целью теста было проверить способность приложения выходить на штатный режим работы после пиковых перегрузок. Проблем не наблюдалось - тест был выполнен успешно. 

[r60x1]: https://i.ibb.co/XDCVrLS/Burst-60-threads-5-workers-soap-ui.png

![image][r60x1] 

- 60 потоков на три сервиса с длительностью 5 минут

[r60x3]: https://i.ibb.co/4JZD1VZ/60-threads-3x5workers-soap-ui.png

![image][r60x3]

- 60 потоков на один сервис с увеличенным количеством воркеров с 5 до 15

[r60x115]: https://i.ibb.co/wLn3Lrk/60-threads-15workers-soap-ui.png

![image][r60x115]


статистика утилизации сервера за время тестов

[stat]: https://i.ibb.co/tzTh35V/App-Server-Statistics.png

![image][stat] 

Результаты тестирования при обрыве связи
----------------------------------------

Тест проводился 10 минут из которых 4 ре минуты настройками файрвола блокировался доступ апликациаонного сервера к серверу базы данных. Далее настройки доступа востанавливались. Целью теста было проверить способность приложения востанавливаться после сетевых проблем. После востановления сетевого подключения приложение продолжило работать в штатном режиме.


[fail]: https://i.ibb.co/sJ2pGKc/firewall-error-graph.png

![image][fail] 






















