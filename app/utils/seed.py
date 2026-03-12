from app import db
from app.models.user import User
from app.models.tour import Tour
from app.models.esperienza import Esperienza
from app.models.pacchetto import Pacchetto


def seed_admin():
    """Crea l'utente admin se non esiste."""
    if User.query.filter_by(email='admin@romalusso.it').first():
        return

    admin = User(
        username='admin',
        email='admin@romalusso.it',
        role='admin',
        attivo=True
    )
    admin.set_password('admin123')
    db.session.add(admin)

    # Dati demo
    _seed_demo()

    db.session.commit()
    print('[SEED] Admin creato: admin@romalusso.it / admin123')


def _seed_demo():
    """Inserisce dati demo se tabelle vuote."""
    if Tour.query.count() > 0:
        return

    tours = [
        Tour(
            nome='Tour dei Fori Imperiali',
            descrizione='Visita guidata ai Fori Imperiali e al Colosseo con guida esperta.',
            destinazione='Roma',
            paese='Italia',
            categoria='Culturale',
            durata_giorni=1,
            prezzo_adulto=85.00,
            prezzo_bambino=45.00,
            capacita_max=15,
            incluso='Guida certificata, accesso prioritario Colosseo, auricolari',
            attivo=True,
            is_demo=True
        ),
        Tour(
            nome='Tour della Costiera Amalfitana',
            descrizione='Escursione di 3 giorni lungo la splendida Costiera Amalfitana.',
            destinazione='Amalfi',
            paese='Italia',
            categoria='Mare',
            durata_giorni=3,
            prezzo_adulto=420.00,
            prezzo_bambino=280.00,
            capacita_max=20,
            incluso='Trasporti, 2 notti hotel 4★, colazioni, guida',
            attivo=True,
            is_demo=True
        ),
        Tour(
            nome='Wine Tour Toscana',
            descrizione='Tour enogastronomico nelle cantine del Chianti e della Val d\'Orcia.',
            destinazione='Firenze',
            paese='Italia',
            categoria='Gastronomia',
            durata_giorni=2,
            prezzo_adulto=320.00,
            prezzo_bambino=0.00,
            capacita_max=12,
            incluso='Degustazioni in 4 cantine, pranzo tipico, transfer da Firenze',
            attivo=True,
            is_demo=True
        ),
    ]

    esperienze = [
        Esperienza(
            nome='Degustazione pasta fresca romana',
            descrizione='Corso pratico di pasta fresca con chef locale nel cuore di Roma.',
            destinazione='Roma',
            paese='Italia',
            categoria='Food & Wine',
            durata_ore=3.0,
            prezzo_adulto=95.00,
            prezzo_bambino=65.00,
            fornitore='Cucina Romana SRL',
            lingua='Italiano/Inglese',
            attivo=True,
            is_demo=True
        ),
        Esperienza(
            nome='Tour notturno del Vaticano',
            descrizione='Visita esclusiva ai Musei Vaticani di notte, senza folla.',
            destinazione='Roma',
            paese='Italia',
            categoria='Arte & Cultura',
            durata_ore=3.5,
            prezzo_adulto=130.00,
            prezzo_bambino=85.00,
            fornitore='Vatican Tours',
            lingua='Italiano',
            attivo=True,
            is_demo=True
        ),
        Esperienza(
            nome='Kayak sul Lago di Como',
            descrizione='Escursione in kayak sulle acque cristalline del Lago di Como.',
            destinazione='Como',
            paese='Italia',
            categoria='Sport',
            durata_ore=4.0,
            prezzo_adulto=75.00,
            prezzo_bambino=50.00,
            fornitore='Lake Adventures',
            lingua='Italiano/Inglese',
            attivo=True,
            is_demo=True
        ),
    ]

    for t in tours:
        db.session.add(t)
    for e in esperienze:
        db.session.add(e)

    # Pacchetti demo
    p1 = Pacchetto(
        nome='Roma Classica',
        descrizione='Il meglio di Roma: storia, arte e cucina in un unico pacchetto.',
        destinazione='Roma',
        durata_giorni=3,
        prezzo_base=150.00,
        prezzo_adulto=370.00,
        prezzo_bambino=240.00,
        include_hotel=True,
        attivo=True,
        is_demo=True
    )
    p1.tours.append(tours[0])
    p1.esperienze.append(esperienze[0])
    p1.esperienze.append(esperienze[1])

    p2 = Pacchetto(
        nome='Toscana Gourmet',
        descrizione='Tour enogastronomico tra le cantine del Chianti con esperienza di pasta fresca.',
        destinazione='Firenze',
        durata_giorni=4,
        prezzo_base=200.00,
        prezzo_adulto=615.00,
        prezzo_bambino=345.00,
        include_volo=True,
        include_hotel=True,
        include_auto=True,
        attivo=True,
        is_demo=True
    )
    p2.tours.append(tours[2])
    p2.esperienze.append(esperienze[0])

    p3 = Pacchetto(
        nome='Weekend Costiera Amalfitana',
        descrizione='Tre giorni di relax e bellezza sulla Costiera Amalfitana.',
        destinazione='Amalfi',
        durata_giorni=3,
        prezzo_base=100.00,
        prezzo_adulto=520.00,
        prezzo_bambino=330.00,
        include_hotel=True,
        include_auto=True,
        attivo=True,
        is_demo=True
    )
    p3.tours.append(tours[1])
    p3.esperienze.append(esperienze[2])

    db.session.add_all([p1, p2, p3])
