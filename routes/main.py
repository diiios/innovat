from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.ideas import Idea
from ..models.tools_chapter import ToolSection
from ..models.resources import Resources
from ..models.events import Events


import smtplib
from email.mime.text import MIMEText
import os



main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    ideas = Idea.query.order_by(Idea.id.desc()).limit(5).all()  
    tool_sections = ToolSection.query.order_by(ToolSection.id.desc()).all()
    reses = Resources.query.order_by(Resources.id.desc()).all()
    events = Events.query.order_by(Events.id.desc()).all()
    return render_template('main/index.html', ideas=ideas, tool_sections = tool_sections, reses=reses, events=events)


@main.route('/send', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash("Пожалуйста, заполните все поля.", "error")
        return redirect(url_for('main.index'))

    # SMTP-настройки (пример для Яндекс)
    smtp_server = "smtp.yandex.ru"
    smtp_port = 465
    smtp_login = os.getenv("EMAIL_USERNAME")  # желательно хранить в .env
    smtp_password = os.getenv("EMAIL_PASSWORD")
    recipient = smtp_login

    subject = f"Сообщение с сайта от {name}"
    body = f"Имя: {name}\nEmail: {email}\n\nСообщение:\n{message}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_login
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_login, smtp_password)
            server.sendmail(smtp_login, recipient, msg.as_string())
        flash("Сообщение отправлено!", "success")
    except Exception as e:
        flash(f"Ошибка при отправке: {e}", "error")

    return redirect(request.referrer or url_for('main.index'))

@main.route('/help', methods=['GET'])
def open_help():
    return render_template('main/help.html')
