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