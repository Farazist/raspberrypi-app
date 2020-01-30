import mysql.connector


class Database:

    @staticmethod
    def connect():
        return mysql.connector.connect(
            host="93.115.150.179",
            user="farazist_user",
            passwd="sara&sajjad&amir",
            database="farazist_db"
        )

    @staticmethod
    def login(mobileNumber):
        mydb = Database.connect()

        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM users WHERE user_mobileNumber = '{mobileNumber}'")
        result = mycursor.fetchall()

        if len(result) == 0:
            return None
        else:
            return result[0]

    @staticmethod
    def getCategories():
        mydb = Database.connect()

        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM categories")
        result = mycursor.fetchall()

        return result

    @staticmethod
    def getWastes():
        mydb = Database.connect()

        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM wastes")
        result = mycursor.fetchall()

        return result

    @staticmethod
    def getWallet(mobileNumber):
        mydb = Database.connect()

        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM users")
        result = mycursor.fetchall()

        return result        

