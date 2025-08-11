from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from ..extentions import db
from ..models.resources import Resources
from ..models.comments import Comment
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime
import time
import shutil
import random
import re

resources = Blueprint('resource', __name__)

@resources.route('/create')
def open():
    resources = Resources.query.all()
    return render_template('main/resources.html', resources=resources)







def parse_test_from_text(raw_text):
    questions_html = []
    question_blocks = [q.strip() for q in raw_text.strip().split('***') if q.strip()]
    
    for index, block in enumerate(question_blocks, start=1):
        lines = block.splitlines()
        if not lines:
            continue

        question_match = re.match(r'\d+\)\s*(.+)', lines[0])
        if not question_match:
            continue
        question_text = question_match.group(1).strip()

        answers_html = []
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('-'):
                ans_text = line[1:].strip()
                
                # НЕПРАВИЛЬНЫЙ ответ — число НЕ должно делиться на 3 и 4 одновременно
                number = random.randint(10000, 100000)
                while number % 12 == 0:
                    number = random.randint(10000, 100000)

                answers_html.append(f'<button value="{number}">{ans_text}</button>')
            
            elif line.startswith('+'):
                ans_text = line[1:].strip()
                
                # ПРАВИЛЬНЫЙ ответ — число ДОЛЖНО делиться на 3 и 4 → на 12
                number = random.randint(10000, 100000)
                while number % 12 != 0:
                    number = random.randint(10000, 100000)

                answers_html.append(f'<button value="{number}">{ans_text}</button>')

        question_html = f'''
        <div class="one-question" data-question="{index}">
          <div>
            <h1>{question_text}</h1>
            <h2>Варианты ответов</h2>
          </div>
          {''.join(answers_html)}
        </div>
        '''
        questions_html.append(question_html)

    result_button_html = '''
    <button class="get-rezalt">
      Узнать ответ
    </button>
    '''

    full_html = f'{"".join(questions_html)}\n{result_button_html}'
    return full_html

# def parse_test_from_text(raw_text):
#     questions_html = []
#     question_blocks = [q.strip() for q in raw_text.strip().split('***') if q.strip()]
    
#     for index, block in enumerate(question_blocks, start=1):
#         lines = block.splitlines()
#         if not lines:
#             continue

#         question_match = re.match(r'\d+\)\s*(.+)', lines[0])
#         if not question_match:
#             continue
#         question_text = question_match.group(1).strip()

#         answers_html = []
#         for line in lines[1:]:
#             line = line.strip()
#             if line.startswith('-'):
#                 ans_text = line[1:].strip()
#                 answers_html.append(f'<button>{ans_text}</button>')
#             elif line.startswith('+'):
#                 ans_text = line[1:].strip()
#                 answers_html.append(f'<button value="right">{ans_text}</button>')

#         question_html = f'''
#         <div class="one-question" data-question="{index}">
#           <h1>{index}) {question_text}</h1>
#           {''.join(answers_html)}
#         </div>
#         '''
#         questions_html.append(question_html)

#     result_button_html = '''
#     <button class="get-rezalt">
#       Узнать ответ
#     </button>
#     '''

#     full_html = f'{"".join(questions_html)}\n{result_button_html}'
#     return full_html

@resources.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        print('--- POST data received in resource.create ---')
        print('Form keys:', list(request.form.keys()))
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

            if username == 'admin' and password == 'secret':
                session['is_admin'] = True
                return redirect(url_for('resource.create'))
            else:
                flash('Неверный логин или пароль', 'error')
        else:
            import os
            import io
            import time
            import imghdr
            import hashlib
            from werkzeug.utils import secure_filename

            # Получаем данные ресурса
            name = request.form.get('res_name')
            raw_test_text = request.form.get('test')
            parsed_test_html = parse_test_from_text(raw_test_text)
            dop = request.form.get('res_dop')
            description = request.form.get('res_description')
            likes = 0
            dislikes = 0

            photo = request.files.get('res_photo')
            pdf = request.files.get('res_pdf')

            # 1. Сохраняем ресурс в базу (без файлов)
            new_res = Resources(
                name=name,
                dop=dop,
                description=description,
                test=parsed_test_html,
                likes=likes,
                dislikes=dislikes
            )
            db.session.add(new_res)
            db.session.flush()

            res_id = new_res.id

            # Папка для ресурса: static/uploads/resources/<res_id>
            base_upload_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_RES'])
            res_folder = os.path.join(base_upload_path, str(res_id))
            os.makedirs(res_folder, exist_ok=True)

            # 2. Сохраняем фото
            if photo and photo.filename:
                original_photo_filename = secure_filename(photo.filename)
                photo_name, _ = os.path.splitext(original_photo_filename)

                photo_bytes = photo.read()
                image_type = imghdr.what(None, h=photo_bytes)
                if not image_type:
                    flash('Неверный тип изображения', 'error')
                    return redirect(url_for('resource.create'))

                photo.stream = io.BytesIO(photo_bytes)
                ext = f'.{image_type}'
                hashed_name = hashlib.md5((photo_name + str(time.time())).encode()).hexdigest()
                photo_filename = f'{hashed_name}{ext}'
                photo_path = os.path.join(res_folder, photo_filename)
                photo.save(photo_path)

                # Путь в базе — относительно /static/
                new_res.photo = photo_filename

            # 3. Сохраняем PDF
            if pdf and pdf.filename:
                original_pdf_filename = secure_filename(pdf.filename)
                file_name, ext = os.path.splitext(original_pdf_filename)
                if not ext:
                    ext = '.pdf'
                hashed_name = hashlib.md5((file_name + str(time.time())).encode()).hexdigest()
                pdf_filename = f'{hashed_name}{ext}'
                pdf_path = os.path.join(res_folder, pdf_filename)
                pdf.save(pdf_path)

                new_res.file = pdf_filename

            # 4. Коммитим
            db.session.commit()

            flash('Ресурс успешно создан и сохранён!', 'success')
            return redirect(url_for('resource.create'))

    return render_template('main/create.html', is_admin=session.get('is_admin'))

@resources.route('/<int:id>')
def open_one(id):
    resource = Resources.query.get_or_404(id)
    return render_template('main/resource.html', resource=resource, is_admin=session.get('is_admin'))

from flask import jsonify
@resources.route('/vote/<int:id>', methods=['POST'])
def vote(id):
    idea_obj = Resources.query.get_or_404(id)

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

#внутри routes/resources.py


@resources.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete_resource(id):
    resource = db.session.get(Resources, id)

    if not resource:
        flash('Ресурс не найден', 'error')
        return redirect(url_for('resource.open'))

    try:
        # Удаляем папку с файлами ресурса
        res_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'resources', str(id))
        if os.path.exists(res_folder):
            import shutil
            shutil.rmtree(res_folder)
            print(f'🗑️ Удалена папка ресурса: {res_folder}')
        else:
            print(f'⚠️ Папка не найдена: {res_folder}')

        # Удаляем сам ресурс из базы
        db.session.delete(resource)
        db.session.commit()

        flash(f'Ресурс ID {id} успешно удалён!', 'success')
    except Exception as e:
        print('Ошибка при удалении:', e)
        flash('Произошла ошибка при удалении ресурса', 'error')

    return redirect(url_for('resource.open'))