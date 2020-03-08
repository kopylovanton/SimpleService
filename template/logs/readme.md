В этом катологе создаются логи приложения. Конфигурация по умолчанию сохраняет логи за последние 14 дней
```
<service_name>_main.log - основной лог содержащий время выполнения и сообщения об ошибках
<service_name>_main.log - лог регистрации обращений к сервису
```
логи nginx общие для всех сервисов и храняться тут:

```
/var/log/nginx/access.log
/var/log/nginx/error.log
```

Centos 7 Audit log
```
sudo cat /var/log/audit/audit.log | grep nginx | grep denied
```