from flask import (
    Blueprint, g, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        date = request.form['date']
        db = get_db()
        reservations = db.execute(
            "SELECT uid, name, phone, date, time FROM reservation JOIN client ON client.id = reservation.uid WHERE date = ?", (date,)
        ).fetchall()
        return render_template('backend/dashboard.html', reservations=reservations)
    return render_template('backend/dashboard.html')