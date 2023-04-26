import os
from dotenv import load_dotenv


class Config():
    def __init__(self) -> None:
        load_dotenv()
        self.token = os.getenv("TOKEN")
        self.db_host = os.getenv("DB_HOST")
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_pass = os.getenv("DB_PASS")
        self.db_port = os.getenv("DB_PORT")
        self.chat_id = os.getenv("CHAT_ID")
