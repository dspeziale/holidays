"""
Generatore di dati demo per Roma Lusso Travel.
Crea clienti, tour, esperienze e fornitori con dati realistici.
"""
import random
import string
from datetime import date, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.models.cliente import Cliente
from app.models.tour import Tour
from app.models.esperienza import Esperienza
from app.models.fornitore import Fornitore
from app.models.pacchetto import Pacchetto
from app.models.viaggio import Viaggio
from app.utils.decorators import admin_required

demo_bp = Blueprint('demo', __name__, url_prefix='/demo')

# ── Dati per clienti ──────────────────────────────────────────────────────────

_CLIENTI = [
    # (nome, cognome, nazionalita, paese, citta, cap, prefisso_tel, dominio_email)
    ('Marco', 'Rossi', 'Italiana', 'Italia', 'Roma', '00100', '+39 06', 'gmail.com'),
    ('Giulia', 'Ferrari', 'Italiana', 'Italia', 'Milano', '20121', '+39 02', 'libero.it'),
    ('Luca', 'Bianchi', 'Italiana', 'Italia', 'Firenze', '50100', '+39 055', 'hotmail.it'),
    ('Sofia', 'Conti', 'Italiana', 'Italia', 'Napoli', '80100', '+39 081', 'icloud.com'),
    ('Alessandro', 'Ricci', 'Italiana', 'Italia', 'Torino', '10100', '+39 011', 'yahoo.it'),
    ('Francesca', 'Marino', 'Italiana', 'Italia', 'Bologna', '40100', '+39 051', 'gmail.com'),
    ('Matteo', 'Greco', 'Italiana', 'Italia', 'Venezia', '30100', '+39 041', 'gmail.com'),
    ('Valentina', 'Bruno', 'Italiana', 'Italia', 'Palermo', '90100', '+39 091', 'virgilio.it'),
    ('Davide', 'Lombardi', 'Italiana', 'Italia', 'Bari', '70100', '+39 080', 'gmail.com'),
    ('Chiara', 'Esposito', 'Italiana', 'Italia', 'Genova', '16100', '+39 010', 'hotmail.it'),
    # Inglesi
    ('James', 'Smith', 'Britannica', 'Regno Unito', 'London', 'SW1A 1AA', '+44 20', 'gmail.com'),
    ('Emily', 'Johnson', 'Britannica', 'Regno Unito', 'Manchester', 'M1 1AE', '+44 161', 'outlook.com'),
    ('Oliver', 'Williams', 'Britannica', 'Regno Unito', 'Edinburgh', 'EH1 1YZ', '+44 131', 'gmail.com'),
    ('Sophie', 'Brown', 'Britannica', 'Regno Unito', 'Birmingham', 'B1 1BB', '+44 121', 'yahoo.co.uk'),
    # Tedeschi
    ('Hans', 'Müller', 'Tedesca', 'Germania', 'Berlin', '10115', '+49 30', 'gmail.com'),
    ('Sabine', 'Schmidt', 'Tedesca', 'Germania', 'München', '80331', '+49 89', 'web.de'),
    ('Klaus', 'Wagner', 'Tedesca', 'Germania', 'Hamburg', '20095', '+49 40', 'gmx.de'),
    # Francesi
    ('Pierre', 'Dubois', 'Francese', 'Francia', 'Paris', '75001', '+33 1', 'gmail.com'),
    ('Marie', 'Laurent', 'Francese', 'Francia', 'Lyon', '69001', '+33 4', 'laposte.net'),
    ('Jean', 'Martin', 'Francese', 'Francia', 'Marseille', '13001', '+33 4', 'orange.fr'),
    # Americani
    ('Michael', 'Anderson', 'Statunitense', 'USA', 'New York', 'NY 10001', '+1 212', 'gmail.com'),
    ('Jennifer', 'Davis', 'Statunitense', 'USA', 'Los Angeles', 'CA 90001', '+1 310', 'yahoo.com'),
    ('Robert', 'Wilson', 'Statunitense', 'USA', 'Chicago', 'IL 60601', '+1 312', 'outlook.com'),
    # Spagnoli
    ('Carlos', 'García', 'Spagnola', 'Spagna', 'Madrid', '28001', '+34 91', 'gmail.com'),
    ('Ana', 'Martínez', 'Spagnola', 'Spagna', 'Barcelona', '08001', '+34 93', 'hotmail.es'),
    # Russi
    ('Александр', 'Иванов', 'Russa', 'Russia', 'Mosca', '101000', '+7 495', 'mail.ru'),
    ('Елена', 'Смирнова', 'Russa', 'Russia', 'San Pietroburgo', '190000', '+7 812', 'yandex.ru'),
    # Giapponesi
    ('Kenji', 'Tanaka', 'Giapponese', 'Giappone', 'Tokyo', '100-0001', '+81 3', 'gmail.com'),
    ('Yuki', 'Yamamoto', 'Giapponese', 'Giappone', 'Osaka', '530-0001', '+81 6', 'yahoo.co.jp'),
    # Arabi
    ('Mohammed', 'Al-Rashid', 'Emiratina', 'UAE', 'Dubai', '00000', '+971 4', 'gmail.com'),
    ('Fatima', 'Al-Mansouri', 'Emiratina', 'UAE', 'Abu Dhabi', '00000', '+971 2', 'hotmail.com'),
    # Brasiliani
    ('Carlos', 'Silva', 'Brasiliana', 'Brasile', 'São Paulo', '01310-100', '+55 11', 'gmail.com'),
    ('Ana', 'Oliveira', 'Brasiliana', 'Brasile', 'Rio de Janeiro', '20040-020', '+55 21', 'hotmail.com'),
    # Cinesi
    ('Wei', 'Zhang', 'Cinese', 'Cina', 'Shanghai', '200001', '+86 21', 'qq.com'),
    ('Mei', 'Li', 'Cinese', 'Cina', 'Beijing', '100000', '+86 10', 'gmail.com'),
    # Australiani
    ('Liam', 'Wilson', 'Australiana', 'Australia', 'Sydney', 'NSW 2000', '+61 2', 'gmail.com'),
    ('Emma', 'Taylor', 'Australiana', 'Australia', 'Melbourne', 'VIC 3000', '+61 3', 'hotmail.com'),
    # Svizzeri
    ('Hans', 'Keller', 'Svizzera', 'Svizzera', 'Zürich', '8001', '+41 44', 'gmx.ch'),
    ('Isabelle', 'Favre', 'Svizzera', 'Svizzera', 'Genève', '1200', '+41 22', 'gmail.com'),
    # Olandesi
    ('Jan', 'de Vries', 'Olandese', 'Paesi Bassi', 'Amsterdam', '1011 AB', '+31 20', 'gmail.com'),
    ('Anna', 'van Dijk', 'Olandese', 'Paesi Bassi', 'Rotterdam', '3011 AA', '+31 10', 'hotmail.nl'),
    # Svedesi
    ('Erik', 'Svensson', 'Svedese', 'Svezia', 'Stockholm', '111 20', '+46 8', 'gmail.com'),
    # Belgi
    ('Thomas', 'Dupont', 'Belga', 'Belgio', 'Bruxelles', '1000', '+32 2', 'gmail.com'),
    # Portoghesi
    ('João', 'Ferreira', 'Portoghese', 'Portogallo', 'Lisboa', '1100-148', '+351 21', 'gmail.com'),
    # Greci
    ('Nikos', 'Papadopoulos', 'Greca', 'Grecia', 'Atene', '105 57', '+30 21', 'gmail.com'),
    # Polacchi
    ('Piotr', 'Kowalski', 'Polacca', 'Polonia', 'Warszawa', '00-001', '+48 22', 'gmail.com'),
    # Turchi
    ('Ahmet', 'Yilmaz', 'Turca', 'Turchia', 'Istanbul', '34000', '+90 212', 'gmail.com'),
    # Indiani
    ('Raj', 'Sharma', 'Indiana', 'India', 'Mumbai', '400001', '+91 22', 'gmail.com'),
    ('Priya', 'Patel', 'Indiana', 'India', 'New Delhi', '110001', '+91 11', 'yahoo.in'),
    # Canadesi
    ('David', 'Thompson', 'Canadese', 'Canada', 'Toronto', 'M5H 2N2', '+1 416', 'gmail.com'),
]

_LINGUE = {
    'Italiana': 'Italiano', 'Britannica': 'Inglese', 'Tedesca': 'Tedesco',
    'Francese': 'Francese', 'Statunitense': 'Inglese', 'Spagnola': 'Spagnolo',
    'Russa': 'Russo', 'Giapponese': 'Giapponese', 'Emiratina': 'Arabo',
    'Brasiliana': 'Portoghese', 'Cinese': 'Cinese', 'Australiana': 'Inglese',
    'Svizzera': 'Tedesco', 'Olandese': 'Olandese', 'Svedese': 'Svedese',
    'Belga': 'Francese', 'Portoghese': 'Portoghese', 'Greca': 'Greco',
    'Polacca': 'Polacco', 'Turca': 'Turco', 'Indiana': 'Hindi', 'Canadese': 'Inglese',
}

_INDIRIZZI = [
    'Via Roma', 'Via Garibaldi', 'Corso Italia', 'Via Mazzini', 'Piazza Navona',
    'Via Nazionale', 'Corso Vittorio Emanuele', 'Via del Corso', 'Via Veneto',
    'Via Cola di Rienzo', 'Via Appia Antica', 'Via Giulia', 'Lungarno Corsini',
]

_TIPI_DOC = ['Passaporto', 'Carta d\'identità', 'Passaporto']


def _rnd_doc():
    return ''.join(random.choices(string.ascii_uppercase, k=2)) + \
           ''.join(random.choices(string.digits, k=7))


def _rnd_date_nascita():
    start = date(1955, 1, 1)
    end = date(2000, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def _rnd_phone(prefix):
    return f'{prefix} {random.randint(100, 999)} {random.randint(1000, 9999)}'


# ── Dati per tour ─────────────────────────────────────────────────────────────

_TOURS = [
    # (nome, descrizione, destinazione, paese, categoria, giorni, prezzo_adulto, prezzo_bambino, capacita, incluso, escluso)
    ('Roma Imperiale — 5 giorni', 'Immergiti nella grandezza dell\'Impero Romano: Colosseo, Foro Romano, Palatino, Pantheon e Castel Sant\'Angelo con guide esperte e accesso prioritario.', 'Roma', 'Italia', 'Culturale', 5, 1290, 650, 15, 'Guide esperta, accesso prioritario siti, trasporti interni, 4 cene incluse', 'Voli, hotel, colazioni, pranzi'),
    ('Toscana del Vino e Sapori', 'Tour enogastronomico nelle colline del Chianti, Montalcino e Montepulciano con degustazioni nei migliori produttori, pranzi in agriturismo e visite a cantine storiche.', 'Firenze', 'Italia', 'Gastronomia', 6, 1850, 800, 12, 'Tutte le degustazioni, 3 pranzi in agriturismo, trasporti privati', 'Voli, hotel'),
    ('Costa Amalfitana in Barca', 'Esplora la Costiera Amalfitana a bordo di uno yacht privato: Positano, Ravello, Grotta Azzurra di Capri e spiagge nascoste accessibili solo via mare.', 'Napoli', 'Italia', 'Mare', 7, 3200, 1500, 8, 'Yacht privato, skipper, snorkel, 6 pranzi a bordo', 'Voli, hotel, cene'),
    ('Sicilia Barocca e Sapori', 'Catania, Siracusa, Agrigento e Taormina: barocco UNESCO, Valle dei Templi, mercati storici e cucina siciliana autentica con chef locale.', 'Catania', 'Italia', 'Culturale', 8, 1650, 750, 16, 'Guide, ingressi siti UNESCO, cooking class, 4 cene', 'Voli, hotel'),
    ('Dolomiti Trekking Lusso', 'Trekking guidato tra le Dolomiti patrimonio UNESCO con soste in rifugi d\'alta quota ristrutturati, spa alpina e cene gourmet con vista sulle vette.', 'Bolzano', 'Italia', 'Montagna', 7, 2400, 1100, 10, 'Guide alpine, rifugi lusso, spa, 6 cene gourmet, noleggio attrezzatura', 'Voli, trasporti'),
    ('Venezia e Laguna Segreta', 'Venezia oltre i canali principali: gite in gondola privata, visita a Murano e Burano, regata storica, cena in palazzo veneziano e tour notturno.', 'Venezia', 'Italia', 'Culturale', 4, 1450, 600, 12, 'Gondola privata, traghetti laguna, ingressi, 2 cene', 'Voli, hotel'),
    ('Safari Tanzania — Grand Tour', 'Serengeti, Ngorongoro e Kilimanjaro: 10 giorni tra i Big Five con lodge di lusso immersi nella savana, guide ranger locali e tramonto sulle praterie africane.', 'Arusha', 'Tanzania', 'Safari', 10, 6800, 4200, 8, 'Lodge lusso, jeep safari, guide ranger, voli interni, pension completa', 'Volo internazionale'),
    ('Giappone tra Tradizione e Futuro', 'Tokyo, Kyoto, Osaka e Hiroshima: tempio Fushimi Inari, geisha di Gion, cerimonia del tè, alta velocità su Shinkansen e cucina kaiseki nel miglior ristorante di Kyoto.', 'Tokyo', 'Giappone', 'Culturale', 12, 5400, 2800, 10, 'Hotel 5★, Shinkansen pass, guide locali, 8 cene, ingressi', 'Volo internazionale'),
    ('Maldive Private Island Experience', 'Villa overwater in resort privato, snorkeling sulla barriera corallina, diving, cena romantica sulla spiaggia e gita in catamarano al tramonto.', 'Malé', 'Maldive', 'Mare', 7, 7200, 3600, 6, 'Villa overwater, pension completa, diving, snorkeling, catamarano', 'Volo internazionale'),
    ('Grecia delle Isole — Cicladi', 'Santorini, Mykonos e Milos in catamarano privato: caldera, grotte di Kleftiko, spiagge di sabbia rosa e cene sul porto con vista sul tramonto più bello del mondo.', 'Atene', 'Grecia', 'Mare', 8, 3800, 1800, 8, 'Catamarano privato, skipper, colazioni a bordo, 3 cene', 'Voli, hotel primo/ultimo giorno'),
    ('Marocco Imperiale', 'Marrakech, Fes, Meknes e Chefchaouen: souk, palazzo della Bahia, tintorie di Fes, cena nel riad con musica gnawa e escursione nel deserto.', 'Marrakech', 'Marocco', 'Culturale', 9, 2100, 980, 14, 'Riad boutique, guide, camel trekking, 6 cene tradizionali, trasporti', 'Voli'),
    ('Norvegia — Aurore Boreali', 'Tromsø e Lofoten: whale watching, aurora boreale, kayak tra i fiordi ghiacciati, soggiorno in cabina di lusso con vista sul fiordo e cena a base di salmone.', 'Oslo', 'Norvegia', 'Avventura', 7, 4200, 2100, 8, 'Cabine lusso, whale watching, kayak, aurora tour, 5 cene', 'Voli'),
    ('Perù — Machu Picchu Luxury', 'Lima, Cusco e Machu Picchu: Hiram Bingham luxury train, accesso alba esclusive, degustazione pisco, cerimonia inca e lodge di alta quota con panorama mozzafiato.', 'Lima', 'Perù', 'Avventura', 10, 5200, 2600, 8, 'Hiram Bingham train, lodge lusso, guida locale, 8 pasti, ingressi', 'Voli'),
    ('Provenza e Côte d\'Azur', 'Nizza, Monaco, Cannes, Aix-en-Provence e Gordes: mercati di Provenza, degustazione rosé, Monaco in GT, Cannes fuori stagione e lavanda in fiore.', 'Nizza', 'Francia', 'Gastronomia', 6, 2600, 1200, 12, 'Hotel 4★, trasporti privati, degustazioni, 4 cene, guide', 'Voli'),
    ('New York — La Grande Mela VIP', 'Manhattan, Brooklyn, Hudson Valley: tour privato in limousine, accesso Top of the Rock, cena al Eleven Madison Park, Broadway show in prima fila.', 'New York', 'USA', 'Città', 5, 4800, 2400, 8, 'Hotel 5★ Times Square, limousine, cene 3★ Michelin, Broadway, guide', 'Voli'),
    ('Dubai — Lusso nel Deserto', 'Burj Khalifa, Desert Safari, Dubai Marina, Souk d\'oro, dhow cruise e cena nel ristorante al 123° piano con vista sulla città illuminata.', 'Dubai', 'UAE', 'Città', 5, 3600, 1800, 10, 'Hotel 5★, safari desert, dhow cruise, cena panoramica, transfers', 'Voli'),
    ('Umbria — Cuore Verde d\'Italia', 'Assisi, Perugia, Orvieto, Norcia e Spoleto: francescanesimo, tartufo nero, sagrantino di Montefalco, terme di Fontecchio e borghi medievali.', 'Perugia', 'Italia', 'Gastronomia', 5, 1380, 620, 14, 'Agriturismo 4★, guide, degustazioni tartufo, 4 cene, trasporti', 'Voli'),
    ('Puglia — Fascia Dorata', 'Alberobello, Ostuni, Lecce barocca, Otranto e Polignano a Mare: trulli UNESCO, barocco leccese, mare cristallino e cucina pugliese con chef stellato.', 'Bari', 'Italia', 'Culturale', 7, 1720, 780, 16, 'Masseria di charme, guide, cooking class, 5 cene, trasporti', 'Voli'),
    ('Islanda — Land of Fire and Ice', 'Ring Road islandese: Geysir, Gullfoss, Aurora Boreale, Blue Lagoon, glaciologi guida al Vatnajökull e cena nello chef\'s table islandese.', 'Reykjavík', 'Islanda', 'Avventura', 8, 4600, 2300, 8, 'Hotel boutique, jeep 4x4, Blue Lagoon, guide glaciologhe, 6 cene', 'Voli'),
    ('Bali — Spirito e Benessere', 'Ubud, Seminyak, Nusa Dua: cerimonia Hindu, rice terrace di Tegallalang, yoga al sorgere del sole, massaggi balinesi, tempio di Tanah Lot e sunset dinner.', 'Denpasar', 'Indonesia', 'Benessere', 9, 3100, 1550, 10, 'Villa privata con pool, massaggi giornalieri, yoga, guide, 7 cene', 'Voli'),
]

# ── Dati per esperienze ───────────────────────────────────────────────────────

_ESPERIENZE = [
    # (nome, descrizione, destinazione, paese, categoria, durata_ore, prezzo_adulto, prezzo_bambino, fornitore, punto_incontro, lingua)
    ('Tour del Colosseo con Accesso Arena', 'Visita guidata al Colosseo con accesso esclusivo all\'arena dove combattevano i gladiatori, Foro Romano e Palatino. Guida archeologa specializzata.', 'Roma', 'Italia', 'Arte & Cultura', 3.5, 85, 45, 'Roma Luxe Tours', 'Colosseo — Ingresso Via Sacra', 'Italiano'),
    ('Cena in Cantina con Sommelier', 'Cena esclusiva in una cantina storica del Chianti con degustazione di 6 vini abbinati a 5 portate di cucina toscana contemporanea guidata dal sommelier AIS.', 'Firenze', 'Italia', 'Food & Wine', 4.0, 145, 70, 'Cantina Castello del Nero', 'Piazza della Repubblica 1, Firenze', 'Italiano'),
    ('Snorkeling Grotta Azzurra Capri', 'Escursione privata in barca a Capri con snorkeling alla Grotta Azzurra e alle Grotte Bianche, pranzo a bordo con pesce fresco e visita alla Villa Jovis.', 'Napoli', 'Italia', 'Sport', 6.0, 180, 90, 'Blue Sea Capri', 'Porto di Napoli — Molo Beverello', 'Italiano'),
    ('Cooking Class Pasta Artigianale Roma', 'Impara a fare pasta fresca, cacio e pepe e tiramisù con una nonna romana nel suo appartamento al Trastevere. Include spesa al mercato di Campo de\' Fiori.', 'Roma', 'Italia', 'Food & Wine', 3.0, 95, 50, 'Nonna Italiana', 'Campo de\' Fiori — Fontana', 'Italiano'),
    ('E-Bike Tour Toscana tra Vigne', 'Pedalata in e-bike attraverso le colline del Chianti con soste nelle migliori cantine e un picnic gourmet in un campo di girasoli con vista su San Gimignano.', 'Siena', 'Italia', 'Sport', 5.0, 110, 60, 'Tuscany Bike Tours', 'Siena — Piazza del Campo', 'Italiano'),
    ('Visita Privata Musei Vaticani', 'Accesso all\'alba nei Musei Vaticani prima dell\'apertura al pubblico: Cappella Sistina senza folla, Stanze di Raffaello e Giardini Vaticani. Max 6 persone.', 'Roma', 'Italia', 'Arte & Cultura', 3.0, 220, 120, 'Vatican Private Tours', 'Musei Vaticani — Ingresso Viale Vaticano', 'Italiano'),
    ('Kayak Cinque Terre', 'Esplora le scogliere delle Cinque Terre in kayak: dalle grotte di Monterosso alle acque turchesi di Vernazza, con foto underwater e aperitivo in spiaggia privata.', 'La Spezia', 'Italia', 'Sport', 4.0, 75, 40, 'Liguria Sea Kayak', 'Monterosso al Mare — Spiaggia Nord', 'Italiano'),
    ('Degustazione Tartufo Norcia', 'Truffle hunting con i migliori tartufai di Norcia, degustazione di tartufo nero in tutti i piatti con abbinamento di vini Sagrantino, certificato di esperto tartufaio incluso.', 'Perugia', 'Italia', 'Food & Wine', 5.0, 165, 80, 'Tartufi Bianconi', 'Norcia — Piazza San Benedetto', 'Italiano'),
    ('Tour Notturno Roma a Piedi', 'Fontana di Trevi, Pantheon e Piazza Navona di notte: storie di fantasmi, misteri e leggende romane con storyteller professionista. Aperitivo finale in enoteca storica.', 'Roma', 'Italia', 'Arte & Cultura', 2.5, 55, 28, 'Roma Segreta Tours', 'Fontana di Trevi — Scalinata', 'Italiano'),
    ('Lezione di Pizza Napoletana DOC', 'Impara l\'arte del pizzaiolo napoletano certificato AVPN: impasto, stesura a mano e cottura nel forno a legna. Mangi la tua pizza e porti a casa il certificato.', 'Napoli', 'Italia', 'Food & Wine', 2.5, 65, 35, 'Pizzeria Sorbillo Academy', 'Napoli — Via dei Tribunali 32', 'Italiano'),
    ('Giro in Gondola Privata Venezia', 'Gita in gondola privata nei canali meno turistici di Venezia con gondoliere-cantante: Canal Grande, Canale della Giudecca e Rialto. Prosecco a bordo.', 'Venezia', 'Italia', 'Arte & Cultura', 1.0, 120, 60, 'Gondole Venezia Classic', 'San Marco — Bacino Orseolo', 'Italiano'),
    ('Safari Fotografico Serengeti', 'Game drive fotografico all\'alba con guida ranger e fotografo professionista: Big Five, gnu in migrazione e aquile pescatrici al tramonto. Include fotografie post-prodotte.', 'Arusha', 'Tanzania', 'Natura', 8.0, 320, 180, 'Serengeti Photo Safaris', 'Arusha Lodge — Main Lobby', 'Inglese'),
    ('Cerimonia del Tè a Kyoto', 'Cerimonia del tè tradizionale Ura Senke con maestra certificata in una casa da tè storica di Higashiyama. Indossare kimono, ikebana e visita al giardino zen.', 'Kyoto', 'Giappone', 'Arte & Cultura', 2.0, 95, 48, 'Higashiyama Tea House', 'Gion — Hanamikoji Street', 'Inglese'),
    ('Diving Barriera Corallina Maldive', 'Immersione guidata nella barriera corallina delle Maldive con istruttore PADI: mante giganti, tartarughe, barracuda e squali balena nel Blue Hole.', 'Malé', 'Maldive', 'Sport', 4.0, 140, 80, 'Maldives Dive Academy', 'Resort Jetty — Water Bungalow', 'Inglese'),
    ('Tour di Street Food Bangkok', 'Esplora i mercati notturni di Bangkok con guida food blogger: pad thai, mango sticky rice, scorpioni fritti e cena in un ristorante galleggiante sul Chao Phraya.', 'Bangkok', 'Thailandia', 'Food & Wine', 3.5, 55, 28, 'Bangkok Food Tours', 'Khao San Road — Main Entrance', 'Inglese'),
    ('Yoga al Sorgere del Sole Bali', 'Sessione di Hatha yoga all\'alba sulla terrazza di un tempio hindu a Ubud con vista sulle risaie, pranzo ayurvedico, meditazione e massaggio tradizionale balinese.', 'Denpasar', 'Indonesia', 'Benessere', 4.0, 85, 42, 'Ubud Spirit Wellness', 'Ubud — Rice Terrace Entrance', 'Inglese'),
    ('Crociera Tramonto Santorini', 'Crociera al tramonto sulla caldera di Santorini in catamarano: hot springs di Palea Kameni, grotte vulcaniche, bagno in acque termali e cena seafood con vista sul tramonto.', 'Santorini', 'Grecia', 'Mare', 5.5, 130, 65, 'Santorini Sailing', 'Athinios Port — Gate 3', 'Inglese'),
    ('Visita Fantasma Palazzo Medici', 'Tour serale esclusivo a Palazzo Medici Riccardi con accesso agli appartamenti privati non aperti al pubblico, ritratti segreti e il tesoro nascosto dei Medici.', 'Firenze', 'Italia', 'Arte & Cultura', 2.0, 75, 40, 'Florence Secret Tours', 'Palazzo Medici — Via Cavour 1', 'Italiano'),
    ('Massaggio Tradizionale Hammam Istanbul', 'Esperienza completa nell\'hammam ottomano del 1584: peeling con guanto di crine, sapone all\'olio d\'oliva, massaggio turco con ciotola di rame e tè alla menta.', 'Istanbul', 'Turchia', 'Benessere', 2.5, 70, 35, 'Çemberlitaş Hamamı', 'Çemberlitaş — Vezirhan Caddesi 8', 'Inglese'),
    ('Aurora Boreale in Slitta con Husky', 'Escursione serale su slitta trainata da husky a Tromsø in cerca dell\'aurora boreale, con vin brulé, grappa di Sami e cena in yurta tradizionale.', 'Tromsø', 'Norvegia', 'Natura', 4.0, 185, 95, 'Arctic Adventure Norway', 'Tromsø Harbor — Aurora Bus Stop', 'Inglese'),
    ('Surf Lezione Principianti Biarritz', 'Lezione di surf in acqua a Biarritz con istruttore federale FFSurf: teoria, sicurezza, esercizi a terra e prime onde sulla spiaggia di Côte des Basques.', 'Biarritz', 'Francia', 'Sport', 2.5, 65, 35, 'École de Surf Biarritz', 'Plage Côte des Basques — Entrée Nord', 'Francese'),
    ('Flamenco Show + Cena Sevilla', 'Spettacolo di flamenco autentico in tablao storico di Siviglia con cena andalusa: gazpacho, jamón ibérico pata negra, tortilla e cava durante lo show.', 'Siviglia', 'Spagna', 'Arte & Cultura', 3.0, 95, 48, 'Tablao El Arenal', 'Calle Rodo 7, Sevilla', 'Spagnolo'),
    ('Tour in Elicottero Dolomiti', 'Sorvolo delle Dolomiti in elicottero: Tre Cime di Lavaredo, Marmolada e Pale di San Martino con atterraggio su ghiacciaio e foto con lo skipper alpinista.', 'Bolzano', 'Italia', 'Avventura', 1.5, 380, 280, 'Dolomiti Helicopter', 'Aeroporto Bolzano — Terminal Charter', 'Italiano'),
    ('Vespa Tour Roma con Pranzo', 'Giro in Vespa d\'epoca per Roma: Trastevere, Gianicolo, EUR, Appia Antica e sosta all\'osteria storica per pranzo tipico romano con vino dei Castelli.', 'Roma', 'Italia', 'Arte & Cultura', 4.0, 120, 60, 'Vespa Roma Tours', 'Via Veneto 10 — Hotel Excelsior', 'Italiano'),
    ('Escursione Etna con Vulcanologo', 'Salita all\'Etna con guida vulcanologa: crateri sommitali, colate laviche del 2021, cantine dell\'Etna DOC e degustazione di Nerello Mascalese con vista sul mare.', 'Catania', 'Italia', 'Natura', 7.0, 140, 70, 'Etna Experts', 'Catania — Piazza Stesicoro', 'Italiano'),
]

# ── Dati per fornitori ────────────────────────────────────────────────────────

_FORNITORI = [
    # (nome, tipo_servizio, contatto_nome, email, telefono, indirizzo, sito_web, piva, note)
    ('Grand Hotel Villa Medici', 'Hotel', 'Marco Pellegrini', 'reservations@villamedici.it', '+39 055 2381331', 'Via il Prato 42, 50123 Firenze', 'www.grandhotelvillamedici.com', 'IT04521380481', 'Hotel 5★ centro Firenze. Contratto prenotazioni dirette. Commissione 12%.'),
    ('Alitalia Cargo & Charter', 'Voli', 'Valentina Rosso', 'charter@alitalia.com', '+39 06 65621', 'Via Cristoforo Colombo 40, 00147 Roma', 'www.alitalia.com', 'IT04700851005', 'Contratto charter per gruppi. Sconto gruppi 10+ pax: 15%.'),
    ('Blue Limousine Roma', 'Transfer', 'Giuseppe Ferrante', 'booking@bluelimousineroma.it', '+39 06 4746789', 'Via Nomentana 12, 00162 Roma', 'www.bluelimousineroma.it', 'IT09823410583', 'Flotta: Mercedes S-Class, Sprinter, minibus 18 pax. Disponibile H24.'),
    ('Hertz Italia Corporate', 'Noleggio Auto', 'Sara Monti', 'corporate@hertz.it', '+39 02 69683300', 'Via Pirelli 10, 20124 Milano', 'www.hertz.it', 'IT03592790581', 'Contratto corporate. Flotta premium: Porsche Macan, Maserati, Range Rover. Sconto 20%.'),
    ('Tours & Travels Srl', 'Tour Operator', 'Andrea Caruso', 'info@tourstravel.it', '+39 06 8412031', 'Via della Mercede 52, 00187 Roma', 'IT01823410589', 'www.tourstravel.it', 'TO regolare. Guide multilingue. Specializzato in tour culturali Italia.'),
    ('African Safari Luxury', 'Tour Operator', 'John Mbeki', 'booking@africansafariluxury.com', '+254 20 4451234', 'Kimathi Street 42, Nairobi, Kenya', 'www.africansafariluxury.com', '', 'Partner Africa orientale. Lodge lusso Serengeti, Masai Mara, Ngorongoro. Esclusiva Italia.'),
    ('Japan Private Tours Co.', 'Tour Operator', 'Yuki Nakamura', 'info@japanprivatetours.jp', '+81 3 6432 1100', 'Shibuya 2-chome 21, Tokyo 150-0002', 'www.japanprivatetours.jp', '', 'Guide locali giapponesi certificati. Tour esclusivi max 6 persone.'),
    ('Ristorante La Pergola', 'Ristorazione', 'Chef Heinz Beck', 'info@romecavalieri.com', '+39 06 35092152', 'Via Alberto Cadlolo 101, 00136 Roma', 'www.romecavalieri.com', 'IT01234567891', '3 stelle Michelin. Cene di gala, private dining. Prenotazione min 48h.'),
    ('Sommelier Experience Toscana', 'Enogastronomia', 'Paola Neri', 'info@sommelierexperience.it', '+39 0577 841243', 'Loc. Vagliagli, 53010 Castelnuovo Berardenga SI', 'www.sommelierexperience.it', 'IT01765430521', 'Cantine partner: Antinori, Frescobaldi, Mazzei. Degustazioni personalizzate.'),
    ('Maldives Resorts Collection', 'Hotel', 'Aisha Rasheed', 'partnerships@maldivesresorts.com', '+960 330 8800', 'Boduthakurufaanu Magu, Male 20062', 'www.maldivesresorts.com', '', 'Resorts partner: One&Only Reethi Rah, Soneva Fushi, Six Senses Laamu. Commissione 10%.'),
    ('Elicotteri Italia Srl', 'Transfer Aereo', 'Roberto Masini', 'charter@elicotteriitalia.it', '+39 02 40090221', 'Aeroporto Bresso, Via Gerenzano 13, 20020 Milano', 'www.elicotteriitalia.it', 'IT07432190155', 'Helicopter charter. Agusta AW139, EC145. Operativo in tutta Italia.'),
    ('Trenitalia Business Travel', 'Ferroviario', 'Claudia Mantovani', 'business@trenitalia.com', '+39 06 68475475', 'Piazza della Croce Rossa 1, 00161 Roma', 'www.trenitalia.com', 'IT05403151003', 'Frecciarossa, Frecciargento. Contratto corporate. Carrozze riservate per gruppi.'),
    ('Costa Crociere — Charter', 'Crociere', 'Massimiliano Pino', 'charter@costagroup.com', '+39 010 5483248', 'Via XII Ottobre 2, 16121 Genova', 'www.costa.it', 'IT03561540107', 'Charter nave intera o ponti. Mediterraneo, Caraibi, Sudamerica.'),
    ('Private Yacht Roma Med', 'Noleggio Barche', 'Filippo Savoia', 'info@privateyachtromamed.it', '+39 081 7641980', 'Via Caracciolo 28, 80121 Napoli', 'www.privateyachtromamed.it', 'IT08341290635', 'Flotta: Sunseeker 75, Azimut 68, catamarani Lagoon 52. Skipper incluso.'),
    ('Relais Villa Falconieri', 'Hotel', 'Contessa Laura Falconieri', 'reservations@villafalconieri.it', '+39 06 9415906', 'Via del Tuscolo 8, 00044 Frascati Roma', 'www.villafalconieri.it', 'IT02341890589', 'Dimora storica 5★L Relais & Châteaux. Capacità max 30 ospiti. Ideal per eventi privati.'),
    ('InfraRail Europe BV', 'Ferroviario', 'Erik van den Berg', 'charter@infraraileuro.com', '+31 20 5551234', 'Stationsplein 3, 1012 AB Amsterdam', 'www.infraraileuro.com', '', 'Treni charter Europa: Orient Express replica, Flam Railway, Bernina Express. Prenotazione min 3 mesi.'),
    ('Arabian Nights DMC', 'Tour Operator', 'Khalid Al Rashid', 'info@arabianightsdmc.com', '+971 4 3591234', 'Sheikh Zayed Road, Dubai Media City', 'www.arabianightsdmc.com', '', 'DMC UAE, Oman, Arabia Saudita. Desert safari, dhow cruise, palazzo privato.'),
    ('Wellness & Spa Collection Italia', 'Benessere', 'Dott.ssa Elisa Fontana', 'booking@wellnesscollection.it', '+39 0471 909000', 'Via Cassa di Risparmio 58, 39100 Bolzano', 'www.wellnesscollection.it', 'IT02341670211', 'Network 40 spa di lusso in Italia. Programmi detox, ayurveda, beauty.'),
    ('Photo & Film Location Italy', 'Servizi Creativi', 'Matteo Caravaggio', 'info@photolocationitaly.it', '+39 06 32650044', 'Via Margutta 51, 00187 Roma', 'www.photolocationitaly.it', 'IT09234560587', 'Location scouting, fotografi professionisti, videografia travel. Portfolio su richiesta.'),
    ('GreenGo Travel Incoming', 'Tour Operator', 'Federico Conti', 'incoming@greengotravel.it', '+39 051 4212300', 'Piazza Maggiore 6, 40124 Bologna', 'www.greengotravel.it', 'IT03892310376', 'Specializzato incoming da USA, Canada, Australia. Guide in inglese. Ricevitivo lusso.'),
]


def _random_unique_email(nome, cognome, dominio, usati):
    """Genera un\'email unica."""
    base = f'{nome.lower().replace(" ", "").replace("\'", "")}.{cognome.lower().replace(" ", "").replace("\'", "")}'
    import unicodedata
    base = unicodedata.normalize('NFKD', base).encode('ascii', 'ignore').decode('ascii')
    email = f'{base}@{dominio}'
    # Se già usata, aggiungi numero
    if email in usati:
        for i in range(2, 100):
            candidate = f'{base}{i}@{dominio}'
            if candidate not in usati:
                email = candidate
                break
    usati.add(email)
    return email


# ── Route ─────────────────────────────────────────────────────────────────────

@demo_bp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    if request.method == 'POST':
        n_clienti    = max(1, min(int(request.form.get('n_clienti',    10)), 50))
        n_tours      = max(1, min(int(request.form.get('n_tours',       5)), 20))
        n_esperienze = max(1, min(int(request.form.get('n_esperienze',  5)), 20))
        n_fornitori  = max(1, min(int(request.form.get('n_fornitori',   5)), 20))

        contatori = {'clienti': 0, 'tours': 0, 'esperienze': 0, 'fornitori': 0, 'duplicati': 0}

        # ── Dati esistenti per evitare duplicati ──
        email_usate = set(e[0] for e in db.session.execute(db.select(Cliente.email)).all())
        nomi_clienti_usati = set(f"{c[0]} {c[1]}".lower() for c in db.session.execute(db.select(Cliente.nome, Cliente.cognome)).all())
        nomi_tours_usati = set(t[0].lower() for t in db.session.execute(db.select(Tour.nome)).all())
        nomi_esp_usate = set(e[0].lower() for e in db.session.execute(db.select(Esperienza.nome)).all())

        # ── Clienti ───────────────────────────────────────────────────────────
        campioni = random.sample(_CLIENTI, min(n_clienti, len(_CLIENTI)))
        if n_clienti > len(_CLIENTI):
            campioni += random.choices(_CLIENTI, k=n_clienti - len(_CLIENTI))

        for c_data in campioni:
            nome, cognome, naz, paese, citta, cap, tel_prefix, dominio = c_data
            
            # Controllo duplicato per nome e cognome
            full_name = f"{nome} {cognome}".lower()
            if full_name in nomi_clienti_usati:
                contatori['duplicati'] += 1
                continue
                
            email = _random_unique_email(nome, cognome, dominio, email_usate)
            nascita = _rnd_date_nascita()
            rilascio = date(nascita.year + 18, random.randint(1, 12), random.randint(1, 28))
            # Data scadenza fissa al 2027 come richiesto
            scadenza = date(2027, 12, 31)
            tipo_doc = random.choice(_TIPI_DOC)
            indirizzo = f'{random.choice(_INDIRIZZI)}, {random.randint(1, 200)}'

            cliente = Cliente(
                nome=nome,
                cognome=cognome,
                email=email,
                telefono=_rnd_phone(tel_prefix),
                data_nascita=nascita,
                nazionalita=naz,
                tipo_documento=tipo_doc,
                numero_documento=_rnd_doc(),
                data_rilascio_documento=rilascio,
                data_scadenza_documento=scadenza,
                indirizzo=indirizzo,
                citta=citta,
                cap=cap,
                paese=paese,
                lingua_preferita=_LINGUE.get(naz, 'Italiano'),
                attivo=True,
                is_demo=True,
            )
            db.session.add(cliente)
            nomi_clienti_usati.add(full_name) # Evita duplicati nello stesso loop
            contatori['clienti'] += 1

        # ── Tour ──────────────────────────────────────────────────────────────
        campioni_tour = random.sample(_TOURS, min(n_tours, len(_TOURS)))
        if n_tours > len(_TOURS):
            campioni_tour += random.choices(_TOURS, k=n_tours - len(_TOURS))

        for t_data in campioni_tour:
            nome, desc, dest, paese, cat, giorni, p_adulto, p_bambino, cap_max, incluso, escluso = t_data
            
            # Controllo duplicato per nome tour
            if nome.lower() in nomi_tours_usati:
                contatori['duplicati'] += 1
                continue
                
            tour = Tour(
                nome=nome,
                descrizione=desc,
                destinazione=dest,
                paese=paese,
                categoria=cat,
                durata_giorni=giorni,
                prezzo_adulto=p_adulto,
                prezzo_bambino=p_bambino,
                capacita_max=cap_max,
                incluso=incluso,
                escluso=escluso,
                attivo=True,
                is_demo=True,
            )
            db.session.add(tour)
            nomi_tours_usati.add(nome.lower())
            contatori['tours'] += 1

        # ── Esperienze ────────────────────────────────────────────────────────
        campioni_esp = random.sample(_ESPERIENZE, min(n_esperienze, len(_ESPERIENZE)))
        if n_esperienze > len(_ESPERIENZE):
            campioni_esp += random.choices(_ESPERIENZE, k=n_esperienze - len(_ESPERIENZE))

        for e_data in campioni_esp:
            nome, desc, dest, paese, cat, durata, p_adulto, p_bambino, fornitore, punto, lingua = e_data
            
            # Controllo duplicato per nome esperienza
            if nome.lower() in nomi_esp_usate:
                contatori['duplicati'] += 1
                continue
                
            esp = Esperienza(
                nome=nome,
                descrizione=desc,
                destinazione=dest,
                paese=paese,
                categoria=cat,
                durata_ore=durata,
                prezzo_adulto=p_adulto,
                prezzo_bambino=p_bambino,
                fornitore=fornitore,
                punto_incontro=punto,
                lingua=lingua,
                attivo=True,
                is_demo=True,
            )
            db.session.add(esp)
            nomi_esp_usate.add(nome.lower())
            contatori['esperienze'] += 1

        # ── Fornitori ─────────────────────────────────────────────────────────
        campioni_for = random.sample(_FORNITORI, min(n_fornitori, len(_FORNITORI)))
        if n_fornitori > len(_FORNITORI):
            campioni_for += random.choices(_FORNITORI, k=n_fornitori - len(_FORNITORI))

        for f_data in campioni_for:
            nome, tipo, contatto, email, tel, indirizzo, sito, piva, note = f_data
            # Controlla duplicato per nome
            esiste = db.session.execute(
                db.select(Fornitore).where(Fornitore.nome == nome)
            ).scalar_one_or_none()
            if esiste:
                contatori['duplicati'] += 1
                continue
            forn = Fornitore(
                nome=nome,
                tipo_servizio=tipo,
                contatto_nome=contatto,
                email=email,
                telefono=tel,
                indirizzo=indirizzo,
                sito_web=sito,
                piva_codfisc=piva,
                note=note,
                attivo=True,
                is_demo=True,
            )
            db.session.add(forn)
            contatori['fornitori'] += 1

        db.session.commit()

        msg_parts = []
        if contatori['clienti']:    msg_parts.append(f"{contatori['clienti']} clienti")
        if contatori['tours']:      msg_parts.append(f"{contatori['tours']} tour")
        if contatori['esperienze']: msg_parts.append(f"{contatori['esperienze']} esperienze")
        if contatori['fornitori']:  msg_parts.append(f"{contatori['fornitori']} fornitori")
        msg = 'Creati: ' + ', '.join(msg_parts) + '.'
        if contatori['duplicati']:
            msg += f' ({contatori["duplicati"]} record saltati perché già presenti.)'
        flash(msg, 'success')
        return redirect(url_for('demo.index'))

    # Statistiche attuali
    stats = {
        'clienti':    Cliente.query.count(),
        'tours':      Tour.query.count(),
        'esperienze': Esperienza.query.count(),
        'fornitori':  Fornitore.query.count(),
    }
    max_clienti    = len(_CLIENTI)
    max_tours      = len(_TOURS)
    max_esperienze = len(_ESPERIENZE)
    max_fornitori  = len(_FORNITORI)

    return render_template('demo/index.html',
                           stats=stats,
                           max_clienti=max_clienti,
                           max_tours=max_tours,
                           max_esperienze=max_esperienze,
                           max_fornitori=max_fornitori)


@demo_bp.route('/delete', methods=['POST'])
@login_required
@admin_required
def delete_demo():
    """Elimina tutti i dati contrassegnati come demo."""
    try:
        # Recuperiamo gli ID dei dati demo per pulire le tabelle associative
        demo_viaggi_ids = [v.id for v in db.session.query(Viaggio.id).filter(Viaggio.is_demo == True).all()]
        demo_pacchetti_ids = [p.id for p in db.session.query(Pacchetto.id).filter(Pacchetto.is_demo == True).all()]
        
        # 1. Pulizia tabelle associative (many-to-many)
        if demo_viaggi_ids:
            db.session.execute(text("DELETE FROM viaggio_tours WHERE viaggio_id IN :ids"), {"ids": tuple(demo_viaggi_ids)})
            db.session.execute(text("DELETE FROM viaggio_esperienze WHERE viaggio_id IN :ids"), {"ids": tuple(demo_viaggi_ids)})
            db.session.execute(text("DELETE FROM viaggio_partecipanti WHERE viaggio_id IN :ids"), {"ids": tuple(demo_viaggi_ids)})
        
        if demo_pacchetti_ids:
            db.session.execute(text("DELETE FROM pacchetto_tours WHERE pacchetto_id IN :ids"), {"ids": tuple(demo_pacchetti_ids)})
            db.session.execute(text("DELETE FROM pacchetto_esperienze WHERE pacchetto_id IN :ids"), {"ids": tuple(demo_pacchetti_ids)})

        # 2. Eliminazione dati principali
        # Ordine di eliminazione per gestire vincoli di integrità
        n_viaggi = db.session.query(Viaggio).filter(Viaggio.is_demo == True).delete(synchronize_session=False)
        n_pacchetti = db.session.query(Pacchetto).filter(Pacchetto.is_demo == True).delete(synchronize_session=False)
        n_clienti = db.session.query(Cliente).filter(Cliente.is_demo == True).delete(synchronize_session=False)
        n_tours = db.session.query(Tour).filter(Tour.is_demo == True).delete(synchronize_session=False)
        n_esperienze = db.session.query(Esperienza).filter(Esperienza.is_demo == True).delete(synchronize_session=False)
        n_fornitori = db.session.query(Fornitore).filter(Fornitore.is_demo == True).delete(synchronize_session=False)
        
        db.session.commit()
        
        msg = f"Dati demo eliminati con successo: {n_clienti} clienti, {n_tours} tour, {n_esperienze} esperienze, {n_fornitori} fornitori, {n_viaggi} viaggi, {n_pacchetti} pacchetti."
        flash(msg, 'success')
    except Exception as e:
        db.session.rollback()
        # Log dell'errore per debug
        print(f"DEBUG DELETE ERROR: {str(e)}")
        flash(f"Errore durante l'eliminazione dei dati demo: {str(e)}", 'danger')
        
    return redirect(url_for('demo.index'))
