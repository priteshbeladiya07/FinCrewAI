from sqlalchemy import text

from app.database.connection import Base, engine

# Import models so SQLAlchemy registers their tables.
from app.database.models import ResearchJob


def create_tables():

    Base.metadata.create_all(bind=engine)


def test_connection():

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True


def initialize_database():

    test_connection()
    create_tables()

    print("PostgreSQL connected successfully.")
    print("Database tables initialized successfully.")