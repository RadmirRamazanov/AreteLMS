from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from config import MIN_PASSWORD_LENGTH, MIN_USERNAME_LENGTH
from models import BLOCKS, Submission, Task, User, db

web_bp = Blueprint("web", __name__)


def _get_task_status(task_id, user_id):
    last_sub = (
        Submission.query.filter_by(task_id=task_id, user_id=user_id)
        .order_by(Submission.submitted_at.desc())
        .first()
    )
    if not last_sub:
        return False, None, None

    if last_sub.passed:
        return True, "accepted", last_sub.score if last_sub.score is not None else 100

    return False, "rejected", last_sub.score if last_sub.score is not None else 0


def _build_tasks_data(tasks, user_id):
    result = []
    for task in tasks:
        solved = False
        last_verdict = None
        verdict_score = None

        if user_id is not None:
            solved, last_verdict, verdict_score = _get_task_status(task.id, user_id)

        result.append(
            {
                "task": task,
                "solved": solved,
                "last_verdict": last_verdict,
                "verdict_score": verdict_score,
            }
        )
    return result


def _build_all_blocks_summary():
    all_blocks = []
    total_solved = 0
    total_tasks = 0

    user_id = current_user.id if current_user.is_authenticated else None

    for key, info in BLOCKS.items():
        count = Task.query.filter_by(block=key).count()
        solved = current_user.solved_in_block(key) if user_id else 0
        all_blocks.append(
            {
                "key": key,
                "name": info["name"],
                "icon": info["icon"],
                "count": count,
                "solved": solved,
            }
        )
        total_solved += solved
        total_tasks += count

    return all_blocks, total_solved, total_tasks


@web_bp.route("/")
def index():
    blocks_data = []
    for key, info in BLOCKS.items():
        count = Task.query.filter_by(block=key).count()
        solved = (
            current_user.solved_in_block(key) if current_user.is_authenticated else 0
        )
        blocks_data.append(
            {
                "key": key,
                "name": info["name"],
                "icon": info["icon"],
                "description": info["description"],
                "count": count,
                "solved": solved,
            }
        )
    return render_template("index.html", blocks=blocks_data)


@web_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("web.index"))

    if request.method == "POST":
        first_name = request.form.get("firstName", "").strip()
        last_name = request.form.get("lastName", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirmPassword", "")

        errors = _validate_registration(
            first_name, last_name, username, email, password, confirm_password
        )

        if errors:
            return render_template(
                "register.html", errors=errors, form_data=request.form
            )

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
        next_page = request.args.get("next") or request.form.get("next")
        return redirect(next_page or url_for("web.lms", block_key="theory"))

    return render_template("register.html", errors=[], form_data={})


def _validate_registration(first_name, last_name, username, email, password, confirm_password):
    errors = []

    if not first_name or not last_name:
        errors.append("Введите имя и фамилию.")
    if not username or len(username) < MIN_USERNAME_LENGTH:
        errors.append(
            f"Имя пользователя должно быть не менее {MIN_USERNAME_LENGTH} символов."
        )
    if not email or "@" not in email:
        errors.append("Введите корректный email.")
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(
            f"Пароль должен содержать не менее {MIN_PASSWORD_LENGTH} символов."
        )
    if password != confirm_password:
        errors.append("Пароли не совпадают.")
    if User.query.filter_by(username=username).first():
        errors.append("Имя пользователя уже занято.")
    if User.query.filter_by(email=email).first():
        errors.append("Email уже зарегистрирован.")

    return errors


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("web.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            session.permanent = True
            next_page = request.args.get("next") or request.form.get("next")
            return redirect(next_page or url_for("web.lms", block_key="theory"))

        return render_template("login.html", error="Неверный email или пароль.")

    return render_template("login.html", error=None)


@web_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.index"))


@web_bp.route("/lms")
def lms_root():
    return redirect(url_for("web.lms", block_key="theory"))


@web_bp.route("/lms/<block_key>")
def lms(block_key):
    if block_key not in BLOCKS:
        return redirect(url_for("web.lms_root"))

    block_info = BLOCKS[block_key]
    tasks = Task.query.filter_by(block=block_key).order_by(Task.order_num).all()
    user_id = current_user.id if current_user.is_authenticated else None
    tasks_data = _build_tasks_data(tasks, user_id)

    total = len(tasks)
    solved_count = sum(1 for td in tasks_data if td["solved"])

    all_blocks, total_solved, total_tasks = _build_all_blocks_summary()

    return render_template(
        "lms.html",
        block_key=block_key,
        block_info=block_info,
        tasks_data=tasks_data,
        total=total,
        solved_count=solved_count,
        all_blocks=all_blocks,
        total_solved=total_solved,
        total_tasks=total_tasks,
    )


@web_bp.route("/block/<block_key>")
def block(block_key):
    if block_key not in BLOCKS:
        return redirect(url_for("web.index"))

    block_info = BLOCKS[block_key]
    tasks = Task.query.filter_by(block=block_key).order_by(Task.order_num).all()
    user_id = current_user.id if current_user.is_authenticated else None
    tasks_data = _build_tasks_data(tasks, user_id)

    total = len(tasks)
    solved_count = sum(1 for td in tasks_data if td["solved"])

    return render_template(
        "block.html",
        block_key=block_key,
        block_info=block_info,
        tasks_data=tasks_data,
        total=total,
        solved_count=solved_count,
    )


@web_bp.route("/task/<int:task_id>")
def task(task_id):
    t = Task.query.get_or_404(task_id)
    block_info = BLOCKS.get(t.block, {})

    last_submission = None
    submissions_count = 0

    if current_user.is_authenticated:
        last_submission = (
            Submission.query.filter_by(task_id=task_id, user_id=current_user.id)
            .order_by(Submission.submitted_at.desc())
            .first()
        )
        submissions_count = Submission.query.filter_by(
            task_id=task_id, user_id=current_user.id
        ).count()

    return render_template(
        "task.html",
        task=t,
        block_info=block_info,
        last_submission=last_submission,
        submissions_count=submissions_count,
    )
