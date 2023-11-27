import pymysql
import logging
from typing import List, Tuple, Any


class MySQLServerManager(object):
    def __init__(
        self,
        host: str,
        port: str,
        user: str,
        password: str,
        database: str = None,
    ):
        """
        MySQL server manager.

        Parameters
        ----------
        host : str
            Connection host.
        port : str
            Connection port.
        user : str
            User name.
        password : str
            Password.
        database : str, optional
            Try to activate a database, by default None

        Raises
        ------
        Exception
            Port cannot be converted to an integer.
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
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
        )
        self.cursor = self.connection.cursor()

        if database is not None:
            if self.cursor.execute(f"SHOW DATABASES LIKE '{database}'") == 0:
                logging.warning(f"Database {database} not exists!")
            else:
                self.cursor.execute(f"USE {database}")
                self.database_activated = database

    def execute_query(self, query: str, args: list | tuple | dict = None):
        """
        Execute a SQL query.

        Parameters
        ----------
        query : str
            SQL query.
        args : list | tuple | dict, optional
            If args is a list or tuple, %s can be used as a placeholder in the query.
            If args is a dict, %(name)s can be used as a placeholder in the query.
            By default None
        """
        self.cursor.execute(query, args)

    def execute_file(self, file_path: str):
        """
        Execute a SQL script.

        Parameters
        ----------
        file_path : str
            SQL script file path.

        Raises
        ------
        Exception
            The file must be a SQL script which ends with ".sql".
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

    def result(self) -> Tuple[Tuple[Any, ...], ...]:
        """
        Get the result of the last query.

        Returns
        -------
        Tuple[Tuple[Any, ...], ...]
            The result of the last query.
        """
        return self.cursor.fetchall()

    def commit(self):
        """
        Commit the changes.
        The changes that need to be committed include:
            - CREATE DATABASE
            - DROP DATABASE
            - CREATE TABLE
            - DROP TABLE
            - INSERT
            - DELETE

        Query
        -----
            >>> COMMIT
        """
        self.connection.commit()

    def has_database(self, database: str) -> bool:
        """
        Check if the database exists.

        Parameters
        ----------
        database : str
            Database name.

        Returns
        -------
        bool
            True if the database exists, otherwise False.

        Query
        -----
            >>> SHOW DATABASES LIKE database
        """
        return self.cursor.execute(f"SHOW DATABASES LIKE '{database}'") != 0

    def create_database(self, database: str):
        """
        Create a database.

        Parameters
        ----------
        database : str
            Database name.

        Raises
        ------
        Exception
            The database already exists.

        Query
        -----
            >>> CREATE DATABASE database
        """
        if self.has_database(database):
            raise Exception(f"Database {database} already exists!")
        self.cursor.execute(f"CREATE DATABASE {database}")

    def drop_database(self, database: str):
        """
        Drop a database.

        Parameters
        ----------
        database : str
            Database name.

        Raises
        ------
        Exception
            The database not exists.

        Query
        -----
            >>> DROP DATABASE database
        """
        if not self.has_database(database):
            raise Exception(f"Database {database} not exists!")
        self.cursor.execute(f"DROP DATABASE {database}")

    def activate_database(self, database: str):
        """
        Activate a database.

        Parameters
        ----------
        database : str
            Database name.

        Raises
        ------
        Exception
            The database not exists.

        Query
        -----
            >>> USE database
        """
        if not self.has_database(database):
            raise Exception(f"Database {database} not exists!")
        self.cursor.execute(f"USE {database}")
        self.database_activated = database

    def create_table(self, table_name: str, columns: list[str]):
        """
        Create a table.

        Parameters
        ----------
        table_name : str
            Table name.
        columns : list[str]
            Columns of the table.

        Raises
        ------
        Exception
            No database activated. Call method `activate_database()` first.

        Query
        -----
            >>> CREATE TABLE table_name (columns)
        """
        if self.database_activated is None:
            raise Exception("No database activated!")
        else:
            self.cursor.execute(
                f"CREATE TABLE {table_name} ({','.join(columns)})"
            )

    def erase_table(self, table_name: str):
        """
        Erase a table.

        Parameters
        ----------
        table_name : str
            Table name.

        Raises
        ------
        Exception
            No database activated. Call method `activate_database()` first.
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
        each_row: Any = None,
        each_elem: Any = None,
    ):
        """
        Insert records.

        Parameters
        ----------
        table_name : str
            Table name.
        columns : List[str], optional
            Column names of inserted values, by default None (means all columns).
        values : List[List], optional
            Values to insert, by default None.
        each_row : Any, optional
            A function to process each row, by default None.
        each_elem : Any, optional
            A function to process each element, by default None.

        Raises
        ------
        Exception
            No database activated. Call method `activate_database()` first.
        Exception
            No values to insert.

        Query
        -----
            >>> INSERT INTO table_name (columns) VALUES (values)
        """
        if self.database_activated is None:
            raise Exception("No database activated!")
        if values is None or len(values) == 0 or len(values[0]) == 0:
            raise Exception("No values to insert!")

        if each_elem is not None and each_row is not None:
            values = [
                each_row([each_elem(elem) for elem in row]) for row in values
            ]
        elif each_elem is not None:
            values = [[each_elem(elem) for elem in row] for row in values]
        elif each_row is not None:
            values = [each_row(row) for row in values]

        if columns is not None:
            self.cursor.executemany(
                f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({','.join(['%s'] * len(columns))})",
                values,
            )
        else:
            self.cursor.executemany(
                f"INSERT INTO {table_name} VALUES ({','.join(['%s'] * len(values[0]))})",
                values,
            )

    def delete(self, table_name: str, condition: str = None):
        """
        Delete records.

        Parameters
        ----------
        table_name : str
            Table name.
        condition : str, optional
            Condition, by default None (means all records).

        Raises
        ------
        Exception
            No database activated. Call method `activate_database()` first.

        Query
        -----
            >>> DELETE FROM table_name WHERE condition
        """
        if self.database_activated is None:
            raise Exception("No database activated!")
        if condition is None:
            self.cursor.execute(f"DELETE FROM {table_name}")
        else:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
