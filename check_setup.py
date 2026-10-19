import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
url = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)
with create_engine(url).connect() as conn:
    print(conn.execute(text("select version()")).scalar())