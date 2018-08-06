# sqlalchemy-ocientdb
SQLAlchemy connector/dialect for the Ocient Database.


## Installation
```
cd sqlalchemy-ocientdb  
python setup.py sdist  
mkdir install  
cd install  
sudo rm -Rf sqlal*  
cp ../sqlalchemy-ocientdb/dist/sqlalchemy_ocientdb-1.0.dev0.tar.gz .  
tar -xvf sqlalchemy_ocientdb-1.0.dev0.tar.gz  
cd sqlalchemy_ocientdb-1.0.dev0/  
sudo python setup.py install --force  
```

## Usage
To create a connection using this dialect, simply use the `ocientdb+pyodbc` protocol.

For example:

```python
engine = create_engine('ocientdb+pyodbc://looker:looker@OcientLkr')
```

## Sample ODBC Connection Parameters
```
File odbcinst.ini:  (directory where this file resides pointed to by env. variable 'ODBCSYSINI=')

[OcientDB]
Driver = /home/user/sqlalchemy/ocient_odbc.so
FileUsage = 1
[ODBC]
Trace = yes
TraceFile = /home/user/sqlalchemy/odbctrace.out

File .odbc.ini:    (located in user's home directory)

[OcientDB]
Description  = Ocient Test
Driver       = OcientDB
Host         = 10.10.5.23
Port         = 4050
Database     = Test
UserName     = jason
Password     = pwd
[OcientLkr]
Description  = Ocient Looker
Driver       = OcientDB
Host         = 10.10.3.23
Port         = 4050
Database     = looker_db
UserName     = looker
Password     = looker
```

## Required environment variable settings
```
export ODBCSYSINI=/home/user/
export LD_LIBRARY_PATH=/home/user/sqlalchemy/lib/
export PYTHONPATH=/home/user/sqlalchemy/
``` 
