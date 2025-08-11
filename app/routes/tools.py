from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from ..extentions import db
from ..models.tools import Tool
from ..models.tools_chapter import ToolSection
from ..models.comments import Comment
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime
import time
import shutil

import imghdr
import io


tool = Blueprint('tool', __name__)


@tool.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # объявляем переменные сразу, чтобы избежать UnboundLocalError
        photo = request.files.get('tool_photo')
        pdf = request.files.get('tool_pdf')

        if not session.get('is_admin'):
            username = request.form.get('username')
            password = request.form.get('password')
            if username == 'admin' and password == 'secret':
                session['is_admin'] = True
                return redirect(url_for('tool.create'))
            else:
                flash('Неверный логин или пароль', 'error')
                return redirect(url_for('tool.create'))

        name = request.form.get('tool_name')
        type = request.form.get('tool_type')

        try:
            section_id = int(request.form.get('section_id'))
        except (TypeError, ValueError):
            flash('Выберите корректный раздел', 'error')
            return redirect(url_for('tool.create'))
        
        new_tool = Tool(
            name=name,
            type=type,
            section_id=section_id,
            photo=None,
            file=None,
        )

        db.session.add(new_tool)
        db.session.flush()
        tool_id = new_tool.id

        base_folder = os.path.join('app/static/uploads/tools', str(section_id), str(tool_id))
        os.makedirs(base_folder, exist_ok=True)

        import imghdr
        import io
        if photo and photo.filename:
            original_photo_filename = secure_filename(photo.filename)
            photo_name, _ = os.path.splitext(original_photo_filename)

            photo_bytes = photo.read()
            image_type = imghdr.what(None, h=photo_bytes)
            if not image_type:
                flash('Неверный тип изображения', 'error')
                return redirect(request.url)  # или куда нужно

            # Восстанавливаем поток для сохранения
            photo.stream = io.BytesIO(photo_bytes)

            ext = f'.{image_type}'
            unique_string = photo_name + str(time.time())
            hashed_name = hashlib.md5(unique_string.encode('utf-8')).hexdigest()
            photo_filename = f"{hashed_name}{ext}"

            os.makedirs(base_folder, exist_ok=True)
            photo_path = os.path.join(base_folder, photo_filename)
            photo.save(photo_path)

            new_tool.photo = f"{section_id}/{tool_id}/{photo_filename}"


        if pdf and pdf.filename:
            original_pdf_filename = secure_filename(pdf.filename)
            file_name, ext = os.path.splitext(original_pdf_filename)
            if not ext:
                ext = '.pdf'  # подстраховка, если расширения нет
            unique_string = file_name + str(time.time())
            hashed_name = hashlib.md5(unique_string.encode('utf-8')).hexdigest()
            pdf_filename = f"{hashed_name}{ext}"

            pdf_path = os.path.join(base_folder, pdf_filename)
            pdf.save(pdf_path)
            new_tool.file = f"{section_id}/{tool_id}/{pdf_filename}"

        db.session.commit()
        flash('Инструмент успешно создан и сохранен в базе!', 'success')
        return redirect(url_for('tool.create'))

    # GET-запрос
    sections = ToolSection.query.all()
    print(f'✅ Подгружаем разделы ({len(sections)}): {[s.name for s in sections]}')
    return render_template('main/create.html', is_admin=session.get('is_admin'), sections=sections)

@tool.route('/all')
def open():
    sections = ToolSection.query.all()
    # print(f'Loaded sections ({len(sections)}): {[s.name for s in sections]}')
    return render_template('main/tools.html', is_admin=session.get('is_admin'), sections=sections)

@tool.route('/type/<string:type_name>')
def open_by_type(type_name):
    tools = Tool.query.filter_by(type=type_name).all()
    return render_template('main/tool.html', tools=tools, type_name=type_name, is_admin=session.get('is_admin'))


@tool.route('/create-chapter', methods=('GET', 'POST'))
def create_chapter():
    if request.method == 'POST':
        # Проверка админа
        if not session.get('is_admin'):
            username = request.form.get('username')
            password = request.form.get('password')

            if username == 'admin' and password == 'secret':
                session['is_admin'] = True
                return redirect(url_for('tool.create'))
            else:
                flash('Неверный логин или пароль', 'error')
                return redirect(url_for('tool.create_chapter'))

        # Получаем данные
        name = request.form.get('tool_chapter_name')
        description = request.form.get('tool_chapter_description')
        photo = request.files.get('tool_chapter_photo')
        icon = request.files.get('tool_chapter_icon')  # добавлено поле для иконки

        # Шаг 1 — создаём раздел (без фото и иконки пока)
        new_tool_chapter = ToolSection(
            name=name,
            description=description,
            photo=None,
            icon=None,
        )
        db.session.add(new_tool_chapter)
        db.session.flush()  # получаем ID без коммита
        section_id = new_tool_chapter.id

        # Шаг 2 — создаём папку
        section_folder = os.path.join('app/static/uploads/tools', str(section_id))
        os.makedirs(section_folder, exist_ok=True)

        # Шаг 3 — сохраняем фото (если есть)
        if photo and photo.filename:
        # Получаем оригинальное имя (но не полагаемся на расширение)
            original_photo_filename = secure_filename(photo.filename)
            photo_name, _ = os.path.splitext(original_photo_filename)

            # Читаем часть файла, чтобы определить его тип
            photo_bytes = photo.read()  # читаем весь файл в память
            image_type = imghdr.what(None, h=photo_bytes)  # например: 'jpeg', 'png', 'gif'

            if not image_type:
                flash('Неверный тип изображения', 'error')
                return redirect(url_for('tool.create_chapter'))

            # Восстанавливаем поток файла, чтобы сохранить позже
            photo.stream = io.BytesIO(photo_bytes)

            # Создаём уникальное имя с правильным расширением
            ext = f'.{image_type}'
            unique_string = photo_name + str(time.time())
            hashed_name = hashlib.md5(unique_string.encode('utf-8')).hexdigest()
            photo_filename = f"{hashed_name}{ext}"

            # Путь к сохранению
            photo_path = os.path.join(section_folder, photo_filename)
            print('📸 Сохраняем фото в:', photo_path)

            # Сохраняем файл
            photo.save(photo_path)

            # Сохраняем путь в БД (относительный путь от static/)
            new_tool_chapter.photo = f"{section_id}/{photo_filename}"

        # Шаг 4 — сохраняем иконку (если есть)
        if icon and icon.filename:
            _, ext = os.path.splitext(secure_filename(icon.filename))
            icon_filename = f"icon{ext}"  # фиксированное имя для иконки
            icon_path = os.path.join(section_folder, icon_filename)
            print('🖼️ Сохраняем иконку раздела в:', icon_path)
            icon.save(icon_path)

            # Сохраняем путь в БД (относительный путь от static/)
            new_tool_chapter.icon = f"{section_id}/{icon_filename}"

        # Обновляем объект после изменения полей
        db.session.add(new_tool_chapter)

        # Шаг 5 — коммит
        db.session.commit()

        flash('Раздел успешно создан', 'success')
        return redirect(url_for('tool.create_chapter'))

    # GET
    sections = ToolSection.query.all()
    return render_template('main/create.html', is_admin=session.get('is_admin'), sections=sections)


@tool.route('/section/<int:section_id>')
def open_section(section_id):
    section = ToolSection.query.get_or_404(section_id)
    tools = Tool.query.filter_by(section_id=section_id).all()
    comments = CommentTools.query.filter_by(object_type='tool_section', object_id=section_id).order_by(CommentTools.date.desc()).all()
    return render_template(
        'main/tool.html',
        tools=tools,
        section=section,
        comments=comments,
        is_admin=session.get('is_admin'),
        object_type='tool_section',
        object_id=section_id
    )

from flask import request, redirect, url_for, flash
# from ..models.comments import Comment
# from datetime import datetime

from flask import request, jsonify
from datetime import datetime
from ..models.comments import Comment
from ..extentions import db
from ..models.tools_comments import CommentTools

@tool.route('comment', methods=['POST'])
def add_comment_tools():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.get_json()
        print('Получены данные комментария:', data)  # Добавьте лог

        name = data.get('name')
        text = data.get('text')
        object_type = data.get('object_type')
        object_id = data.get('object_id')

        if not all([name, text, object_type, object_id]):
            return jsonify({'error': 'Missing required data'}), 400


        new_comment = CommentTools(
            name=name,
            text=text,
            date=datetime.utcnow(),
            object_type=object_type,
            object_id=object_id
        )
        db.session.add(new_comment)
        db.session.commit()

        return jsonify({
            'id': new_comment.id,
            'name': name,
            'text': text,
            'date': new_comment.date.strftime('%d.%m.%Y %H:%M')
        })

    return '', 400

import shutil
import os

@tool.route('/section/delete/<int:section_id>', methods=['POST'])
def delete_section(section_id):
    if not session.get('is_admin'):
        flash('Нет прав для удаления', 'error')
        return redirect(url_for('tool.open'))

    section = ToolSection.query.get_or_404(section_id)

    # Получаем все инструменты раздела
    tools = Tool.query.filter_by(section_id=section_id).all()
    tool_ids = [tool.id for tool in tools]

    # Удаляем комментарии по разделу
    db.session.query(CommentTools).filter_by(object_type='tool_section', object_id=section_id).delete(synchronize_session=False)

    # Удаляем комментарии по инструментам раздела
    if tool_ids:
        db.session.query(CommentTools).filter(CommentTools.object_type=='tool', CommentTools.object_id.in_(tool_ids)).delete(synchronize_session=False)

    # Удаляем инструменты раздела
    Tool.query.filter_by(section_id=section_id).delete(synchronize_session=False)

    # Удаляем сам раздел
    db.session.delete(section)

    # Удаляем папку раздела вместе со всем содержимым
    base_folder = os.path.join('app/static/uploads/tools', str(section_id))
    if os.path.exists(base_folder):
        try:
            shutil.rmtree(base_folder)
        except Exception as e:
            # Логирование ошибки и сообщение пользователю
            print(f"Ошибка при удалении папки раздела: {e}")
            flash('Не удалось полностью удалить папку раздела на диске.', 'warning')

    db.session.commit()
    flash('Раздел и все связанные данные успешно удалены', 'success')
    return redirect(url_for('tool.open'))

@tool.route('/comment/delete/<int:id>', methods=['POST'])
def delete_comment(id):
    comment = CommentTools.query.get_or_404(id)

    section_id = comment.object_id  # предполагаем, что object_type == 'tool_section'

    db.session.delete(comment)
    db.session.commit()

    flash('Комментарий удалён', 'success')

    return redirect(url_for('tool.open_section', section_id=section_id) + '#comments')


@tool.route('/delete/<int:id>', methods=['POST'])
def delete_tool(id):
    tool_obj = Tool.query.get_or_404(id)
    section_id = tool_obj.section_id
    folder_path = os.path.join('app/static/uploads/tools', str(section_id), str(tool_obj.id))

    # Удаляем папку с файлами (если существует)
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
        except Exception as e:
            flash(f'Ошибка при удалении файлов инструмента: {e}', 'error')
            # Можно логировать ошибку

    # Удаляем объект из БД
    db.session.delete(tool_obj)
    db.session.commit()

    flash('Инструмент удален', 'success')
    return redirect(url_for('tool.open_section', section_id=section_id))



@tool.route('/vote/<int:id>', methods=['POST'])
def vote(id):
    tool_obj = ToolSection.query.get_or_404(id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.get_json()
        action = data.get('action')

        if action == 'like':
            tool_obj.likes = (tool_obj.likes or 0) + 1
        elif action == 'dislike':
            tool_obj.dislikes = (tool_obj.dislikes or 0) + 1
        elif action == 'unlike':
            tool_obj.likes = max((tool_obj.likes or 0) - 1, 0)
        elif action == 'undislike':
            tool_obj.dislikes = max((tool_obj.dislikes or 0) - 1, 0)

        db.session.commit()

        return jsonify({
            'likes': tool_obj.likes,
            'dislikes': tool_obj.dislikes
        })

    return 'Bad Request', 400