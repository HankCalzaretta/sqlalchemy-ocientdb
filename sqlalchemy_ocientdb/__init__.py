__version__ = '1.0'

from sqlalchemy.dialects import registry
from .base import BOOLEAN, INT8, UINT8, INT16, UINT16,\
   INT32, UINT32, INT64, UINT64, FLOAT32,\
   FLOAT64, BLOB, IPV4, UUID, NUMERICXY

__all__ = (
   BOOLEAN, INT8, UINT8, INT16, UINT16,
   INT32, UINT32, INT64, UINT64, FLOAT32,
   FLOAT64, BLOB, IPV4, UUID, NUMERICXY
)

registry.register("ocientdb", "sqlalchemy_ocientdb.pyodbc", "OcientDbDialect_pyodbc")
registry.register("ocientdb.pyodbc", "sqlalchemy_ocientdb.pyodbc", "OcientDbDialect_pyodbc")
