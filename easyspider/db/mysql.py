from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
engine = create_engine("mysql+mysqlconnector://root:admin@localhost/spider?charset=utf8")

Session = sessionmaker(bind=engine)

ScopedSession = scoped_session(sessionmaker(bind=engine, autoflush=True, autocommit=False))


