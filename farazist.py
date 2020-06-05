import sqlite3
import os

conn = sqlite3.connect('database.db')
c = conn.cursor()
try:
#get the count of tables with the name
	c.execute(''' SELECT count(name) FROM information WHERE name='system_id' ''')
    #if the count is 1, then table exists
	if c.fetchone()[0]==1 :
		
		os.system('python main.py')
		print('Table exists.')
	else :
		print('Table does not exist.')
except Exception as e:
	os.system('python setup.py')
	print("error:", e)



#commit the changes to db
conn.commit()
#close the connection
conn.close()