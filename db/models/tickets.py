import datetime as dt
import sqlalchemy as sq

from db import Model
from db import ModelMixin

from sqlalchemy import orm

__all__ = ["Client", "Ticket", "Context"]
ago15 = lambda: dt.datetime.now() - dt.timedelta(minutes=15)


class Client(Model, ModelMixin):
    __tablename__ = "clients"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, nullable=False, unique=False)

    blacklisted = sq.Column(sq.Boolean, nullable=False, default=False)
    blacklisted_until = sq.Column(sq.DateTime, nullable=True)

    last_used = sq.Column(sq.DateTime, nullable=False, default=ago15())

    tickets = orm.relationship("Ticket", backref="client")

    def blacklist(self, hrs: int):
        self.blacklisted = True
        self.blacklisted_until = dt.datetime.now() + dt.timedelta(hours=hrs)
    
    def whitelist(self):
        self.blacklisted = False
        self.blacklisted_until = None

    def bl_delta(self):
        return abs(self.blacklisted_until - dt.datetime.now())

    def opened(self):
        self.last_used = dt.datetime.now()

    def can_open(self):
        has_open = True in [t.resolved for t in self.tickets]
        delta = (self.last_used - dt.datetime.now() >= dt.timedelta(minutes=15))

        if self.blacklisted:
            return False, "You have been blacklisted from opening tickets."
        
        if not delta:
            return False, "You can only open a thread once every 15 minutes!"
        
        if has_open:
            return False, "You already have a thread open. Please resolve that one first."

        return True


class Ticket(Model, ModelMixin):
    __tablename__ = "tickets"

    id = sq.Column(sq.Integer, primary_key=True)
    type_ = sq.Column(sq.String, nullable=False)
    body = sq.Column(sq.String, nullable=True)
    thread_id = sq.Column(sq.Integer, nullable=False)
    notice_id = sq.Column(sq.Integer, nullable=True)

    stamp = sq.Column(sq.DateTime, default=dt.datetime.now(), nullable=False)

    archived = sq.Column(sq.Boolean, nullable=False, default=False)
    resolved = sq.Column(sq.Boolean, nullable=False, default=False)
    resolved_at = sq.Column(sq.DateTime, nullable=True)

    contexts = orm.relationship("Context", backref="ticket")
    client_id = sq.Column(sq.Integer, sq.ForeignKey("clients.id"))


class Context(Model, ModelMixin):
    __tablename__ = "contexts"

    id = sq.Column(sq.Integer, primary_key=True)
    url = sq.Column(sq.String, nullable=False)
    type_ = sq.Column(sq.String, nullable=False, default="image")

    ticket_id = sq.Column(sq.Integer, sq.ForeignKey("tickets.id"))
