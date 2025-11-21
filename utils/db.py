from .configLoader import config
from mysql.connector import connect
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection as Db
from mysql.connector.cursor import MySQLCursor as Cursor
from functools import wraps

autoCommitPool = MySQLConnectionPool(
    pool_name="autocommitPool",
    pool_size=5,
    host=config.db.host,
    user=config.db.user,
    password=config.db.password,
    database=config.db.database,
    charset='utf8mb4',
    collation='utf8mb4_czech_ci',
    use_unicode=True,
    autocommit = True
)

pool = MySQLConnectionPool(
    pool_name="autocommitPool",
    pool_size=5,
    host=config.db.host,
    user=config.db.user,
    password=config.db.password,
    database=config.db.database,
    charset='utf8mb4',
    collation='utf8mb4_czech_ci',
    use_unicode=True,
    autocommit = False
)

def getConnection(autocommit = True) -> Db:
    """Returns database connection

    Args:
        autocommit (bool, optional): Is autocommit set? Defaults to True.

    Returns:
        Db: connection
    """
    if autocommit:
        return autoCommitPool.get_connection()
    else:
        return pool.get_connection()

def fetchOneWithNames(cursor: Cursor):
    """Returns first row as dict (key = column names)

    Args:
        cursor (Cursor): cursor with results of previous action

    Returns:
        dict: row
    """
    row = cursor.fetchone()
    columns = cursor.description
    result = {}
    if row is None:
        return None
    for index, column in enumerate(row):
        result[columns[index][0]] = column

    return result

def fetchAllWithNames(cursor: Cursor):
    """Returns list of rows as dict (key = column names)

    Args:
        cursor (Cursor): cursor with results of previous action

    Returns:
        list[dict]: rows
    """
    columns = cursor.description
    if cursor.rowcount == 0:
        return []
    else:
        return [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

def dbConn(autocommit: bool = True, buffered: bool = True):
    """ Wrapper that establishes connection to database
        function will be called like func(cursor=cursor, db=db, *args, **kwargs)
    Args:
        autocommit (bool, optional): Is autocommit set? Defaults to True.
        buffered (bool, optional): Is the connection buffered? Defaults to True.
    """
    def wrapper(func):
        @wraps(func)
        def connection(*args, **kwargs):
            db = getConnection(autocommit)
            cursor = db.cursor(buffered)
            try:
                result = func(cursor=cursor, db=db, *args, **kwargs)
            finally:
                cursor.close()
                db.close()
            return result
        return connection
    return wrapper

class DatabaseError(Exception):
    """Error after working with database."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
