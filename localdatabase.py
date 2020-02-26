import sqlite3
from sqlite3 import Error
from app import *

class LocalDataBase:

    @staticmethod
    def createConnection():
        con = None
        try:
            con = sqlite3.connect(local_database_name)
            print(sqlite3.version)
        except Error as e:
            print(e)
        finally:
            return con
                
    @staticmethod 
    def createTable(query):
        con = LocalDataBase.createConnection()
        if con is not None:
            try:
                c = conn.cursor()
                c.execute(query)
            except Error as e:
                print(e)
        else:
            print("Error! cannot connect.")

    @staticmethod
    def selectOne(name):
        con = LocalDataBase.createConnection()   
        if con is not None:
            try:
                c = con.cursor()
                c.execute(f"SELECT * FROM information WHERE name='{name}'")
                result = c.fetchone()                
                con.close()
                return result
            except Error as e:
                print(e)
        else:
            print("Error! cannot connect.")

    @staticmethod
    def updateOne(name, value):
        con = LocalDataBase.createConnection()   
        if con is not None:
            try:
                c = con.cursor()
                c.execute(f"UPDATE information SET value = '{value}' WHERE name='{name}'")
                con.commit()
                con.close()
                return True
            except Error as e:
                print(e)
        else:
            print("Error! cannot connect.")


#sql_create_table = "CREATE TABLE IF NOT EXISTS information (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255) NOT NULL, value VARCHAR(255) NOT NULL);"

#result = LocalDataBase.updateOne('system_id', '3')
#print(result)

#result = LocalDataBase.selectOne('system_id')
#print(result)