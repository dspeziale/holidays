from flask import render_template, current_app, url_for
from flask_mail import Message
from app import mail
from threading import Thread


def _send_async(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f'Errore invio email: {e}')


def send_email(to, subject, template=None, body=None, html=None,
               attachments=None, async_send=True, **kwargs):
    if isinstance(to, str):
        to = [to]

    msg = Message(subject=subject, recipients=to)

    if template:
        try:
            msg.body = render_template(f'{template}.txt', **kwargs)
        except Exception:
            msg.body = subject
        try:
            msg.html = render_template(f'{template}.html', **kwargs)
        except Exception:
            pass
    else:
        msg.body = body or ''
        if html:
            msg.html = html

    if attachments:
        for att in attachments:
            msg.attach(
                filename=att['filename'],
                content_type=att.get('content_type', 'application/octet-stream'),
                data=att['data']
            )

    if async_send:
        app = current_app._get_current_object()
        t = Thread(target=_send_async, args=(app, msg))
        t.daemon = True
        t.start()
    else:
        mail.send(msg)

    return True


def send_benvenuto_utente(user, password_generata):
    """Email di benvenuto con password temporanea al nuovo utente."""
    send_email(
        to=user.email,
        subject='Benvenuto in Roma Lusso Travel — Le tue credenziali',
        template='email/benvenuto',
        user=user,
        password_generata=password_generata,
        async_send=False
    )


def send_reset_password(user, token):
    """Email per reset password."""
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    send_email(
        to=user.email,
        subject='Reset Password — Roma Lusso Travel',
        template='email/reset_password',
        user=user,
        reset_url=reset_url,
        async_send=False
    )


def send_email_generica(to, subject, messaggio, mittente_nome=None):
    send_email(
        to=to,
        subject=subject,
        template='email/generica',
        messaggio=messaggio,
        mittente_nome=mittente_nome
    )
