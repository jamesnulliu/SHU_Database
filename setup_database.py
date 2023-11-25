from lqsym import MySQLServerManager
import pandas as pd

DATABASE = "school"
mysql = MySQLServerManager(host="localhost", port="3306", user="root", password="654321")

# Drop the original database if exists
if mysql.has_database(DATABASE):
    mysql.drop_database(DATABASE)
# Create a new database called school
mysql.create_database(DATABASE)
# Activate the database
mysql.activate_database(DATABASE)
# Create all tables with the given sql file
mysql.execute_file(file_path="create_tables.sql")

TABLES = ["colleges", "courses", "students", "teachers", "class_schedule", "course_selection"]
for table in TABLES:
    data = pd.read_csv(f"./data/{table}.csv").values.tolist()
    if table == "course_selection":
        mysql.insert(table_name=table, values=data, replace=(['nan'],None))
    else:
        mysql.insert(table_name=table, values=data)
mysql.commit()