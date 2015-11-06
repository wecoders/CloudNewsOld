from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
engine = create_engine("mysql+mysqlconnector://root:admin@localhost/spider?charset=utf8")

Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)

ScopedSession = scoped_session(sessionmaker(bind=engine, autoflush=True, autocommit=False))


class DBSession(object):
    """docstring for MySQLSession"""
    def __init__(self, ):
        super(MySQLSession, self).__init__()
        self.session = Session()
        
    def query(self, clz):
        return self.session.query(clz)

    def commit(self, autoclose=True):
        self.session.commit()
        if autoclose==True:
            self.session.close()


