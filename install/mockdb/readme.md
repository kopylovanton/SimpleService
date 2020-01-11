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

# /etc/init.d/oracledb_ORCLCDB-19c configure
Note:You can modify the configuration parameters by editing the /etc/sysconfig/oracledb_ORCLCDB-19c.conf file.
This script creates a container database (ORCLCDB) with one pluggable database (ORCLPDB1) and configures the listener at the default port (1521).

Review the status information that is displayed on your screen.
