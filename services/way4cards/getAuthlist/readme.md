Сервис получения списка активных ( не списанных) авторизаций для всех карт по номеру счетового договора
===

формат всех полей - string

Входящие поля
---
Поле|Описание   |Обязательность|
---|------------|---
X-Fields|Фильтр полей в ответе. Список полей через запятую |
source_system|IDT вызывающей системы для логирования|+
uid|уникальный id запроса для логирования|+
mainContractNumber|номер счетового договора по которому будут получены авторизации|+

Ответные поля
-------------
Поле|Описание |Обязательность|
---|---|---
rc|код ответа 200 успешно, 500 - ошибка сервера|+
message|сообщение "ok" если успешно или деталищация ошибки|+
source_system|копия входящего поля|+
uid|копия входящего поля|+
input_parms|составное поле содержит поля фильтрации из запроса - mainContractNumber|+
records|составное поле содержит список авторизаций с набором полей, которые описаны ниже. В случае ошибки поле будет содержать пустой список|+

Состав поля records
-------------------
Поле|Описание |Обязательность|
---|---|---
id|way4 unique document number|
transactionDate|local transaction date time - yyyymmddHHMiss|
transTypeId|trans type unique Id|
transType|trans type name|
transactionStatus|transaction processing status|
transactionAmount|transaction amount|
transactionCurrency|transaction currency|
amountInAccCurr|transaction amount in account currency|
acctCurr|account currency|
feeAmount|fee amount|
feeCurrency|fee currency|
requestCategory|request category (request/advice/reverse)|
tokenDeviceType|token acceptance device type Phone/Tablet/Watch|
tokenProvider|token provider|
sourceChannel|source channel|
targetChannel|target channel|
addInfo|some tag=value; add info|
transactionDescription|transaction description|
retrievalRefNumber|retrieval ref number - printed on receipt|
authCode|auth code - printed on receipt|
transCity|transaction city|
transCountry|trans country|
mccCategory|mccCategory|
transCondAttr|tag; format transaction attributes (chip, attended , etc)|
contractFor|card number masked 4***4|


