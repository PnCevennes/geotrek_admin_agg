from flask import Blueprint, render_template, request, redirect , url_for

from geotrek_agg.app import DB
from geotrek_agg.models import CommonCorrespondances
from geotrek_agg.utils import get_structured_cor_data, get_mapping_el, update_cor_data



mapping_app = Blueprint('mapping_app', __name__)

@mapping_app.route('/')
def render_mapping():
    try:
        data = CommonCorrespondances.query.all()
    except Exception as e:
        print(e)

    structured_voc_data = get_structured_cor_data(DB) 
    
    return render_template(
        'index.html', 
        correspondances=data, 
        col=CommonCorrespondances.__table__.columns.keys(), 
        display_col=("bdd_source", "table_origin", "label_origin"), 
        voc_data=structured_voc_data
    )

@mapping_app.route('/edit_mapping/<id>', methods=["GET", "POST"])
def edit_mapping(id):
    if request.method == 'POST':
        result = request.form
        new_mapping_id = result.get('new_mapping') 
        if new_mapping_id and new_mapping_id == 'None':
            new_mapping_id = None
        update_cor_data(DB, id, new_mapping_id)
        return redirect(url_for('mapping_app.render_mapping'))
    else:
        data = get_mapping_el(DB, id)
        structured_voc_data = get_structured_cor_data(DB) 
        print("data edit maping")
        return render_template(
            'edit_mapping.html',
            el_mapping=data, 
            voc_data=structured_voc_data
        )
