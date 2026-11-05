from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

db_path = Path(__file__).resolve().parent / 'employee_events.db'


# Define a class called `QueryMixin`
class QueryMixin:
    def pandas_query(self, sql_query):
        connection = connect(db_path)
        try:
            return pd.read_sql_query(sql_query, connection)
        finally:
            # Always release the connection, even if the query fails
            connection.close()

    def query(self, sql_query):
        connection = connect(db_path)
        try:
            cursor = connection.cursor()
            return cursor.execute(sql_query).fetchall()
        finally:
            connection.close()


# Leave this code unchanged
def query(func):
    """
    Decorator that runs a standard sql execution
    and returns a list of tuples
    """
    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result
    return run_query
