import mysql.connector
import asyncio

class DatabaseConnection:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.mydb = None

    async def get_connection(self):
        if self.mydb is None:
            pairs = (("host", self.host), ("user", self.user), ("password", self.password), ("database", self.database))
            missing = [name for name, val in pairs if not val]
            if missing:
                raise ValueError(f"Missing DB connection parameters: {missing}")
            try:
                loop = asyncio.get_running_loop()
                self.mydb = await loop.run_in_executor(None, lambda: mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                ))
            except mysql.connector.Error as e:
                raise ConnectionError(f"Error connecting to database: {e}") from e
        return self.mydb

    async def close_connection(self):
        if self.mydb is not None:
            try:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, self.mydb.close)
            finally:
                self.mydb = None