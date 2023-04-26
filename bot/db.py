import psycopg2


from config import Config


class Database:
    def __init__(self, config: Config):
        self.con = psycopg2.connect(
            host=config.db_host,
            dbname=config.db_name,
            user=config.db_user,
            password=config.db_pass,
            port=config.db_port
        )
        self.cur = self.con.cursor()

    def save_user(
            self,
            telegram_id: int,
            user: str,
            contacts: str,
            about: str,
            role: str,
            score: int
    ) -> str:
        result = self.cur.execute("SELECT insert_user(%s, %s, %s, %s, %s, %s)",
                                  (telegram_id, user, contacts, about, role, score))
        self.con.commit()
        return result
