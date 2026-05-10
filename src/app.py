import os
import subprocess
import tempfile
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Task, Submission, BLOCKS, seed_tasks

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', '8013b162-6b42-4997-9691-77b7074026e0')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arete_lms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()
    seed_tasks()


@app.route('/')
def index():
    blocks_data = []
    for key, info in BLOCKS.items():
        count = Task.query.filter_by(block=key).count()
        solved = 0
        if current_user.is_authenticated:
            solved = current_user.solved_in_block(key)
        blocks_data.append({
            'key': key,
            'name': info['name'],
            'icon': info['icon'],
            'description': info['description'],
            'count': count,
            'solved': solved,
        })
    return render_template('index.html', blocks=blocks_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirmPassword', '')

        errors = []
        if not first_name or not last_name:
            errors.append('Введите имя и фамилию.')
        if not username or len(username) < 3:
            errors.append('Имя пользователя должно быть не менее 3 символов.')
        if not email or '@' not in email:
            errors.append('Введите корректный email.')
        if len(password) < 8:
            errors.append('Пароль должен содержать не менее 8 символов.')
        if password != confirm_password:
            errors.append('Пароли не совпадают.')
        if User.query.filter_by(username=username).first():
            errors.append('Имя пользователя уже занято.')
        if User.query.filter_by(email=email).first():
            errors.append('Email уже зарегистрирован.')

        if errors:
            return render_template('register.html', errors=errors, form_data=request.form)

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('index'))

    return render_template('register.html', errors=[], form_data={})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember') == 'on')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            return render_template('login.html', error='Неверный email или пароль.')

    return render_template('login.html', error=None)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/block/<block_key>')
def block(block_key):
    if block_key not in BLOCKS:
        return redirect(url_for('index'))

    block_info = BLOCKS[block_key]
    tasks = Task.query.filter_by(block=block_key).order_by(Task.order_num).all()

    tasks_data = []
    for t in tasks:
        solved = False
        if current_user.is_authenticated:
            solved = t.solved_by(current_user.id)
        tasks_data.append({'task': t, 'solved': solved})

    total = len(tasks)
    solved_count = sum(1 for td in tasks_data if td['solved'])

    return render_template('block.html',
                           block_key=block_key,
                           block_info=block_info,
                           tasks_data=tasks_data,
                           total=total,
                           solved_count=solved_count)


@app.route('/task/<int:task_id>')
def task(task_id):
    t = Task.query.get_or_404(task_id)
    block_info = BLOCKS.get(t.block, {})

    last_submission = None
    if current_user.is_authenticated:
        last_submission = Submission.query.filter_by(
            task_id=task_id, user_id=current_user.id
        ).order_by(Submission.submitted_at.desc()).first()

    return render_template('task.html',
                           task=t,
                           block_info=block_info,
                           last_submission=last_submission)


@app.route('/api/submit', methods=['POST'])
@login_required
def submit():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Нет данных'}), 400

    task_id = data.get('task_id')
    code = data.get('code', '').strip()

    if not task_id or not code:
        return jsonify({'error': 'Необходимо указать task_id и код'}), 400

    t = Task.query.get(task_id)
    if not t:
        return jsonify({'error': 'Задача не найдена'}), 404

    passed = False
    result_text = ''

    if t.task_type == 'python':
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                tmp_path = f.name

            proc = subprocess.run(
                ['python3', tmp_path],
                capture_output=True, text=True, timeout=10
            )
            os.unlink(tmp_path)

            output = proc.stdout.strip()
            stderr = proc.stderr.strip()

            if proc.returncode != 0:
                result_text = f'Ошибка выполнения:\n{stderr}'
                passed = False
            else:
                result_text = output
                expected = (t.expected_output or '').strip()
                passed = output == expected

        except subprocess.TimeoutExpired:
            result_text = 'Превышено время выполнения (10 секунд)'
            passed = False
        except Exception as e:
            result_text = f'Ошибка: {str(e)}'
            passed = False

    elif t.task_type == 'answer':
        answer = code.strip().lower()
        expected = (t.expected_output or '').strip().lower()
        passed = answer == expected
        result_text = code.strip()

    elif t.task_type in ('sql', 'html'):
        expected = (t.expected_output or '').strip().lower()
        answer = code.strip().lower()
        passed = expected in answer
        result_text = 'Ответ принят' if passed else 'Ответ не совпадает с ожидаемым'

    else:
        result_text = 'Неизвестный тип задачи'
        passed = False

    submission = Submission(
        user_id=current_user.id,
        task_id=task_id,
        code=code,
        result=result_text,
        passed=passed,
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'passed': passed,
        'result': result_text,
        'message': 'Верно! Задача решена.' if passed else 'Неверно. Попробуй ещё раз.',
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
