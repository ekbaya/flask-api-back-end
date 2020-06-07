# import the pymysql module

import MySQLdb
import datetime
import time



# Code for creating a connection object
db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="",  # your password
                     db="mysql")        # name of the data base

try:

    # Code for  creating cursor from database connection

    cursorInstance = db.cursor()

    # Code for calculating timestamp of 14 days ago
    tod = datetime.datetime.now()
    d = datetime.timedelta(days = 14)
    a = tod - d

    unixtime = time.mktime(a.timetuple())



    # SQL statement for deleting rows from a table matching a criteria

    sqlDeleteRows = "Delete from locations where time_stamp < 'unixtime'"



    # using the cursor delete a set of rows from the table

    cursorInstance.execute(sqlDeleteRows)



    # Check if there are any existing items with expired status

    sqlSelectRows   = "select * from locations"



    # Execute the SQL query

    cursorInstance.execute(sqlSelectRows)



    #Fetch all the rows using cursor object

    itemRows = cursorInstance.fetchall()



    # print all the remaining rows after deleting the rows with status as "expired"

    for item in itemRows:

        print(item)



except Exception as ex:

    print("Exception occured: %s"%ex)

finally:

    cursorInstance.close()