import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Jobs(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'jobs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    team_leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)
    job = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    work_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    collaborators = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hazard_category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('hazard_categories.id'),
                                           nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.now)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.now)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)

    user = orm.relationship("User", foreign_keys=[team_leader])
    hazard_category = orm.relationship("HazardCategory", back_populates="jobs")
