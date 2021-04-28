import csv
from datetime import datetime
from io import StringIO
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from werkzeug.wrappers import Response

from src.db import query_db, extract_result
from src.solvers import SOLVERS
from tests.test import rainflow

bp = Blueprint('customer_service', __name__)

@bp.route('/', methods=['GET',])
@login_required
def index_backup():
    return redirect(url_for('customer_service.index'))

@bp.route('/index', methods=['GET',])
@login_required
def index():
    if g.user['username'] == 'admin':
        matches = query_db()
    else:
        matches = query_db(parm='username', value=g.user['username'])

    return render_template('customer/index.html', solvers=SOLVERS.keys(), matches=matches)

@bp.route('/request/<solver>', methods=['GET', 'POST'])
@login_required
def calrequest(solver):
    if request.method == 'POST':
        rainflow()
        # TODO 添加表单处理逻辑

    config_list = ['username', 'project', 'description'] + list(SOLVERS[solver][1]) + ['path_prefix']
    return render_template('customer/request.html', config_list=config_list)    

# example data, this could come from wherever you are storing logs
log = [
    ('login', datetime(2015, 1, 10, 5, 30)),
    ('deposit', datetime(2015, 1, 10, 5, 35)),
    ('order', datetime(2015, 1, 10, 5, 50)),
    ('withdraw', datetime(2015, 1, 10, 6, 10)),
    ('logout', datetime(2015, 1, 10, 6, 15))
]

@bp.route('/download')
@login_required
def download_log():
    def generate():
        data = StringIO()
        w = csv.writer(data)

        # write header
        w.writerow(('action', 'timestamp'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # write each log item
        for item in log:
            w.writerow((
                item[0],
                item[1].isoformat()  # format datetime as string
            ))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    # stream the response as the data is generated
    response = Response(generate(), mimetype='text/csv')
    # add a filename
    response.headers.set("Content-Disposition", "attachment", filename="log.csv")
    return response

@bp.route('/download/<_id>')
@login_required
def download(_id):
    def generate(result):
        data = StringIO()

        # write header
        fieldnames = ['torque'] + [str(angal) for angal in range(0,27)]
        w = csv.DictWriter(data, fieldnames=fieldnames)
        w.writeheader()
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # write each log item
        for torque, count in result.items():
            count['torque'] = str(torque)
            w.writerow(count)

            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    for match in query_db(parm='_id', value=_id):
        result = extract_result(match)
    # stream the response as the data is generated
    response = Response(generate(result), mimetype='text/csv')
    # add a filename
    response.headers.set("Content-Disposition", "attachment", filename=_id + ".csv")
    return response
