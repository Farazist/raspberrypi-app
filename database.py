from sqlite3 import connect

database_name = 'database.db'

class DataBase:
    
    @staticmethod 
    def createTable(query):
        try:
            con = connect(database_name)
            c = con.cursor()
            c.execute(query)
        except Exception as e:
            print("error:", e)

    @staticmethod
    def insert(name, value):
        try:
            con = connect(database_name)
            c = con.cursor()
            c.execute(f"INSERT INTO information (name, value) VALUES (%s, %s)")
            con.commit()
            con.close()
            return True
        except Exception as e:
            print("error:", e)

    @staticmethod
    def select(name):
        try:
            con = connect(database_name)
            c = con.cursor()
            c.execute(f"SELECT * FROM information WHERE name='{name}'")
            result = c.fetchone()                
            con.close()
            return result[1]
        except Exception as e:
            print("error:", e)
            
    @staticmethod
    def update(name, value):  
        try:
            con = connect(database_name)
            c = con.cursor()
            c.execute(f"UPDATE information SET value='{value}' WHERE name='{name}'")
            con.commit()
            con.close()
            return True
        except Exception as e:
            print("error:", e)

#sql_create_table = "CREATE TABLE IF NOT EXISTS information (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255) NOT NULL, value VARCHAR(255) NOT NULL);"

#result = LocalDataBase.updateOne('system_id', '3')
#print(result)

#result = LocalDataBase.selectOne('item_camera_port')[2]
#print(result)