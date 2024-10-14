# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URI = 'mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server'

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

def get_db_session():
    return Session()