# sqlalchemy-ocientdb
SQLAlchemy connector/dialect for the Ocient Database.


## Installation
You can simply use
`pip install sqlalchemy-turbodbc`
to install the dialect.

`cd qlalchemy-ocientdb`
`python setup.py sdist`
`mkdir install`
`cd install`
`sudo rm -Rf sqlal*`
`cp ../sqlalchemy-ocientdb/dist/sqlalchemy_ocientdb-1.0.dev0.tar.gz .`
`tar -xvf sqlalchemy_ocientdb-1.0.dev0.tar.gz`
`cd sqlalchemy_ocientdb-1.0.dev0/`
`sudo python setup.py install --force`

## Usage
To create a connection using this dialect, simply use the `ocientdb+pyodbc` protocol.

For example:

```python
engine = create_engine('ocientdb+pyodbc://looker:looker@OcientLkr')
```
