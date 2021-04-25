import csv
from datetime import datetime
from io import StringIO
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from werkzeug.wrappers import Response

from src.db import query_db, extract_result

bp = Blueprint('customer_service', __name__)

@bp.route('/', methods=['GET',])
def index():
    pass

@bp.route('/test')
def test():
    return render_template('base.html')

@bp.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':

        name = request.form['name']
        phone = request.form['phone']
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
         
        db = get_db()
        client_record = get_client(phone)
            
        if client_record is None:
            db.execute(
                'INSERT INTO client (name, phone) VALUES (?, ?)', (name, phone)
            )
            db.commit()
            client_record = get_client(phone)
            
        reservation_info = (client_record['id'], service, date, time)

        db.execute(
            'INSERT INTO reservation (uid, service, date, time) VALUES (?, ?, ?, ?)', reservation_info
        )
        db.commit()

        return redirect(url_for('customer_service.receipt', name=name, date=date, time=time))

    return render_template('customer/solver.html')

@bp.route('/receipt/<name>&<date>&<time>', methods=['GET',])
def receipt(name, date, time):
    return render_template('customer/receipt.html', name=name, date=date, time=time)

@bp.route('/update/<date>', methods=['GET','POST'])
def update(date):
    if request.method == 'POST':
        available_time = [str(i) + ':00' + '~' + str(i+1) + ':00' for i in range(8, 17)]
        available_time = set(available_time)

        db = get_db()
        reserved_time = db.execute(
            'SELECT time FROM reservation WHERE date = ?', (date,)
        ).fetchall()

        if reserved_time:
            for time in reserved_time:
                if time[0] in available_time:
                    available_time.remove(time[0])
        available_time = list(available_time)
        available_time.sort()

        result = '<div class="col-md-6"><label for="time" class="form-label">Time</label><select name="time" class="form-select" id="time" required><option value="">Choose...</option>'
        for time in available_time:
            result += '<option>{}</option>'.format(time)
        result += '</select><div class="invalid-feedback">Please select a valid time.</div></div>'
                
        return result



# example data, this could come from wherever you are storing logs
log = [
    ('login', datetime(2015, 1, 10, 5, 30)),
    ('deposit', datetime(2015, 1, 10, 5, 35)),
    ('order', datetime(2015, 1, 10, 5, 50)),
    ('withdraw', datetime(2015, 1, 10, 6, 10)),
    ('logout', datetime(2015, 1, 10, 6, 15))
]

@bp.route('/download')
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
def download(_id):
    def generate(result):
        data = StringIO()

        # write header
        fieldnames = ['torque'] + [str(angal) + '.0' for angal in range(0,27)]
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
    response.headers.set("Content-Disposition", "attachment", filename="log.csv")
    return response

def get_client(phone):
    db = get_db()
    client_record = db.execute(
            'SELECT id, name FROM client WHERE phone = ?', (phone,)
    ).fetchone()

    return client_record
