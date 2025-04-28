import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class HazardCategory(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'hazard_categories'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    level = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=True)
    jobs = orm.relationship("Jobs", back_populates="hazard_category")

    def __repr__(self):
        return f"HazardCategory(level={self.level}, name='{self.name}')"