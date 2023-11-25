import pymysql
from typing import List, Tuple, Any


class MySQLServerManager(object):
    def __init__(self, host: str, port: str, user: str, password: str, database: str = None):
        """Create a MySQL server manager.

        Args:
            host (str): IP address of the server.
            port (str): Port number.
            user (str): Username.
            password (str): Password.
            database (str, optional): Database name. Defaults to None.

        Raises:
            Exception: If the database is not None but not exists in the server.
        """
        super().__init__()
        self.database_activated = None
        self.host = host
        try:
            self.port = int(port)
        except:
            raise Exception("Port must be a number!")
        self.user = user
        self.password = password
        self.connection = pymysql.connect(host=self.host, user=self.user, password=self.password, port=self.port)
        self.cursor = self.connection.cursor()

        if database is not None:
            if self.cursor.execute(f"SHOW DATABASES LIKE '{database}'") == 0:
                raise Exception(f"Database {database} not exists!")
            else:
                self.cursor.execute(f"USE {database}")
                self.database_activated = database

    def execute_query(self, query: str):
        """Execute a query.

        Args:
            query (str): Query.
        """
        self.cursor.execute(query)

    def execute_file(self, file_path: str):
        """Execute a SQL script.

        Args:
            file_path (str): File path.
        """
        if not file_path.endswith(".sql"):
            raise Exception("File must be a SQL script!")
        with open(file_path, "r") as f:
            statements = f.read().split(";")
            # Remove the last empty statement
            statements.pop()
            # Remove the blank lines
            statements = [statement.strip() for statement in statements]
            # Add the semicolon back
            for statement in statements:
                self.cursor.execute(statement + ";")

    def result(self):
        """Get the result of the last query.

        Returns:
            list: Result.
        """
        return self.cursor.fetchall()

    def commit(self):
        """Commit changes."""
        self.connection.commit()

    def has_database(self, database: str) -> bool:
        """Check if a database exists.

        Query:
            SHOW DATABASES LIKE 'database'

        Args:
            database (str): Database name.

        Returns:
            bool: True if exists, False otherwise.
        """
        return self.cursor.execute(f"SHOW DATABASES LIKE '{database}'") != 0

    def create_database(self, database: str):
        """Create a database.

        Query:
            CREATE DATABASE database

        Args:
            database (str): Database name.

        Raises:
            Exception: If the database already exists.
        """
        if self.has_database(database):
            raise Exception(f"Database {database} already exists!")
        self.cursor.execute(f"CREATE DATABASE {database}")

    def drop_database(self, database: str):
        """Erase a database.

        Query:
            DROP DATABASE database

        Args:
            database (str): Database name.

        Raises:
            Exception: If the database not exists.
        """
        if not self.has_database(database):
            raise Exception(f"Database {database} not exists!")
        self.cursor.execute(f"DROP DATABASE {database}")

    def activate_database(self, database: str):
        """Activate a database.

        Query:
            USE database

        Args:
            database (str): Database name.

        Raises:
            Exception: If the database not exists.
        """
        if not self.has_database(database):
            raise Exception(f"Database {database} not exists!")
        self.cursor.execute(f"USE {database}")
        self.database_activated = database

    def create_table(self, table_name: str, columns: list[str]):
        """Create a table.

        Query:
            CREATE TABLE table_name (columns)

        Args:
            table_name (str): Table name.
            columns (list[str]): Columns.

        Raises:
            Exception: If no database activated.
        """
        if self.database_activated is None:
            raise Exception("No database activated!")
        else:
            self.cursor.execute(f"CREATE TABLE {table_name} ({','.join(columns)})")

    def erase_table(self, table_name: str):
        """Erase a table.

        Query:
            DROP TABLE table_name

        Args:
            table_name (str): Table name.

        Raises:
            Exception: If no database activated.
        """
        if self.database_activated is None:
            raise Exception("No database activated!")
        else:
            self.cursor.execute(f"DROP TABLE {table_name}")

    def insert(
        self,
        table_name: str,
        columns: List[str] = None,
        values: List[List] = None,
        replace: Tuple[List, Any] = None,
    ):
        """Insert a record.

        Query:
            INSERT INTO table_name (columns) VALUES (values)

        Args:
            table_name (str): Table name.
            columns (List[str], optional): Columns of the insertion values. Defaults to None.
            values (List[List], optional): Insertion values. Defaults to None.
            replace (Tuple[List, Any], optional): Replace the target values in replace[0] with replace[1]. Defaults to None.

        Raises:
            Exception: If no database activated.
            Exception: If no values to insert.
        """
        if self.database_activated is None:
            raise Exception("No database activated!")
        if values is None or len(values) == 0 or len(values[0]) == 0:
            raise Exception("No values to insert!")
        if replace is not None:
            for target in replace[0]:
                values = [[replace[1] if str(x) == str(target) else x for x in sublist] for sublist in values]
        if columns is not None:
            self.cursor.executemany(
                f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({','.join(['%s'] * len(columns))})", values
            )
        else:
            self.cursor.executemany(f"INSERT INTO {table_name} VALUES ({','.join(['%s'] * len(values[0]))})", values)

    def delete(self, table_name: str, condition: str = None):
        """Delete records.

        Query:
            DELETE FROM table_name WHERE condition

        Args:
            table_name (str): Table name.
            condition (str, optional): Condition. Defaults to None.

        Raises:
            Exception: If no database activated.
        """
        if self.database_activated is None:
            raise Exception("No database activated!")
        if condition is None:
            self.cursor.execute(f"DELETE FROM {table_name}")
        else:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
