import pyodbc

class SQLServerProvider:
    def __init__(self, connection_string):
        self.connection_string = connection_string
    
    def connect(self):
        return pyodbc.connect(self.connection_string)

    def query_data(self, query):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
