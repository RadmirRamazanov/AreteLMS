import os
import json
import subprocess
import tempfile
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db, User, Task, Submission, BLOCKS, seed_tasks

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', '955c705c4f8ae555ee5ba3ce34ebb79812f63f1b0055d0df700cf4803a3feea6')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arete_lms.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


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

        login_user(user, remember=True)
        session.permanent = True
        next_page = request.args.get('next') or request.form.get('next')
        return redirect(next_page or url_for('lms', block_key='theory'))

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
            login_user(user, remember=True)
            session.permanent = True
            next_page = request.args.get('next') or request.form.get('next')
            return redirect(next_page or url_for('lms', block_key='theory'))
        else:
            return render_template('login.html', error='Неверный email или пароль.')

    return render_template('login.html', error=None)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


def _build_lms_context(block_key):
    if block_key not in BLOCKS:
        return None

    block_info = BLOCKS[block_key]
    tasks = Task.query.filter_by(block=block_key).order_by(Task.order_num).all()

    tasks_data = []
    for t in tasks:
        solved = False
        last_verdict = None
        verdict_score = None
        if current_user.is_authenticated:
            last_sub = Submission.query.filter_by(
                task_id=t.id, user_id=current_user.id
            ).order_by(Submission.submitted_at.desc()).first()
            if last_sub:
                if last_sub.passed:
                    solved = True
                    verdict_score = last_sub.score if last_sub.score is not None else 100
                    last_verdict = 'accepted'
                else:
                    last_verdict = 'rejected'
                    verdict_score = last_sub.score if last_sub.score is not None else 0
        tasks_data.append({'task': t, 'solved': solved, 'last_verdict': last_verdict, 'verdict_score': verdict_score})

    total = len(tasks)
    solved_count = sum(1 for td in tasks_data if td['solved'])

    all_blocks = []
    total_solved = 0
    total_tasks = 0
    for key, info in BLOCKS.items():
        count = Task.query.filter_by(block=key).count()
        s = current_user.solved_in_block(key) if current_user.is_authenticated else 0
        all_blocks.append({'key': key, 'name': info['name'], 'icon': info['icon'], 'count': count, 'solved': s})
        total_solved += s
        total_tasks += count

    return dict(block_key=block_key, block_info=block_info, tasks_data=tasks_data,
                total=total, solved_count=solved_count,
                all_blocks=all_blocks, total_solved=total_solved, total_tasks=total_tasks)


@app.route('/lms')
def lms_root():
    return redirect(url_for('lms', block_key='theory'))


@app.route('/lms/<block_key>')
def lms(block_key):
    ctx = _build_lms_context(block_key)
    if ctx is None:
        return redirect(url_for('lms_root'))
    return render_template('lms.html', **ctx)


@app.route('/block/<block_key>')
def block(block_key):
    if block_key not in BLOCKS:
        return redirect(url_for('index'))

    block_info = BLOCKS[block_key]
    tasks = Task.query.filter_by(block=block_key).order_by(Task.order_num).all()

    tasks_data = []
    for t in tasks:
        solved = False
        last_verdict = None
        verdict_score = None
        if current_user.is_authenticated:
            last_sub = Submission.query.filter_by(
                task_id=t.id, user_id=current_user.id
            ).order_by(Submission.submitted_at.desc()).first()
            if last_sub:
                if last_sub.passed:
                    solved = True
                    verdict_score = last_sub.score if last_sub.score is not None else 100
                    last_verdict = 'accepted'
                else:
                    last_verdict = 'rejected'
                    verdict_score = last_sub.score if last_sub.score is not None else 0
        tasks_data.append({
            'task': t,
            'solved': solved,
            'last_verdict': last_verdict,
            'verdict_score': verdict_score,
        })

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
    submissions_count = 0
    if current_user.is_authenticated:
        last_submission = Submission.query.filter_by(
            task_id=task_id, user_id=current_user.id
        ).order_by(Submission.submitted_at.desc()).first()
        submissions_count = Submission.query.filter_by(
            task_id=task_id, user_id=current_user.id
        ).count()

    return render_template('task.html',
                           task=t,
                           block_info=block_info,
                           last_submission=last_submission,
                           submissions_count=submissions_count)


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

    if t.attempts_limit:
        used = Submission.query.filter_by(
            task_id=task_id, user_id=current_user.id
        ).count()
        if used >= t.attempts_limit:
            return jsonify({
                'error': f'Исчерпан лимит попыток ({t.attempts_limit}). Больше отправок нет.',
                'attempts_exceeded': True,
            }), 403

    test_cases = []
    if t.test_cases_json:
        try:
            test_cases = json.loads(t.test_cases_json)
        except Exception:
            test_cases = []
    if not test_cases and t.expected_output is not None:
        test_cases = [{'input': '', 'output': t.expected_output}]

    passed = False
    score = 0
    result_text = ''

    if t.task_type == 'python':
        passed_count = 0
        result_lines = []
        total_tc = len(test_cases)
        for i, tc in enumerate(test_cases):
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    tmp_path = f.name
                proc = subprocess.run(
                    ['python3', tmp_path],
                    input=tc.get('input', ''),
                    capture_output=True, text=True, timeout=10
                )
                os.unlink(tmp_path)
                output = proc.stdout.strip()
                expected = tc.get('output', '').strip()
                if proc.returncode != 0:
                    stderr = proc.stderr.strip()
                    result_lines.append(f'Тест {i+1}: Ошибка выполнения\n{stderr[:300]}')
                elif output == expected:
                    passed_count += 1
                    result_lines.append(f'Тест {i+1}: OK')
                else:
                    result_lines.append(
                        f'Тест {i+1}: Неверный ответ\nОжидалось: {expected}\nПолучено: {output}'
                    )
            except subprocess.TimeoutExpired:
                result_lines.append(f'Тест {i+1}: Превышено время выполнения (10 с)')
            except Exception as e:
                result_lines.append(f'Тест {i+1}: Ошибка: {str(e)}')

        score = int(passed_count / total_tc * 100) if total_tc > 0 else 0
        passed = (passed_count == total_tc and total_tc > 0)
        result_text = '\n'.join(result_lines)

    elif t.task_type == 'answer':
        answer = code.strip().lower()
        expected = (t.expected_output or '').strip().lower()
        passed = (answer == expected)
        score = 100 if passed else 0
        result_text = code.strip()

    elif t.task_type in ('sql', 'html'):
        expected = (t.expected_output or '').strip().lower()
        answer = code.strip().lower()
        passed = expected in answer
        score = 100 if passed else 0
        result_text = 'Ответ принят' if passed else 'Ответ не совпадает с ожидаемым'

    else:
        result_text = 'Неизвестный тип задачи'
        passed = False
        score = 0

    submission = Submission(
        user_id=current_user.id,
        task_id=task_id,
        code=code,
        result=result_text,
        passed=passed,
        score=score,
    )
    db.session.add(submission)
    db.session.commit()

    if passed:
        verdict_msg = f'Зачтено {score}/100 баллов'
    else:
        verdict_msg = 'Доработать'

    return jsonify({
        'passed': passed,
        'score': score,
        'result': result_text,
        'message': verdict_msg,
        'verdict': 'accepted' if passed else 'rejected',
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
