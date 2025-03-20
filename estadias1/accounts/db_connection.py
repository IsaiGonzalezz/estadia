import pymysql

#bd emily
'''
host = 'localhost',
user = 'root',
password = 'miau',
database = 'CONTROL_INVENTARIO',
port = 3306
'''

#bd i
'''
host = 'localhost',
user = 'root',
password = '3Sa1s87873!',
database = 'EstadiaPruebas',
port = 3306
'''

class Database:
    def __init__(self) :
        self.connection = pymysql.connect(
            host = 'localhost',
            user = 'root',
            password = '3Sa1s87873!',
            database = 'CONTROL_INVENTARIO',
            port = 3306
        )

    def execute_query(self, query, params=()):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor

    def fetch_all(self, query, params=()):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result

    def close(self):
        if self.connection:
            self.connection.close()