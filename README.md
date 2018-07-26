# sqlalchemy-ocientdb
SQLAlchemy connector/dialect for the Ocient Database.


## Installation
You can simply use
`pip install sqlalchemy-turbodbc`
to install the dialect.


## Usage
To create a connection using this dialect, simply use the `ocientdb+pyodbc` protocol.

For example:

```python
engine = create_engine('ocientdb+pyodbc://looker:looker@OcientLkr')
```
