from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

BLOCKS = {
    'theory': {'name': 'Теория', 'icon': '📚', 'description': 'Основы Python, математические задачи и алгоритмическое мышление'},
    'algorithms': {'name': 'Алгоритмы', 'icon': '⚡', 'description': 'Сортировки, поиск, графы, динамическое программирование'},
    'data': {'name': 'Данные', 'icon': '📊', 'description': 'SQL-запросы, pandas, numpy и работа с данными'},
    'backend': {'name': 'Бэкенд', 'icon': '🔧', 'description': 'REST API, Flask, работа с базами данных и сервером'},
    'frontend': {'name': 'Фронтенд', 'icon': '🎨', 'description': 'HTML, CSS, JavaScript и создание интерфейсов'},
}


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submissions = db.relationship('Submission', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def solved_in_block(self, block):
        return Submission.query.filter_by(user_id=self.id, passed=True).join(Task).filter(Task.block == block).count()


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    block = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    task_type = db.Column(db.String(50), nullable=False)
    expected_output = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), default='easy')
    order_num = db.Column(db.Integer, default=0)
    submissions = db.relationship('Submission', backref='task', lazy=True)

    def solved_by(self, user_id):
        return Submission.query.filter_by(task_id=self.id, user_id=user_id, passed=True).first() is not None


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    code = db.Column(db.Text, nullable=True)
    result = db.Column(db.Text, nullable=True)
    passed = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


def seed_tasks():
    if Task.query.count() > 0:
        return

    tasks = [
        Task(block='theory', title='Привет, мир!', description='Напишите программу, которая выводит "Hello, World!" на экран.', task_type='python', expected_output='Hello, World!', difficulty='easy', order_num=1),
        Task(block='theory', title='Сумма двух чисел', description='Дано два числа a и b. Выведите их сумму.\nПример: a=3, b=5 → 8', task_type='python', expected_output='8', difficulty='easy', order_num=2),
        Task(block='theory', title='Факториал', description='Напишите программу вычисления факториала числа n.\nВходные данные: n=5\nВыходные данные: 120', task_type='python', expected_output='120', difficulty='medium', order_num=3),
        Task(block='theory', title='Числа Фибоначчи', description='Выведите первые 10 чисел Фибоначчи через пробел.', task_type='python', expected_output='0 1 1 2 3 5 8 13 21 34', difficulty='medium', order_num=4),
        Task(block='theory', title='Простое число', description='Является ли число 17 простым? Ответьте: True или False.', task_type='answer', expected_output='True', difficulty='easy', order_num=5),

        Task(block='algorithms', title='Сортировка пузырьком', description='Реализуйте сортировку пузырьком для списка [64, 25, 12, 22, 11].\nВыведите отсортированный список.', task_type='python', expected_output='[11, 12, 22, 25, 64]', difficulty='medium', order_num=1),
        Task(block='algorithms', title='Бинарный поиск', description='Реализуйте бинарный поиск элемента 7 в отсортированном списке [1, 3, 5, 7, 9, 11].\nВыведите индекс элемента.', task_type='python', expected_output='3', difficulty='medium', order_num=2),
        Task(block='algorithms', title='Разворот строки', description='Разверните строку "Arete LMS" без использования срезов.\nВыведите результат.', task_type='python', expected_output='SML etarA', difficulty='easy', order_num=3),
        Task(block='algorithms', title='Скобочная последовательность', description='Проверьте, является ли строка "({[]})" правильной скобочной последовательностью.\nВыведите True или False.', task_type='python', expected_output='True', difficulty='hard', order_num=4),

        Task(block='data', title='SELECT запрос', description='Напишите SQL-запрос для выборки всех пользователей из таблицы users, где возраст больше 18.\nСтруктура: id, name, age', task_type='sql', expected_output='SELECT * FROM users WHERE age > 18', difficulty='easy', order_num=1),
        Task(block='data', title='Среднее значение', description='Напишите SQL-запрос, который вернёт среднее значение столбца salary из таблицы employees.', task_type='sql', expected_output='SELECT AVG(salary) FROM employees', difficulty='easy', order_num=2),
        Task(block='data', title='Pandas DataFrame', description='Создайте DataFrame из словаря {"name": ["Alice", "Bob"], "age": [25, 30]} и выведите среднее значение столбца age.', task_type='python', expected_output='27.5', difficulty='medium', order_num=3),
        Task(block='data', title='GROUP BY', description='Напишите SQL-запрос, который считает количество пользователей по городам из таблицы users(id, name, city).', task_type='sql', expected_output='SELECT city, COUNT(*) FROM users GROUP BY city', difficulty='medium', order_num=4),

        Task(block='backend', title='Flask маршрут', description='Напишите Flask-маршрут для пути /hello, который возвращает JSON {"message": "Hello, World!"}.', task_type='python', expected_output='{"message": "Hello, World!"}', difficulty='easy', order_num=1),
        Task(block='backend', title='GET запрос', description='Напишите Flask-маршрут /users, который принимает GET-запрос и возвращает список пользователей в JSON.', task_type='python', expected_output='[{"id": 1, "name": "Alice"}]', difficulty='medium', order_num=2),
        Task(block='backend', title='POST запрос', description='Напишите Flask-маршрут /create, который принимает POST-запрос с JSON телом и возвращает статус создания.', task_type='python', expected_output='{"status": "created", "id": 1}', difficulty='medium', order_num=3),

        Task(block='frontend', title='Hello HTML', description='Напишите минимальную HTML-страницу с заголовком "Привет, мир!" в теге h1.', task_type='html', expected_output='<h1>Привет, мир!</h1>', difficulty='easy', order_num=1),
        Task(block='frontend', title='CSS кнопка', description='Напишите HTML-кнопку с классом "btn" и стилем: фиолетовый фон (#8b5cf6), белый текст, скруглённые углы 8px.', task_type='html', expected_output='background: #8b5cf6', difficulty='easy', order_num=2),
        Task(block='frontend', title='JavaScript счётчик', description='Напишите HTML-страницу со счётчиком: кнопка "+" увеличивает число, кнопка "-" уменьшает. Начальное значение: 0.', task_type='html', expected_output='counter', difficulty='medium', order_num=3),
    ]

    for task in tasks:
        db.session.add(task)
    db.session.commit()
