from db import Model

import sqlalchemy as sq

from sqlalchemy import orm

from datetime import datetime as dt


class StaleView(Model):
    __tablename__ = "staleviews"

    id = sq.Column(sq.Integer, primary_key=True)
    msg_id = sq.Column(sq.Integer, nullable=False)


class Tournament(Model):
    __tablename__ = "tournaments"

    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String, nullable=False)
    link = sq.Column(sq.String, nullable=False)
    active = sq.Column(sq.Boolean, nullable=False, default=True)
    stamp = sq.Column(sq.DateTime, nullable=False, default=dt.now())

    rounds = orm.relationship("Round", backref="tournament")


class Round(Model):
    __tablename__ = "rounds"

    id = sq.Column(sq.Integer, primary_key=True)
    rnum = sq.Column(sq.Integer, nullable=False)
    rtype = sq.Column(sq.Integer, nullable=False, default="Playoffs")

    players = orm.relationship("Player", backref="round")
    tourn_id = sq.Column(sq.Integer, sq.ForeignKey("tournaments.id"))


class Player(Model):
    __tablename__ = "players"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.Integer, nullable=False)
    votes = orm.relationship("Vote", backref="player")

    round_id = sq.Column(sq.Integer, sq.ForeignKey("rounds.id"))


class Vote(Model):
    __tablename__ = "votes"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, nullable=False)
    stamp = sq.Column(sq.DateTime, nullable=False, default=dt.now())

    player_id = sq.Column(sq.Integer, sq.ForeignKey("players.id"))
