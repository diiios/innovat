from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from ..extentions import db
from ..models.events import Events
import os
from datetime import datetime

import io
import time
import imghdr
import hashlib
from werkzeug.utils import secure_filename


event = Blueprint('event', __name__)

@event.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        if not session.get('is_admin'):
            username = request.form.get('username')
            password = request.form.get('password')
            if username == 'admin' and password == '123':
                session['is_admin'] = True
                return redirect(url_for('event.create'))
            else:
                flash('Неверный логин или пароль', 'error')
                return redirect(url_for('event.create'))

        # 1. Дата
        start_date_str = request.form.get('date_start')
        end_date_str = request.form.get('date_end')

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None
        except ValueError:
            flash('Неверный формат даты', 'error')
            return redirect(url_for('event.create'))

        # 2. Формат
        places = request.form.getlist('place')  # получим все чекбоксы
        place = ', '.join(places)

        # 3. Остальные поля
        link = request.form.get('link')
        text = request.form.get('text')
        slogan = request.form.get('slogan')

        # Обработка фото с хешированием
        photo_file = request.files.get('photo')
        photo_filename = None

        if photo_file and photo_file.filename:
            original_filename = secure_filename(photo_file.filename)
            photo_name, _ = os.path.splitext(original_filename)

            # Читаем байты, чтобы определить тип изображения
            photo_bytes = photo_file.read()
            image_type = imghdr.what(None, h=photo_bytes)

            if not image_type:
                flash('Неверный тип изображения', 'error')
                return redirect(url_for('event.create'))

            # Создаем новое имя файла: md5 от имени + время + расширение
            ext = f'.{image_type}'
            hash_name = hashlib.md5((photo_name + str(time.time())).encode()).hexdigest()
            photo_filename = f'{hash_name}{ext}'

            # Путь для сохранения
            save_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'events')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, photo_filename)

            # Сохраняем файл — для этого заново создаем поток из байтов
            photo_file.stream = io.BytesIO(photo_bytes)
            photo_file.save(save_path)


        # 5. Сохраняем в БД
        new_event = Events(
            link=link,
            start_date=start_date,
            end_date=end_date,
            place=place,
            text=text,
            slogan=slogan,
            photo=photo_filename
        )
        db.session.add(new_event)
        db.session.commit()

        flash("Мероприятие добавлено!", "success")
        return redirect(url_for('event.create'))

    return render_template('main/create.html', is_admin=session.get('is_admin'))


@event.route('/event/delete/<int:id>', methods=['POST'])
def delete(id):
    event = Events.query.get_or_404(id)

    # Удаление фото
    if event.photo:
        photo_path = os.path.join(current_app.static_folder, 'uploads', 'events', event.photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)

    # Удаление самого события
    db.session.delete(event)
    db.session.commit()
    flash('Мероприятие удалено', 'success')

    return redirect(url_for('main.index'))