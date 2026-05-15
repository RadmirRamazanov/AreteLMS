from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from tasks import TASK_DEFINITIONS

db = SQLAlchemy()

BLOCKS = {
    "theory": {
        "name": "Теория",
        "icon": "📚",
        "description": (
            "Математика, системы счисления и логические задачи олимпиадного уровня"
        ),
    },
    "algorithms": {
        "name": "Алгоритмы",
        "icon": "⚡",
        "description": (
            "Сортировки, поиск, динамическое программирование и игровые задачи"
        ),
    },
    "data": {
        "name": "Данные",
        "icon": "📊",
        "description": (
            "SQL-запросы, анализ данных и работа с Python-структурами"
        ),
    },
    "backend": {
        "name": "Бэкенд",
        "icon": "🔧",
        "description": (
            "REST API, Flask, алгоритмы на Python с правильным вводом/выводом"
        ),
    },
    "frontend": {
        "name": "Фронтенд",
        "icon": "🎨",
        "description": (
            "HTML, CSS, JavaScript и строгая валидация интерфейсов"
        ),
    },
}


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    submissions = db.relationship("Submission", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def solved_in_block(self, block):
        return (
            Submission.query.filter_by(user_id=self.id, passed=True)
            .join(Task)
            .filter(Task.block == block)
            .count()
        )


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    block = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    task_type = db.Column(db.String(50), nullable=False)
    expected_output = db.Column(db.Text, nullable=True)
    test_cases_json = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), default="medium")
    order_num = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=100)
    attempts_limit = db.Column(db.Integer, nullable=True)
    time_limit = db.Column(db.String(40), nullable=True)
    memory_limit = db.Column(db.String(40), nullable=True)
    input_format = db.Column(db.String(80), nullable=True)
    output_format = db.Column(db.String(80), nullable=True)
    submissions = db.relationship("Submission", backref="task", lazy=True)

    def solved_by(self, user_id):
        return (
            Submission.query.filter_by(
                task_id=self.id, user_id=user_id, passed=True
            ).first()
            is not None
        )


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    code = db.Column(db.Text, nullable=True)
    result = db.Column(db.Text, nullable=True)
    passed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.now)


def sync_tasks():
    known_titles = {spec["title"] for spec in TASK_DEFINITIONS}

    for spec in TASK_DEFINITIONS:
        matches = Task.query.filter_by(title=spec["title"]).order_by(Task.id).all()
        task = matches[0] if matches else None
        for duplicate in matches[1:]:
            db.session.delete(duplicate)
        if task is None:
            task = Task()
            db.session.add(task)
        for key, value in spec.items():
            setattr(task, key, value)

    for orphan in Task.query.all():
        if orphan.title not in known_titles:
            db.session.delete(orphan)

    db.session.commit()


def seed_tasks():
    sync_tasks()
