from db import Model
from db import ModelMixin

import sqlalchemy as sq

from sqlalchemy import orm

from datetime import datetime as dt

__all__ = ["DumpEntry", "Tag", "Attachment"]


class DumpEntry(Model, ModelMixin):
    __tablename__ = "entries"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String, nullable=False)
    stamp = sq.Column(sq.DateTime, default=dt.now(), nullable=False)

    tags = orm.relationship("Tag", backref="entry")
    atch = orm.relationship("Attachment", back_populates="entry", uselist=False)


class Tag(Model, ModelMixin):
    __tablename__ = "tags"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String, nullable=False)
    entry_id = sq.Column(sq.Integer, sq.ForeignKey("entries.id"))

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()


class Attachment(Model, ModelMixin):
    __tablename__ = "attachments"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String, nullable=False)
    url = sq.Column(sq.String, nullable=False)
    entry_id = sq.Column(sq.Integer, sq.ForeignKey("entries.id"))

    entry = orm.relationship("DumpEntry", back_populates="atch")
