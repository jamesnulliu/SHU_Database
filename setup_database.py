from lqsym import MySQLServerManager
import pandas as pd

DATABASE = "school"
mysql = MySQLServerManager(
    host="localhost", port="3306", user="root", password="654321"
)

# Drop the original database if exists
if mysql.has_database(DATABASE):
    mysql.drop_database(DATABASE)
# Create a new database called school
mysql.create_database(DATABASE)
# Activate the database
mysql.activate_database(DATABASE)
# Create all tables with the given sql file
mysql.execute_file(file_path="create_tables.sql")

TABLES = [
    "colleges",
    "courses",
    "students",
    "teachers",
    "class_schedule",
    "course_selection",
]


def each_elem_course_selection(elem):
    if str(elem) == "nan":
        return None
    else:
        return elem


def each_row_course_selection(row):
    class_shcedule_id, semester, course_id, teacher_id = row[2:6]
    # Check if the class_schedule_id exists
    mysql.execute_query(
        f"SELECT id FROM class_schedule  \
        WHERE id = {class_shcedule_id} AND semester = '{semester}' AND  \
        course_id = {course_id} AND teacher_id = {teacher_id}"
    )
    if mysql.result():
        return row
    else:
        raise Exception(f"Class schedule id {class_shcedule_id} not exists!")


for table in TABLES:
    data = pd.read_csv(f"./data/{table}.csv").values.tolist()
    if table == "course_selection":
        mysql.insert(
            table_name=table,
            values=data,
            each_row=each_row_course_selection,
            each_elem=each_elem_course_selection,
        )
    else:
        mysql.insert(table_name=table, values=data)
mysql.commit()
