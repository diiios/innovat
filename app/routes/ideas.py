from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from ..extentions import db
from ..models.ideas import Idea
from ..models.comments import Comment
from ..models.tools_chapter import ToolSection
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime
import time

idea = Blueprint('idea', __name__)

@idea.route('/create', methods=('GET', 'POST'))
def create():
    sections = ToolSection.query.all()
    if request.method == 'POST':
        photo = None
        pdf = None
        print('--- POST data received in idea.create ---')
        print('Form keys:', list(request.form.keys()))
        print('Form data:')
        for key in request.form.keys():
            print(f'  {key}: {request.form.get(key)}')

        print('Files:', list(request.files.keys()))
        for file_key in request.files.keys():
            f = request.files[file_key]
            print(f'  File field: {file_key}, filename: {f.filename if f else "None"}')

        if not session.get('is_admin'):
            # Проверка логина
            username = request.form.get('username')
            password = request.form.get('password')

            if username == 'admin' and password == '123':
                session['is_admin'] = True
                return redirect(url_for('idea.create'))
            else:
                flash('Неверный логин или пароль', 'error')

        else:
            # Получаем данные идеи
            name = request.form.get('name')
            description = request.form.get('description')
            # tags = request.form.get('tags')

            # Получаем все выбранные значения тегов (список)
            tags_list = request.form.getlist('tags')

            # Преобразуем в строку через запятую
            tags_string = ', '.join(tags_list)

            links = request.form.get('links')
            likes = 0
            dislikes = 0

            photo = request.files.get('photos')
            pdf = request.files.get('pdf_file')


            # Сохраняем фото

        import imghdr
        import io

        if photo and photo.filename:
            # Получаем оригинальное имя (но не полагаемся на расширение)
            original_photo_filename = secure_filename(photo.filename)
            photo_name, _ = os.path.splitext(original_photo_filename)

            # Читаем часть файла, чтобы определить его тип
            photo_bytes = photo.read()  # читаем весь файл в память
            image_type = imghdr.what(None, h=photo_bytes)  # например: 'jpeg', 'png', 'gif'

            if not image_type:
                flash('Неверный тип изображения', 'error')
                return redirect(url_for('idea.create'))

            # Восстанавливаем поток файла, чтобы сохранить позже
            photo.stream = io.BytesIO(photo_bytes)

            # Создаём уникальное имя с правильным расширением
            ext = f'.{image_type}'
            unique_string = photo_name + str(time.time())
            hashed_name = hashlib.md5(unique_string.encode('utf-8')).hexdigest()
            photo_filename = f"{hashed_name}{ext}"

            # Путь к сохранению
            photo_folder = current_app.config['UPLOAD_IDEA_PHOTOS']
            os.makedirs(photo_folder, exist_ok=True)
            photo_path = os.path.join(photo_folder, photo_filename)
            print('📸 Сохраняем фото в:', photo_path)

            # Сохраняем файл
            photo.save(photo_path)

            if pdf and pdf.filename:
                original_pdf_filename = secure_filename(pdf.filename)
                file_name, ext = os.path.splitext(original_pdf_filename)

                if not ext:  # если нет расширения — добавим .pdf
                    ext = '.pdf'

                unique_string = file_name + str(time.time())
                hashed_name = hashlib.md5(unique_string.encode('utf-8')).hexdigest()
                pdf_filename = f"{hashed_name}{ext}"

                pdf_folder = current_app.config['UPLOAD_IDEA_FILES']
                os.makedirs(pdf_folder, exist_ok=True)
                pdf_path = os.path.join(pdf_folder, pdf_filename)
                pdf.save(pdf_path)

            # Создаём объект модели Idea
            new_idea = Idea(
                name=name,
                description=description,
                tags=tags_string,
                links=links,
                photo=photo_filename,
                file=pdf_filename,
                likes=likes,
                dislikes=dislikes,
            )

            db.session.add(new_idea)
            db.session.commit()

            flash('Идея успешно создана и сохранена в базе!', 'success')
            return redirect(url_for('idea.create'))

    return render_template('main/create.html', is_admin=session.get('is_admin'), sections=sections)# Выход

@idea.route('/logout', methods=['POST'])
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('idea.create'))

# @idea.route('/ideas')
# def open():
#     page = request.args.get('page', 1, type=int)
#     per_page = 5

#     pagination = Idea.query.order_by(Idea.id.desc()).paginate(page=page, per_page=per_page)
#     ideas = pagination.items
#     comments = Comment.query.order_by(Comment.date.desc()).all()

#     return render_template('main/ideas.html',
#                            ideas=ideas,
#                            pagination=pagination,
#                            comments=comments,
#                            is_admin=session.get('is_admin'))

@idea.route('/ideas')
def open():
    all_ideas = Idea.query.order_by(Idea.id.desc()).all()  # Все идеи
    comments = Comment.query.order_by(Comment.date.desc()).all()

    return render_template('main/ideas.html',
                           ideas=all_ideas,
                           comments=comments,
                           is_admin=session.get('is_admin'))

@idea.route('/idea/<int:id>')
def open_one(id):
    idea = Idea.query.get_or_404(id)
    return render_template('main/idea.html', idea=idea, is_admin=session.get('is_admin'))


import os

@idea.route('/delete/<int:id>', methods=['POST'])
def delete(id):  # функция удаления идеи
    idea = Idea.query.get_or_404(id)

    # Удаляем связанные файлы
    if idea.photo:
        photo_path = os.path.join(current_app.config['UPLOAD_IDEA_PHOTOS'], idea.photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)
            print(f'🗑️ Удалено фото: {photo_path}')
        else:
            print(f'⚠️ Фото не найдено: {photo_path}')

    if idea.file:
        pdf_path = os.path.join(current_app.config['UPLOAD_IDEA_FILES'], idea.file)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f'🗑️ Удалён PDF: {pdf_path}')
        else:
            print(f'⚠️ PDF не найден: {pdf_path}')

    # Удаляем из базы
    db.session.delete(idea)
    db.session.commit()

    flash('Идея и её файлы успешно удалены.', 'success')
    return redirect(url_for('idea.open'))

from flask import jsonify

@idea.route('/vote/<int:id>', methods=['POST'])
def vote(id):
    idea_obj = Idea.query.get_or_404(id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.get_json()
        action = data.get('action')

        if action == 'like':
            idea_obj.likes = (idea_obj.likes or 0) + 1
        elif action == 'dislike':
            idea_obj.dislikes = (idea_obj.dislikes or 0) + 1
        elif action == 'unlike':
            idea_obj.likes = max((idea_obj.likes or 0) - 1, 0)
        elif action == 'undislike':
            idea_obj.dislikes = max((idea_obj.dislikes or 0) - 1, 0)

        db.session.commit()

        return jsonify({
            'likes': idea_obj.likes,
            'dislikes': idea_obj.dislikes
        })

    return 'Bad Request', 400

from flask import request, redirect, url_for, flash
# from ..models.comments import Comment
# from datetime import datetime

from flask import request, jsonify
from datetime import datetime
from ..models.comments import Comment
from ..extentions import db

@idea.route('/comment', methods=['POST'])
def add_comment():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.get_json()
        name = data.get('name')
        text = data.get('text')

        new_comment = Comment(name=name, text=text, date=datetime.utcnow())
        db.session.add(new_comment)
        db.session.commit()

        return jsonify({
            'id': new_comment.id,            # Очень важно вернуть id
            'name': name,
            'text': text,
            'date': new_comment.date.strftime('%d.%m.%Y %H:%M')
        })
    return '', 400


@idea.route('/comment/delete/<int:id>', methods=['POST'])
def delete_comment(id):
    comment = Comment.query.get_or_404(id)

    db.session.delete(comment)
    db.session.commit()

    flash('Комментарий удален', 'success')
    return redirect(url_for('idea.open') + '#comments')  # или куда нужно