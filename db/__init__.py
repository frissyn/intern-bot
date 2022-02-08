import logging

import sqlalchemy as sq

from sqlalchemy import orm


DB_URI = "sqlite:///db/db/site.db"
Model = orm.declarative_base()

rootLog = logging.getLogger("sqlalchemy")
enLog = logging.getLogger("sqlalchemy.engine")
rootLog.handlers, enLog.handlers, = [], []

handler = logging.FileHandler("db/logs/actions.log")
handler.setLevel(logging.DEBUG)
enLog.addHandler(handler)

engine = sq.create_engine(DB_URI, echo=False)
session = (orm.sessionmaker(engine))()


class ModelMixin():
    def update(self, **kwargs):
        cols = []

        for c in list(self.__table__.columns):
            cols.append(str(c).replace(f"{self.__tablename__}", ""))
        
        for row, val in kwargs.items():
            self.__setattr__(row, val)

        session.commit()

    def add_self(self, s):
        s.add(self)