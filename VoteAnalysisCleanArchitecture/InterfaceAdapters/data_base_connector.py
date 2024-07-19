import sqlite3


class DBConnectorMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DBConnector(metaclass=DBConnectorMeta):
    def __init__(self, db_name: str):
        self._db_name = db_name
        self._connection = sqlite3.connect(self._db_name)

    @property
    def db_name(self) -> str:
        return self._db_name

    @db_name.setter
    def db_name(self, new_name: str):
        self._db_name = new_name

    def connect_2_db(self):
        self._connection = sqlite3.connect(self._db_name)

    def execute_query(
        self, query_str, parameters=[], commit=False, return_query_set=True
    ):
        """
        It executes query string with or without parameters and commit and return query set if it is necessary
        :param query_str: SQL-query string for execution
        :param parameters: list ot tuples query parameters, by default is empty
        :param commit: Is needed commit query flag, by default is False
        :param return_query_set: Is needed return query set flag, by default is True
        :return: SQL query set or None
        """

        result = None
        cursor = self._connection.cursor()
        if parameters and all(
            isinstance(param, (tuple, list)) for param in parameters
        ):
            cursor.executemany(query_str, parameters)
        else:
            cursor.execute(query_str)
        if commit:
            self._connection.commit()
        if return_query_set:
            if "insert" in query_str.lower() and self.table_exists(
                query_str.split()[2]
            ):
                cursor.execute(
                    f"SELECT id FROM {query_str.split()[2]} WHERE rowid=last_insert_rowid();"
                )
            result = cursor.fetchall()
        cursor.close()
        return result

    def table_exists(self, table_name: str) -> bool:
        check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        return bool(self.execute_query(check_query))

    def __str__(self):
        return f"{self._db_name} – {str(self._connection)}"
