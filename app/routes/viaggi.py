from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.viaggio import Viaggio

viaggi_bp = Blueprint('viaggi', __name__, url_prefix='/viaggi')




def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources on the disk.
    """
    import os
    from flask import current_app
    
    if not uri:
        return ""
        
    static_url = current_app.static_url_path or '/static'
    uri_clean = uri.split('?')[0]
    
    if uri_clean.startswith(static_url):
        relative_path = uri_clean.replace(static_url, '', 1).lstrip('/')
        path = os.path.join(current_app.static_folder, relative_path)
    else:
        path = os.path.join(current_app.root_path, uri_clean.lstrip('/'))
        
    if not os.path.isfile(path):
        path = os.path.join(current_app.static_folder, uri_clean.lstrip('/'))
        
    if os.path.isfile(path):
        return os.path.abspath(path)
        
    return uri


@viaggi_bp.route('/')
@login_required
def index():
    viaggi = Viaggio.query.order_by(Viaggio.created_at.desc()).all()
    return render_template('viaggi/index.html', viaggi=viaggi)


@viaggi_bp.route('/<int:id>')
@login_required
def detail(id):
    from app.models.cliente import Cliente
    from app.models.tour import Tour
    from app.models.esperienza import Esperienza
    viaggio = Viaggio.query.get_or_404(id)
    tutti_clienti = Cliente.query.filter_by(attivo=True).order_by(Cliente.cognome, Cliente.nome).all()
    tutti_tours = Tour.query.filter_by(attivo=True).order_by(Tour.nome).all()
    tutte_esperienze = Esperienza.query.filter_by(attivo=True).order_by(Esperienza.nome).all()
    return render_template('viaggi/detail.html', 
                            viaggio=viaggio, 
                            tutti_clienti=tutti_clienti,
                            tutti_tours=tutti_tours,
                            tutte_esperienze=tutte_esperienze)


@viaggi_bp.route('/<int:id>/modifica-info', methods=['POST'])
@login_required
def modifica_info(id):
    viaggio = Viaggio.query.get_or_404(id)
    if viaggio.stato != 'bozza':
        flash('Non puoi modificare un viaggio già confermato o pagato.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))
    
    viaggio.nome = request.form.get('nome')
    viaggio.destinazione = request.form.get('destinazione')
    
    from datetime import datetime
    data_p = request.form.get('data_partenza')
    data_r = request.form.get('data_rientro')
    if data_p: viaggio.data_partenza = datetime.strptime(data_p, '%Y-%m-%d')
    if data_r: viaggio.data_rientro = datetime.strptime(data_r, '%Y-%m-%d')
    
    viaggio.n_adulti = request.form.get('n_adulti', type=int, default=1)
    viaggio.n_bambini = request.form.get('n_bambini', type=int, default=0)
    viaggio.budget = request.form.get('budget', type=float)
    viaggio.note_cliente = request.form.get('note_cliente')
    
    db.session.commit()
    flash('Informazioni viaggio aggiornate.', 'success')
    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/aggiungi-tour', methods=['POST'])
@login_required
def aggiungi_tour(id):
    from app.models.tour import Tour
    viaggio = Viaggio.query.get_or_404(id)
    if viaggio.stato != 'bozza':
        flash('Non puoi modificare un viaggio già confermato o pagato.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))

    tour_id = request.form.get('tour_id', type=int)
    if tour_id:
        tour = Tour.query.get(tour_id)
        if tour and tour not in viaggio.tours:
            viaggio.tours.append(tour)
            # Ricalcolo prezzo
            viaggio.prezzo_totale = float(viaggio.prezzo_totale or 0) + float(tour.prezzo_adulto)
            db.session.commit()
            flash(f'Tour "{tour.nome}" aggiunto.', 'success')
    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/aggiungi-esperienza', methods=['POST'])
@login_required
def aggiungi_esperienza(id):
    from app.models.esperienza import Esperienza
    viaggio = Viaggio.query.get_or_404(id)
    if viaggio.stato != 'bozza':
        flash('Non puoi modificare un viaggio già confermato o pagato.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))

    esp_id = request.form.get('esp_id', type=int)
    if esp_id:
        esp = Esperienza.query.get(esp_id)
        if esp and esp not in viaggio.esperienze:
            viaggio.esperienze.append(esp)
            # Ricalcolo prezzo
            viaggio.prezzo_totale = float(viaggio.prezzo_totale or 0) + float(esp.prezzo_adulto)
            db.session.commit()
            flash(f'Esperienza "{esp.nome}" aggiunta.', 'success')
    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/stato', methods=['POST'])
@login_required
def cambia_stato(id):
    from datetime import datetime
    viaggio = Viaggio.query.get_or_404(id)
    nuovo_stato = request.form.get('stato')
    if nuovo_stato in Viaggio.STATI:
        # Se passa a pagato, inizializza i dati della ricevuta se non già presenti
        if nuovo_stato == 'pagato' and not viaggio.ricevuta_emessa:
            viaggio.ricevuta_emessa = True
            viaggio.data_ricevuta = datetime.utcnow()
            viaggio.numero_ricevuta = f"RIC-{datetime.utcnow().year}-{viaggio.id}"
            flash('Viaggio pagato: Ricevuta pronta.', 'info')
        
        viaggio.stato = nuovo_stato
        db.session.commit()
        flash(f'Stato aggiornato: {viaggio.stato_label()}', 'success')
    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
def elimina(id):
    viaggio = Viaggio.query.get_or_404(id)
    nome = viaggio.nome
    db.session.delete(viaggio)
    db.session.commit()
    flash(f'Viaggio "{nome}" eliminato.', 'warning')
    return redirect(url_for('viaggi.index'))


@viaggi_bp.route('/<int:id>/rimuovi-tour/<int:tour_id>', methods=['POST'])
@login_required
def rimuovi_tour(id, tour_id):
    from app.models.tour import Tour
    viaggio = Viaggio.query.get_or_404(id)
    if viaggio.stato != 'bozza':
        flash('Non puoi modificare un viaggio confermato o pagato.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))

    tour = Tour.query.get_or_404(tour_id)
    if tour in viaggio.tours:
        viaggio.tours.remove(tour)
        db.session.commit()
        flash(f'Tour "{tour.nome}" rimosso.', 'info')
    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/rimuovi-esperienza/<int:esp_id>', methods=['POST'])
@login_required
def rimuovi_esperienza(id, esp_id):
    from app.models.esperienza import Esperienza
    viaggio = Viaggio.query.get_or_404(id)
    if viaggio.stato != 'bozza':
        flash('Non puoi modificare un viaggio confermato o pagato.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))

    esp = Esperienza.query.get_or_404(esp_id)
    if esp in viaggio.esperienze:
        viaggio.esperienze.remove(esp)
        db.session.commit()
        flash(f'Esperienza "{esp.nome}" rimossa.', 'info')
    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/pnr', methods=['POST'])
@login_required
def aggiorna_pnr(id):
    viaggio = Viaggio.query.get_or_404(id)
    viaggio.pnr_volo = request.form.get('pnr_volo', '').strip().upper()
    db.session.commit()
    flash('Numero prenotazione volo aggiornato.', 'success')
    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/rimuovi-volo/<string:item_id>', methods=['POST'])
@login_required
def rimuovi_volo(id, item_id):
    import json
    viaggio = Viaggio.query.get_or_404(id)
    if viaggio.stato != 'bozza':
        flash('Non puoi modificare un viaggio confermato o pagato.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))

    if not viaggio.volo_json:
        return redirect(url_for('viaggi.detail', id=id))

    try:
        data = json.loads(viaggio.volo_json)
        if isinstance(data, dict): # Legacy single object
            if item_id == 'legacy' or data.get('item_id') == item_id:
                prezzo_str = data.get('prezzo', '0')
                try:
                    prezzo = float(prezzo_str.split()[0])
                except:
                    prezzo = 0.0
                viaggio.prezzo_totale = float(viaggio.prezzo_totale or 0) - prezzo
                viaggio.volo_json = None
                viaggio.include_volo = False
        elif isinstance(data, list):
            nuova_lista = []
            prezzo_rimosso = 0.0
            for v in data:
                if v.get('item_id') == item_id:
                    prezzo_str = v.get('prezzo', '0')
                    try:
                        prezzo_rimosso = float(prezzo_str.split()[0])
                    except:
                        prezzo_rimosso = 0.0
                else:
                    nuova_lista.append(v)
            
            viaggio.volo_json = json.dumps(nuova_lista) if nuova_lista else None
            if not nuova_lista: viaggio.include_volo = False
            viaggio.prezzo_totale = round(float(viaggio.prezzo_totale or 0) - prezzo_rimosso, 2)
            
        db.session.commit()
        flash('Volo rimosso.', 'info')
    except Exception as e:
        flash(f'Errore nella rimozione: {str(e)}', 'danger')

    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/rimuovi-transfer/<string:item_id>', methods=['POST'])
@login_required
def rimuovi_transfer(id, item_id):
    import json
    viaggio = Viaggio.query.get_or_404(id)
    if viaggio.stato != 'bozza':
        flash('Non puoi modificare un viaggio confermato o pagato.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))

    if not viaggio.transfer_json:
        return redirect(url_for('viaggi.detail', id=id))

    try:
        data = json.loads(viaggio.transfer_json)
        if isinstance(data, dict):
            if item_id == 'legacy' or data.get('item_id') == item_id:
                prezzo_str = data.get('prezzo', '0')
                try:
                    prezzo = float(prezzo_str.split()[0])
                except:
                    prezzo = 0.0
                viaggio.prezzo_totale = float(viaggio.prezzo_totale or 0) - prezzo
                viaggio.transfer_json = None
                viaggio.include_transfer = False
        elif isinstance(data, list):
            nuova_lista = []
            prezzo_rimosso = 0.0
            for t in data:
                if t.get('item_id') == item_id:
                    prezzo_str = t.get('prezzo', '0')
                    try:
                        prezzo_rimosso = float(str(prezzo_str).split()[0])
                    except:
                        prezzo_rimosso = 0.0
                else:
                    nuova_lista.append(t)
            
            viaggio.transfer_json = json.dumps(nuova_lista) if nuova_lista else None
            if not nuova_lista: viaggio.include_transfer = False
            viaggio.prezzo_totale = round(float(viaggio.prezzo_totale or 0) - prezzo_rimosso, 2)
            
        db.session.commit()
        flash('Transfer rimosso.', 'info')
    except Exception as e:
        flash(f'Errore nella rimozione: {str(e)}', 'danger')

    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/aggiungi-partecipante', methods=['POST'])
@login_required
def aggiungi_partecipante(id):
    from app.models.cliente import Cliente
    viaggio = Viaggio.query.get_or_404(id)
    if viaggio.stato != 'bozza':
        flash('Non puoi modificare un viaggio confermato o pagato.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))

    cliente_id = request.form.get('cliente_id', type=int)
    
    if not cliente_id:
        flash('Seleziona un cliente.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))
        
    cliente = Cliente.query.get_or_404(cliente_id)
    
    if cliente == viaggio.cliente:
        flash('Il cliente è già il capogruppo.', 'info')
    elif cliente in viaggio.partecipanti:
        flash('Il cliente è già tra i partecipanti.', 'info')
    else:
        viaggio.partecipanti.append(cliente)
        db.session.commit()
        flash(f'Cliente "{cliente.nome_completo()}" aggiunto ai partecipanti.', 'success')
        
    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/rimuovi-partecipante/<int:cliente_id>', methods=['POST'])
@login_required
def rimuovi_partecipante(id, cliente_id):
    from app.models.cliente import Cliente
    viaggio = Viaggio.query.get_or_404(id)
    if viaggio.stato != 'bozza':
        flash('Non puoi modificare un viaggio confermato o pagato.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))

    cliente = Cliente.query.get_or_404(cliente_id)
    
    if cliente in viaggio.partecipanti:
        viaggio.partecipanti.remove(cliente)
        db.session.commit()
        flash(f'Partecipante "{cliente.nome_completo()}" rimosso.', 'info')
        
    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/pdf')
@login_required
def esporta_pdf(id):
    from xhtml2pdf import pisa
    from io import BytesIO
    from flask import make_response
    
    from datetime import datetime
    viaggio = Viaggio.query.get_or_404(id)
    html = render_template('viaggi/pdf_report.html', viaggio=viaggio, now=datetime.utcnow().strftime('%d/%m/%Y %H:%M'))
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=viaggio_{id}.pdf'
        return response
    
    flash("Errore durante la generazione del PDF.", "danger")
    return redirect(url_for('viaggi.detail', id=id))


@viaggi_bp.route('/<int:id>/ricevuta')
@login_required
def emetti_ricevuta(id):
    from xhtml2pdf import pisa
    from io import BytesIO
    from flask import make_response
    from datetime import datetime
    
    viaggio = Viaggio.query.get_or_404(id)
    if viaggio.stato not in ['pagato', 'completato']:
        flash('La ricevuta può essere emessa solo per viaggi pagati.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))
        
    if not viaggio.ricevuta_emessa:
        viaggio.ricevuta_emessa = True
        viaggio.data_ricevuta = datetime.utcnow()
        viaggio.numero_ricevuta = f"RIC-{datetime.utcnow().year}-{viaggio.id}"
        db.session.commit()
        
    html = render_template('viaggi/ricevuta_pdf.html', 
                          viaggio=viaggio, 
                          now=datetime.utcnow().strftime('%d/%m/%Y %H:%M'))
    
    result = BytesIO()
    pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    
    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=ricevuta_{viaggio.id}.pdf'
    return response


@viaggi_bp.route('/<int:id>/fattura')
@login_required
def emetti_fattura(id):
    from xhtml2pdf import pisa
    from io import BytesIO
    from flask import make_response
    from datetime import datetime
    
    viaggio = Viaggio.query.get_or_404(id)
    if not viaggio.ricevuta_emessa:
        flash('Emetti prima la ricevuta.', 'warning')
        return redirect(url_for('viaggi.detail', id=id))
        
    if not viaggio.fattura_emessa:
        viaggio.fattura_emessa = True
        viaggio.data_fattura = datetime.utcnow()
        viaggio.numero_fattura = f"FAT-{datetime.utcnow().year}-{viaggio.id}"
        db.session.commit()
        
    html = render_template('viaggi/fattura_pdf.html', viaggio=viaggio, now=datetime.utcnow().strftime('%d/%m/%Y %H:%M'))
    
    result = BytesIO()
    pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    
    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=fattura_{viaggio.id}.pdf'
    return response
