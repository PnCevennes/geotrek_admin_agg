from enum import unique
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Sequence, UniqueConstraint
from geotrek_agg.app import DB


class GeotrekAggCorrespondances(DB.Model):
    __tablename__ = "geotrekagg_correspondances"
    __table_args__ = {"schema": "public"}
    id = DB.Column(
        DB.Integer,
        primary_key=True
    )
    bdd_source = DB.Column(DB.Unicode)
    table_origin = DB.Column(DB.Unicode)
    id_origin = DB.Column(DB.Integer)
    label_origin = DB.Column(DB.Unicode)
    id_destination = DB.Column(DB.Integer)
    UniqueConstraint(bdd_source, table_origin, id_origin)

class GeotrekAggSources(DB.Model):
    __tablename__ = "geotrekagg_sources"
    __table_args__ = {"schema": "public"}
    id = DB.Column(
        DB.Integer,
        primary_key=True
    )
    bdd_source = DB.Column(DB.Unicode, unique=True)

