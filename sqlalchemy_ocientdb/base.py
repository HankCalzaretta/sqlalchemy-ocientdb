# ocient/base.py
# Copyright (C) 2007-2012 the SQLAlchemy authors and contributors <see AUTHORS file>
# Copyright (C) 2007 Paul Johnston, paj@pajhome.org.uk
# Portions derived from jet2sql.py by Matt Keranen, mksql@yahoo.com
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Support for the Ocient database.


"""
import re
from sqlalchemy import types as sqltypes
from sqlalchemy import sql, schema, types, exc, pool
from sqlalchemy.sql import compiler, expression, elements
from sqlalchemy.engine import default, base, reflection
from sqlalchemy import processors
from sqlalchemy.types import CHAR, VARCHAR, \
    DATE, TIMESTAMP, Integer, Float
from sqlalchemy.ext.compiler import compiles

class OcientDbExecutionContext(default.DefaultExecutionContext):
    pass

class OcientDbCompiler(compiler.SQLCompiler):
    extract_map = compiler.SQLCompiler.extract_map.copy()
    extract_map.update({
            'month': 'm',
            'day': 'd',
            'year': 'yyyy',
            'second': 's',
            'hour': 'h',
            'doy': 'y',
            'minute': 'n',
            'quarter': 'q',
            'dow': 'w',
            'week': 'ww'
    })


    def visit_label(self, label,
                     add_to_result_map=None,
                     within_label_clause=False,
                     within_columns_clause=False,
                     render_label_as_label=None,
                     **kw):
        if str(label.name) in "count":
		label.name = str(label.name).replace("count","CNT")
        if "(" in str(label.name):
                label.name = str(label.name).replace("(","_")
                label.name = str(label.name).replace(")","")
#		labelname = str(label._label).replace("count","CNT")
#		return self.preparer.format_label(label, name=labelname)
#        else:
	return super(OcientDbCompiler, self).visit_label( \
	        label,                         \
               	add_to_result_map=add_to_result_map, \
               	within_label_clause=within_label_clause, \
               	within_columns_clause=within_columns_clause, \
               	render_label_as_label=render_label_as_label, **kw)

    def visit_bindparam(self, bindparam, within_columns_clause=False,
                        literal_binds=False,
                        skip_bind_expression=False,
                        **kwargs):
	
	return super(OcientDbCompiler, self).visit_bindparam( \
		 bindparam, within_columns_clause=within_columns_clause,    \
                 literal_binds=literal_binds,
                 skip_bind_expression=skip_bind_expression,
                 **kwargs)

    def visit_binary(self, binary, override_operator=None,
                     eager_grouping=False, **kw):

        return super(OcientDbCompiler, self).visit_binary( \
                 binary, override_operator=override_operator,    \
                 eager_grouping=eager_grouping,                 \
                 **kw)

    def visit_select(self, select, asfrom=False, parens=True,
                  fromhints=None,
                  compound_index=0,
                  nested_join_translation=False,
                  select_wraps_for=None,
                  lateral=False,
                  **kwargs): 
	if self.bind is not None:
	    connection = self.bind
	    dialect = self.bind.dialect
            if len(select._from_obj): 
	        if isinstance(select._from_obj[0], expression.TableClause):
	            table_name = select._from_obj[0].name
	            schema = select._from_obj[0].schema
	            columns = OcientDbDialect.get_columns(dialect, connection, table_name, schema=schema)
	            for col in columns:
	                if str(col.get("type")).startswith("TIMESTAMP"):
	                    for c in select._whereclause:
		                if str(c.left)  == col.get("name"):
		                    if (str(c.right).startswith("'") and str(c.right).endswith("'")) or \
		                       (str(c.right).startswith('"') and str(c.right).endswith('"')):
		      	                c.right.text = "TIMESTAMP(" + c.right.text + ")" 
	
        return super(OcientDbCompiler, self).visit_select( \
		  select, asfrom=asfrom, parens=parens,    \
                  fromhints=fromhints,                     \
                  compound_index=compound_index,           \
                  nested_join_translation=nested_join_translation, \
                  select_wraps_for=select_wraps_for,       \
                  lateral=lateral,                         \
                  **kwargs) 

    def for_update_clause(self, select):
        """FOR UPDATE is not supported by OcientDb; silently ignore"""
        return ''

    def visit_column(self, column, add_to_result_map=None,
                     include_table=True, **kwargs):
        name = orig_name = column.name
        if name is None:
            name = self._fallback_column_name(column)

        is_literal = column.is_literal
        if not is_literal and isinstance(name, elements._truncated_label):
            name = self._truncated_identifier("colident", name)

        if add_to_result_map is not None:
            add_to_result_map(
                name,
                orig_name,
                (column, name, column.key),
                column.type
            )

        if is_literal:
            name = self.escape_literal_column(name)
        else:
            name = self.preparer.quote(name)
        table = column.table
        if table is None or not include_table or not table.named_with_column:
            return name
        else:
            effective_schema = self.preparer.schema_for_object(table)
            schema_prefix = ''
            tablename = table.name
            if isinstance(tablename, elements._truncated_label):
                tablename = self._truncated_identifier("alias", tablename)

            return schema_prefix + \
                self.preparer.quote(tablename) + \
                "." + name

    def order_by_clause(self, select, **kw):
        order_by = select._order_by_clause
        if len(str(order_by)) > 0:
            order_by_str = str(order_by)
            order_by_str = order_by_str.replace(".","_")
            order_by_str = order_by_str.replace('COUNT(*)','"CNT"')
            if "(" in order_by_str:
                order_by_str = order_by_str.replace("(","_")
                order_by_str = order_by_str.replace(")","")
                if "ASC" in order_by_str or "DESC" in order_by_str:
                    order_by_str = '"' + order_by_str.replace(" ",'" ')
		else: 
                    order_by_str = '"' + order_by_str + '"'
            return " ORDER BY " + order_by_str
#            return " ORDER BY " + str(order_by).replace('.','_')
        else:
            return ""

    def visit_join(self, join, asfrom=False, **kwargs):
        return ('(' + self.process(join.left, asfrom=True) + \
                (join.isouter and " LEFT OUTER JOIN " or " INNER JOIN ") + \
                self.process(join.right, asfrom=True) + " ON " + \
                self.process(join.onclause) + ')')

    def visit_extract(self, extract, **kw):
        field = self.extract_map.get(extract.field, extract.field)
        return 'DATEPART("%s", %s)' % \
                    (field, self.process(extract.expr, **kw))

class BOOLEAN(sqltypes.TypeEngine):
    __visit_name__ = 'BOOLEAN'

class INT8(Integer):
    __visit_name__ = 'INT8'

class UINT8(Integer):
    __visit_name__ = 'UINT8'

class INT16(Integer):
    __visit_name__ = 'INT16'

class UINT16(Integer):
    __visit_name__ = 'UINT16'

class INT32(Integer):
    __visit_name__ = 'INT32'

class UINT32(Integer):
    __visit_name__ = 'UINT32'

class INT64(Integer):
    __visit_name__ = 'INT64'

class UINT64(Integer):
    __visit_name__ = 'UINT64'

class FLOAT32(sqltypes.TypeEngine):
    __visit_name__ = 'FLOAT32'

class FLOAT64(sqltypes.TypeEngine):
    __visit_name__ = 'FLOAT64'

class BLOB(sqltypes.TypeEngine):
    __visit_name__ = 'BLOB'

class TIMESTAMP(sqltypes.TypeEngine):
    __visit_name__ = 'TIMESTAMP'

class IPV4(sqltypes.TypeEngine):
    __visit_name__ = 'IPV4'

class UUID(sqltypes.TypeEngine):
    __visit_name__ = 'UUID'

class NUMERICXY(sqltypes.TypeEngine):
    __visit_name__ = 'NUMERICXY'

class OcientDbTypeCompiler(compiler.GenericTypeCompiler):
    def visit_BOOLEAN(self, type_, **kw):
        return "BOOLEAN"

    def visit_INT8(self, type_, **kw):
        return "INT8"

    def visit_UINT8(self, type_, **kw):
        return "UINT8"

    def visit_INT16(self, type_, **kw):
        return "INT16"

    def visit_UINT16(self, type_, **kw):
        return "UINT16"

    def visit_INT32(self, type_, **kw):
        return "INT32"

    def visit_UINT32(self, type_, **kw):
        return "UINT32"

    def visit_INT64(self, type_, **kw):
        return "INT64"

    def visit_UINT64(self, type_, **kw):
        return "UINT64"

    def visit_FLOAT32(self, type_, **kw):
        return "FLOAT32"

    def visit_FLOAT64(self, type_, **kw):
        return "FLOAT64"

    def visit_BLOB(self, type_, **kw):
        return "BLOB"

    def visit_IPV4(self, type_, **kw):
        return "IPV4"

    def visit_UUID(self, type_, **kw):
        return "UUID"

    def visit_NUMERICXY(self, type_, **kw):
        return "NUMERICXY"


ischema_names = {
    'BOOLEAN': BOOLEAN,
    'INT8': Integer,
    'UINT8': Integer,
    'INT16': Integer,
    'UINT16': Integer,
    'INT32': Integer,
    'UINT32': Integer,
    'INT64': Integer,
    'UINT64': Integer,
    'FLOAT32': Float,
    'FLOAT64': Float,
    'CHAR': CHAR,
    'VARCHAR': VARCHAR,
    'BLOB': BLOB,
    'DATE': DATE,
    'TIMESTAMP': TIMESTAMP,
    'IPV4': IPV4,
    'UUID': UUID,
    'NUMERICXY': NUMERICXY
}


class OcientDbIdentifierPreparer(compiler.IdentifierPreparer):
    reserved_words = compiler.RESERVED_WORDS.copy()
    reserved_words.update(['value', 'text'])
    def __init__(self, dialect):
        super(OcientDbIdentifierPreparer, self).\
                __init__(dialect, initial_quote='"', final_quote='"')



class OcientDbDialect(default.DefaultDialect):
    name = 'ocient'
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    supports_unicode_statements = False 
    supports_unicode_binds = False
    supports_simple_order_by_label = True

    poolclass = pool.SingletonThreadPool
    type_compiler = OcientDbTypeCompiler
    statement_compiler = OcientDbCompiler
#   ddl_compiler = OcientDbDDLCompiler
    preparer = OcientDbIdentifierPreparer
    execution_ctx_cls = OcientDbExecutionContext

    ischema_names = ischema_names

    @classmethod
    def dbapi(cls):
        import pyodbc as module
        return module

    def create_connect_args(self, url):
        opts = url.translate_connect_args()
        connectors = ["Driver={OcientDB}"]
        connectors.append("Dbq=%s" % opts["database"])
        user = opts.get("username", None)
        if user:
            connectors.append("UID=%s" % user)
            connectors.append("PWD=%s" % opts.get("password", ""))
        return [[";".join(connectors)], {}]

    @reflection.cache
    def get_table_names(self, connection, schema=None, **kw):
	conn = connection.engine.raw_connection()
	try:
		cursor = conn.cursor()
		table_names=[]
		for rows in cursor.tables(catalog='%', schema='%', table='%', tableType='%'):
        		rows = [str(r) for r in rows]
        		table_names.append(rows[2])
		cursor.close()
	finally:
		conn.close()
        return table_names

    @reflection.cache
    def get_columns(self, connection, table_name, schema=None, **kw):
	conn = connection.engine.raw_connection()
	try:
		cursor = conn.cursor()
		columns = []
		for rows in cursor.columns(catalog='%', schema=schema, table=table_name, column='%'):
        		col_info = self._get_column_info(
                		rows.column_name,
                		rows.type_name,
                		rows.nullable,
                		rows.remarks,
                		rows.char_octet_length)
        		columns.append(col_info)
		cursor.close()
	finally:
		conn.close()
        return columns

    def _get_column_info(self, name, type_, nullable, remarks, length):

        coltype = self.ischema_names.get(type_, None)

        kwargs = {}
	
	if coltype in (CHAR, VARCHAR):
            args = (length,)
        else: 
	     args = ()

        if coltype:
            coltype = coltype(*args, **kwargs)
        else:
            util.warn("Did not recognize type '%s' of column '%s'" %
                      (type_, name))
            coltype = sqltypes.NULLTYPE

        column_info = dict(name=name, type=coltype, nullable=nullable,
                           remarks=remarks)
        return column_info

    @reflection.cache
    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
	conn = connection.engine.raw_connection()
	try:
		cursor = conn.cursor()
		constrained_columns = []
		for cat, sch, tab, unique, idxq, idxname, type, ord, col, asc, card, pgs, filt in \
     			cursor.statistics(table_name, catalog='%', schema=schema, unique=False, quick=True):
        			constrained_columns.append(col)

		cdict = {"constrained_columns": constrained_columns,
     			 "name" : idxname
    		}
		cursor.close()
	finally:
		conn.close()
        return cdict

    @reflection.cache
    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        
        foreign_keys = []
	return foreign_keys

    @reflection.cache
    def get_unique_constraints(self, connection, table_name, schema=None, **kw):
        
        constraints = []
	return constraints

    @reflection.cache
    def get_check_constraints(self, connection, table_name, schema=None, **kw):
        
        constraints = []
	return constraints

    @reflection.cache
    def get_table_comment(self, connection, table_name, schema=None, **kw):
        
        comment = {"text": None}
	return comment

    @reflection.cache
    def get_indexes(self, connection, table_name, schema=None, **kw):
	conn = connection.engine.raw_connection()
	try:
		cursor = conn.cursor()
		indexes = []
		column_names = []
		for cat, sch, tab, unique, idxq, idxname, type, ord, col, asc, card, pgs, filt in \
        		cursor.statistics(table_name, catalog='%', schema=schema, unique=False, quick=True):
                		column_names.append(col)
		index_d = {}
		index_d['name'] = idxname
		index_d['column_names'] = column_names
		index_d['unique'] = not bool(unique)
		indexes.append(index_d)
		cursor.close()
	finally:
		conn.close()
        return indexes 

    def _check_unicode_returns(self, connection, additional_tests=None):
        return False

    def _check_unicode_description(self, connection):
        return False

    def do_rollback(self, dbapi_connection):
        # No support for transactions.
        pass

dialect = OcientDbDialect
