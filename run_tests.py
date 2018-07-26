from sqlalchemy.dialects import registry

registry.register("ocientdb", "sqlalchemy_ocientdb.pyodbc", "OcientDbDialect_pyodbc")
registry.register("ocientdb.pyodbc", "sqlalchemy_ocientdb.pyodbc", "OcientDbDialect_pyodbc")

from sqlalchemy.testing import runner

runner.main()
