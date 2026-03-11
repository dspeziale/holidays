from flask import Blueprint, render_template
from flask_login import login_required
from app.models.cliente import Cliente
from app.models.tour import Tour
from app.models.esperienza import Esperienza
from app.models.pacchetto import Pacchetto
from app.models.user import User

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')


@dashboard_bp.route('/')
@login_required
def index():
    stats = {
        'clienti': Cliente.query.count(),
        'tours': Tour.query.filter_by(attivo=True).count(),
        'esperienze': Esperienza.query.filter_by(attivo=True).count(),
        'pacchetti': Pacchetto.query.filter_by(attivo=True).count(),
        'utenti': User.query.count(),
    }
    tours_recenti = Tour.query.order_by(Tour.created_at.desc()).limit(5).all()
    esperienze_recenti = Esperienza.query.order_by(Esperienza.created_at.desc()).limit(5).all()
    return render_template('dashboard/index.html', stats=stats,
                           tours_recenti=tours_recenti,
                           esperienze_recenti=esperienze_recenti)
