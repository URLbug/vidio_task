from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,String,Integer,Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData


DATABASE_NAME = 'bot'

engine = create_engine('sqlite:///sqlite3.db')

Base = declarative_base()
metadata_obj = MetaData()

Session = sessionmaker(bind=engine)

session = Session()

user = Table(
    "user",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String(100)),
    Column('user_id', Integer),
    Column('balans', Integer),
    Column('regis', String(500)),
    Column('uniqueized', Integer),
    Column('comand', Integer)
)


class User(Base):

  __tablename__ = 'user'

  id = Column(Integer, primary_key=True)
  username = Column(String(100))
  user_id = Column(Integer)
  balans = Column(Integer)
  regis = Column(String(500))
  uniqueized = Column(Integer)
  comand = Column(Integer)

  def update_name(id_to_update, new_desc):
    try:
        session.query(User).filter(User.username == id_to_update).\
            update({User.username: new_desc}, synchronize_session=False)
        session.commit()
    except:
        session.rollback()

def creates(what):
  try:
    what.create(engine)
  except:
    print('goal')

creates(user)