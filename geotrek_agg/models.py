from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Sequence
from geotrek_agg.app import DB


class GeotrekAggCorrespondances(DB.Model):
    __tablename__ = "geotrekagg_correspondances"
    __table_args__ = {"schema": "public"}
    id = DB.Column(DB.Integer)
    bdd_source = DB.Column(DB.Unicode, primary_key=True)
    table_origin = DB.Column(DB.Unicode, primary_key=True)
    id_origin = DB.Column(DB.Integer, primary_key=True)
    label_origin = DB.Column(DB.Unicode)
    id_destination = DB.Column(DB.Integer)



class GeotrekAggSources(DB.Model):
    __tablename__ = "geotrekagg_sources"
    __table_args__ = {"schema": "public"}
    id = DB.Column(DB.Integer)
    bdd_source = DB.Column(DB.Unicode, primary_key=True)

