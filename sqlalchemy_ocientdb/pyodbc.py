# ocientdb/pyodbc.py
# Copyright (C) 2005-2012 the SQLAlchemy authors and contributors <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Support for Microsoft OcientDb via pyodbc.

pyodbc is available at:

    http://pypi.python.org/pypi/pyodbc/

Connecting
^^^^^^^^^^

Examples of pyodbc connection string URLs:

* ``ocientdb+pyodbc://mydsn`` - connects using the specified DSN named ``mydsn``.

"""


from .base import OcientDbExecutionContext, OcientDbDialect
from sqlalchemy.connectors.pyodbc import PyODBCConnector
from sqlalchemy import types as sqltypes, util
import decimal

class _OcientDbNumeric_pyodbc(sqltypes.Numeric):
    """Turns Decimals with adjusted() < 0 or > 7 into strings.

    The routines here are needed for older pyodbc versions
    as well as current mxODBC versions.

    """

    def bind_processor(self, dialect):

        super_process = super(_OcientDbNumeric_pyodbc, self).\
                        bind_processor(dialect)

        if not dialect._need_decimal_fix:
            return super_process

        def process(value):
            if self.asdecimal and \
                    isinstance(value, decimal.Decimal):

                adjusted = value.adjusted()
                if adjusted < 0:
                    return self._small_dec_to_string(value)
                elif adjusted > 7:
                    return self._large_dec_to_string(value)

            if super_process:
                return super_process(value)
            else:
                return value
        return process

    # these routines needed for older versions of pyodbc.
    # as of 2.1.8 this logic is integrated.

    def _small_dec_to_string(self, value):
        return "%s0.%s%s" % (
                    (value < 0 and '-' or ''),
                    '0' * (abs(value.adjusted()) - 1),
                    "".join([str(nint) for nint in value.as_tuple()[1]]))

    def _large_dec_to_string(self, value):
        _int = value.as_tuple()[1]
        if 'E' in str(value):
            result = "%s%s%s" % (
                    (value < 0 and '-' or ''),
                    "".join([str(s) for s in _int]),
                    "0" * (value.adjusted() - (len(_int)-1)))
        else:
            if (len(_int) - 1) > value.adjusted():
                result = "%s%s.%s" % (
                (value < 0 and '-' or ''),
                "".join(
                    [str(s) for s in _int][0:value.adjusted() + 1]),
                "".join(
                    [str(s) for s in _int][value.adjusted() + 1:]))
            else:
                result = "%s%s" % (
                (value < 0 and '-' or ''),
                "".join(
                    [str(s) for s in _int][0:value.adjusted() + 1]))
        return result


class OcientDbExecutionContext_pyodbc(OcientDbExecutionContext):
    pass


class OcientDbDialect_pyodbc(PyODBCConnector, OcientDbDialect):

    execution_ctx_cls = OcientDbExecutionContext_pyodbc

    pyodbc_driver_name = 'OcientDB'
    supports_unicode_statements = False
    supports_unicode_binds = False

    colspecs = util.update_copy(
        OcientDbDialect.colspecs,
        {
            sqltypes.Numeric:_OcientDbNumeric_pyodbc
        }
    )

    def connect(self, *cargs, **cparams):
        # Get connection
        conn = super(OcientDbDialect_pyodbc, self).connect(*cargs, **cparams)

        # Set up encodings
        conn.setdecoding(self.dbapi.SQL_CHAR, encoding='utf-8')
        conn.setdecoding(self.dbapi.SQL_WCHAR, encoding='utf-8')
        #conn.setdecoding(self.dbapi.SQL_WMETADATA, encoding='utf-8')
        conn.setencoding(str, encoding='utf-8')
        conn.setencoding(unicode, encoding='utf-8')

        # Return connection
        return conn

