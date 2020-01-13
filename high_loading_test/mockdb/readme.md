### Step 0:
Start downloading rpm 19.X the install files from [Oracle](http://www.oracle.com/technetwork/database/enterprise-edition/downloads/index.html)

### Step 1:
Create a blank CentOs 7 instance

Convert to Oracle Linux: ([source](https://linux.oracle.com/switch/centos/))
```
curl -O https://linux.oracle.com/switch/centos2ol.sh 
sh centos2ol.sh
yum upgrade
```

### Step 2:

Install database preinstall package:
```
yum -y install oracle-database-preinstall-19c
```

Copy install files from your machine to the server
```
scp oracle-database-ee-19c-1.0-1.x86_64.rpm root@167.71.60.173:/tmp

```


[Install the database software using the yum localinstall command](https://docs.oracle.com/en/database/oracle/oracle-database/19/ladbi/running-rpm-packages-to-install-oracle-database.html#GUID-BB7C11E3-D385-4A2F-9EAF-75F4F0AACF02)
``` 
yum -y localinstall oracle-database-ee-19c-1.0-1.x86_64.rpm
```

### Step 3

configure/change host name to real IP

```
host
ifconfig 
nano /etc/hosts
```

Creating and Configuring an Oracle Database

To create a sample database with the default settings, perform the following steps:

Log in as root.

To configure a sample Oracle Database instance, run the following service configuration script:
```
/etc/init.d/oracledb_ORCLCDB-19c configure
```
Note:You can modify the configuration parameters by editing the /etc/sysconfig/oracledb_ORCLCDB-19c.conf file.
This script creates a container database (ORCLCDB) with one pluggable database (ORCLPDB1) and configures the listener at the default port (1521).

Review the status information that is displayed on your screen.


### Step 4

[Configuring an Oracle Database for RPM Based](http://oracle-help.com/oracle-19c/creating-and-configuring-an-oracle-database-for-rpm-based/)

```
[oracle@oracle19c sw]# ps -ef|grep pmon
oracle   29358     1  0 03:47 ?        00:00:00 ora_pmon_ORCLCDB
root     30579 17822  0 03:59 pts/0    00:00:00 grep --color=auto pmon

[oracle@oracle19c sw]$ . oraenv
ORACLE_SID = [oracle] ? ORCLCDB
The Oracle base has been set to /opt/oracle
[oracle@oracle19c sw]$ sqlplus / as sysdba
```

```
alter session set "_ORACLE_SCRIPT"=true
/
CREATE USER bwx IDENTIFIED BY oracle
/
GRANT CREATE SESSION TO bwx 
/
GRANT CREATE TABLE TO bwx
/
GRANT CREATE PROCEDURE TO bwx
/
GRANT CREATE TRIGGER TO bwx
/
GRANT CREATE VIEW TO bwx
/
GRANT CREATE SEQUENCE TO bwx
/
GRANT ALTER ANY TABLE TO bwx
/
GRANT ALTER ANY PROCEDURE TO bwx
/
GRANT ALTER ANY TRIGGER TO bwx
/
GRANT ALTER PROFILE TO bwx
/
GRANT DELETE ANY TABLE TO bwx  
/
GRANT DROP ANY TABLE TO bwx
/
GRANT DROP ANY PROCEDURE TO bwx
/
GRANT DROP ANY TRIGGER TO bwx
/
GRANT DROP ANY VIEW TO bwx
/
GRANT DROP PROFILE TO bwx
/
GRANT execute on DBMS_LOCK TO bwx
/
```

### step5

create function for bwx


```
create or replace FUNCTION SLEEP 
(from_time in number,to_time number ) 

RETURN VARCHAR2 AS 

k  number;

BEGIN
  
    k := DBMS_RANDOM.VALUE(from_TIME, to_time);
    DBMS_LOCK.sleep(k);

    RETURN to_char(round(k,2));
END SLEEP;

```



