from lqsym import MySQLServerManager
import pandas as pd

DATABASE = "school"
mysql = MySQLServerManager(host="localhost", port="3306", user="root", password="654321")
mysql.activate_database(DATABASE)

mysql.execute_query("SELECT * FROM students WHERE id = 1101")

print(mysql.result())