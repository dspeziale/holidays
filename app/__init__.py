from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Effettua il login per accedere.'
login_manager.login_message_category = 'warning'


def create_app(config_name=None):
    import os
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.clienti import clienti_bp
    from app.routes.tours import tours_bp
    from app.routes.esperienze import esperienze_bp
    from app.routes.pacchetti import pacchetti_bp
    from app.routes.utenti import utenti_bp
    from app.routes.amadeus import amadeus_bp
    from app.routes.getyourguide import gyg_bp
    from app.routes.wizard import wizard_bp
    from app.routes.viaggi import viaggi_bp
    from app.routes.treni import treni_bp
    from app.routes.transfer import transfer_bp
    from app.routes.fornitori import fornitori_bp
    from app.routes.demo import demo_bp
    from app.routes.gateway import gateway_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clienti_bp)
    app.register_blueprint(tours_bp)
    app.register_blueprint(esperienze_bp)
    app.register_blueprint(pacchetti_bp)
    app.register_blueprint(utenti_bp)
    app.register_blueprint(amadeus_bp)
    app.register_blueprint(gyg_bp)
    app.register_blueprint(wizard_bp)
    app.register_blueprint(viaggi_bp)
    app.register_blueprint(treni_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(fornitori_bp)
    app.register_blueprint(demo_bp)
    app.register_blueprint(gateway_bp)

    # Filtri Jinja2
    import json as _json

    @app.template_filter('from_json')
    def from_json_filter(value):
        try:
            return _json.loads(value or '{}')
        except Exception:
            return {}

    @app.template_filter('formato_valuta')
    def formato_valuta_filter(value, paese=None):
        try:
            if isinstance(value, str):
                # Estrai solo la parte numerica (gestisce punti e virgole)
                clean_val = value.replace(' ', '').replace('€', '').replace('$', '').replace('EUR', '')
                if ',' in clean_val and '.' in clean_val:
                    # Probabile formato 1.234,56
                    clean_val = clean_val.replace('.', '').replace(',', '.')
                elif ',' in clean_val:
                    # Probabile formato 1234,56
                    clean_val = clean_val.replace(',', '.')
                
                import re
                nums = re.findall(r"[-+]?\d*\.\d+|\d+", clean_val)
                if nums:
                    val = float(nums[0])
                else:
                    return value
            else:
                val = float(value or 0)
            
            # Formato migliaia con punto e decimali con virgola
            formatted = "{:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")
            result = f"€ {formatted}"
            
            if paese and paese.lower() != 'italia':
                # Tasso di cambio indicativo per demo
                val_usd = val * 1.08 
                formatted_usd = "{:,.2f}".format(val_usd).replace(",", "X").replace(".", ",").replace("X", ".")
                result += f" / $ {formatted_usd}"
            return result
        except Exception:
            return value
    return app
