import sqlite3
from sqlite3 import Error

database_name = 'database.db'

class DataBase:
    
    @staticmethod 
    def createTable(query):
        try:
            con = sqlite3.connect(database_name)
            c = con.cursor()
            c.execute(query)
        except Error as e:
            print(e)
            
    @staticmethod
    def select(name):
        try:
            con = sqlite3.connect(database_name)
            c = con.cursor()
            c.execute(f"SELECT * FROM information WHERE name='{name}'")
            result = c.fetchone()                
            con.close()
            return result[2]
        except Error as e:
            print(e)
            
    @staticmethod
    def update(name, value):  
        try:
            con = sqlite3.connect(database_name)
            c = con.cursor()
            c.execute(f"UPDATE information SET value='{value}' WHERE name='{name}'")
            con.commit()
            con.close()
            return True
        except Error as e:
            print(e)

#sql_create_table = "CREATE TABLE IF NOT EXISTS information (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255) NOT NULL, value VARCHAR(255) NOT NULL);"

#result = LocalDataBase.updateOne('system_id', '3')
#print(result)

#result = LocalDataBase.selectOne('item_camera_port')[2]
#print(result)