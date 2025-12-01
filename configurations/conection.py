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
                raise ValueError(f"La cadena de conexión tiene parametros vacíos: {missing}")
            try:
                loop = asyncio.get_running_loop()
                self.mydb = await loop.run_in_executor(None, lambda: mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                ))
            except mysql.connector.Error as e:
                raise ConnectionError(f"Error conectando a la base de datos: {e}") from e
        return self.mydb
