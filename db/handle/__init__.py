import logging

import sqlalchemy as sq

from sqlalchemy import orm


DB_URI = "sqlite:///db/db/site.db"
BASE = orm.declarative_base()

handler = logging.FileHandler("db/logs/actions.log")
handler.setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy').addHandler(handler)

engine = sq.create_engine(DB_URI, echo=True)
session = (orm.sessionmaker(engine))()


from .models import Tag
from .models import DumpEntry
from .models import Attachment