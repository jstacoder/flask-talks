import os
from mongoengine import connect
from pymongo.errors import ConfigurationError,OperationFailure

def _get_conn_from_uri(uri):
    conn = connect(**_get_info_from_url(uri))
    return conn
    return conn[_get_info_from_url(uri)['db']]

def _get_info_from_url(uri):
    uri = uri.split('://')[-1]
    user_data,host_data =  uri.split('@')
    username,password = user_data.split(':')
    host,port = host_data.split(':')
    port,db = port.split('/')
    port = int(port)

    res = dict(username=username,password=password,host=host,port=port,db=db)
    return res

def get_connection():
    if 'MONGOLAB_URI' in os.environ:
        conn = connect(**_get_info_from_url(os.environ.get('MONGOLAB_URI')))
    else:
        conn = connect()
    return conn

def get_connection_and_dbname():
    conn = get_connection()
    if 'MONGOLAB_URI' in os.environ:
        dbname = _get_info_from_url(os.environ.get('MONGOLAB_URI'))['db']
    else:
        dbname = 'test'
    return dbname,conn
        

def get_default_db():
    dbname,conn = get_connection_and_dbname()
    try:
        if dbname in conn.database_names():
            rtn = conn[dbname]
    except OperationFailure:
        pass
    try:
        rtn = conn.get_default_database()
    except ConfigurationError:
        conn._MongoClient__default_database_name = dbname
        rtn = conn.get_default_database()
    return rtn
        
        
