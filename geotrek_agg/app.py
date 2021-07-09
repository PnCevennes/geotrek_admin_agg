import os

from flask import Flask
from flask import render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, 
            static_url_path='', 
            static_folder='../web/static',
            template_folder='../web/templates'
)
 
# load the instance config, if it exists, when not testing
app.config.from_pyfile('../config/config.py', silent=False)

DB = SQLAlchemy(app)
DB.init_app(app)

with app.app_context(): 

    from geotrek_agg.commands import create_db_schema, import_mapping, populate_gta
    app.cli.add_command(create_db_schema)
    app.cli.add_command(import_mapping)
    app.cli.add_command(populate_gta)

    from geotrek_agg.mapping_app import mapping_app
    app.register_blueprint(mapping_app)
