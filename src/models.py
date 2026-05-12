import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

BLOCKS = {
    'theory':     {'name': 'Теория',     'icon': '📚', 'description': 'Математика, системы счисления и логические задачи олимпиадного уровня'},
    'algorithms': {'name': 'Алгоритмы', 'icon': '⚡', 'description': 'Сортировки, поиск, динамическое программирование и игровые задачи'},
    'data':       {'name': 'Данные',     'icon': '📊', 'description': 'SQL-запросы, анализ данных и работа с Python-структурами'},
    'backend':    {'name': 'Бэкенд',    'icon': '🔧', 'description': 'REST API, Flask, алгоритмы на Python с правильным вводом/выводом'},
    'frontend':   {'name': 'Фронтенд',  'icon': '🎨', 'description': 'HTML, CSS, JavaScript и строгая валидация интерфейсов'},
}


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    first_name    = db.Column(db.String(50),  nullable=False)
    last_name     = db.Column(db.String(50),  nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    submissions   = db.relationship('Submission', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def solved_in_block(self, block):
        return (
            Submission.query
            .filter_by(user_id=self.id, passed=True)
            .join(Task)
            .filter(Task.block == block)
            .count()
        )


class Task(db.Model):
    __tablename__ = 'tasks'
    id              = db.Column(db.Integer, primary_key=True)
    block           = db.Column(db.String(50),  nullable=False)
    title           = db.Column(db.String(200), nullable=False)
    description     = db.Column(db.Text,        nullable=False)
    task_type       = db.Column(db.String(50),  nullable=False)  # python / sql / html / answer
    expected_output = db.Column(db.Text,        nullable=True)   # for fallback / answer tasks
    test_cases_json = db.Column(db.Text,        nullable=True)   # JSON [{input, output}]
    difficulty      = db.Column(db.String(20),  default='medium')
    order_num       = db.Column(db.Integer,     default=0)
    max_score       = db.Column(db.Integer,     default=100)
    attempts_limit  = db.Column(db.Integer,     nullable=True)   # None = unlimited
    # display-only constraint fields
    time_limit      = db.Column(db.String(40),  nullable=True)
    memory_limit    = db.Column(db.String(40),  nullable=True)
    input_format    = db.Column(db.String(80),  nullable=True)
    output_format   = db.Column(db.String(80),  nullable=True)
    submissions     = db.relationship('Submission', backref='task', lazy=True)

    def solved_by(self, user_id):
        return (
            Submission.query
            .filter_by(task_id=self.id, user_id=user_id, passed=True)
            .first() is not None
        )


class Submission(db.Model):
    __tablename__ = 'submissions'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id      = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    code         = db.Column(db.Text,    nullable=True)
    result       = db.Column(db.Text,    nullable=True)
    passed       = db.Column(db.Boolean, default=False)
    score        = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


def _tc(cases):
    """Shorthand: convert list of (input, output) tuples to JSON string."""
    return json.dumps([{'input': inp, 'output': out} for inp, out in cases])


def seed_tasks():
    if Task.query.count() > 0:
        return

    tasks = [

        # ══════════════════════════════════════════════════════════
        # ТЕОРИЯ
        # ══════════════════════════════════════════════════════════
        Task(
            block='theory',
            title='Большая цифра',
            difficulty='hard',
            order_num=1,
            task_type='answer',
            attempts_limit=2,
            expected_output='238',
            description='''\
В 250-ричной системе счисления записано 12-значное число, в котором цифра X встречается
на позициях 3, 6 и 9 (считая с конца, начиная с 1):

  [ 9 ][ 8 ][ X ][ 7 ][ 6 ][ X ][ 5 ][ 1 ][ X ][ 4 ][ 3 ][ 5 ]
   №12  №11  №10  №9   №8   №7   №6   №5   №4   №3   №2   №1

Все остальные цифры фиксированы. Найди наибольшую цифру X (0 ≤ X ≤ 249),
при которой данное 250-ричное число делится на 147.

Внимание: только 2 попытки!

Введи единственное число — ответ.
''',
        ),

        # ══════════════════════════════════════════════════════════
        # АЛГОРИТМЫ
        # ══════════════════════════════════════════════════════════
        Task(
            block='algorithms',
            title='Архиватор битовых строк',
            difficulty='medium',
            order_num=1,
            task_type='python',
            time_limit='1 с',
            memory_limit='256 МБ',
            input_format='stdin',
            output_format='stdout',
            test_cases_json=_tc([
                ('00011000',  '3 2 3'),
                ('1110',      '0 3 1'),
                ('0',         '1'),
                ('10101',     '0 1 1 1 1 1'),
                ('000',       '3'),
            ]),
            description='''\
Реализуй архиватор битовых строк на основе кодирования длин серий (RLE).

Входная строка состоит только из символов '0' и '1'. Архив — список длин
последовательных одинаковых символов, начиная с нулей. Если строка начинается
с '1', первое число в списке равно 0.

Формат ввода:
  Одна строка — битовая строка (1 ≤ длина ≤ 10⁶).

Формат вывода:
  Числа длин серий через пробел.

Примеры:
  Ввод: 00011000   Вывод: 3 2 3
  Ввод: 1110        Вывод: 0 3 1
  Ввод: 0            Вывод: 1
''',
        ),

        Task(
            block='algorithms',
            title='Алиса и ловля насекомых',
            difficulty='hard',
            order_num=2,
            task_type='python',
            time_limit='2 с',
            memory_limit='256 МБ',
            input_format='stdin',
            output_format='stdout',
            test_cases_json=_tc([
                ('4\n3 9 1 2', '11'),
                ('2\n5 3',     '5'),
                ('1\n7',       '7'),
                ('6\n1 2 3 4 5 6', '12'),
                ('4\n1 1 1 1',     '2'),
            ]),
            description='''\
N насекомых расположены в ряд, у каждого своя ценность. Алиса и Боб
по очереди ловят насекомых (Алиса ходит первой). В каждый ход игрок
берёт насекомое с любого конца ряда. Оба играют оптимально — каждый
максимизирует свою суммарную ценность. Найди суммарную ценность насекомых
Алисы.

Формат ввода:
  Строка 1: N (1 ≤ N ≤ 1000)
  Строка 2: N чисел — ценности насекомых (1 ≤ ai ≤ 10⁹)

Формат вывода:
  Одно число — суммарная ценность насекомых Алисы.

Пример:
  Ввод:        Вывод:
  4            11
  3 9 1 2
''',
        ),

        Task(
            block='algorithms',
            title='Винни-Пух и шарики',
            difficulty='medium',
            order_num=3,
            task_type='python',
            time_limit='1 с',
            memory_limit='256 МБ',
            input_format='stdin',
            output_format='stdout',
            test_cases_json=_tc([
                ('3\n3 2 1', 'YES'),
                ('2\n4 1',   'NO'),
                ('1\n1',     'YES'),
                ('3\n1 1 5', 'NO'),
                ('4\n3 3 2 2', 'YES'),
            ]),
            description='''\
Винни-Пух хочет расставить шарики K цветов в ряд так, чтобы никакие два
соседних шарика не были одного цвета. Известно количество шариков каждого цвета.

Определи, возможно ли такое расположение.

Формат ввода:
  Строка 1: K (1 ≤ K ≤ 100) — количество цветов
  Строка 2: K чисел — количество шариков каждого цвета (1 ≤ ci ≤ 10⁶)

Формат вывода:
  YES, если расположение возможно, NO иначе.

Примеры:
  Ввод: 3 / 3 2 1  →  YES
  Ввод: 2 / 4 1    →  NO
''',
        ),

        Task(
            block='algorithms',
            title='Бизнес-центр',
            difficulty='hard',
            order_num=4,
            task_type='python',
            time_limit='1 с',
            memory_limit='256 МБ',
            input_format='stdin',
            output_format='stdout',
            test_cases_json=_tc([
                ('3\n0 30\n5 10\n15 20', '2'),
                ('3\n7 10\n2 4\n0 1',    '1'),
                ('2\n1 5\n2 6',          '2'),
                ('1\n0 100',             '1'),
                ('4\n1 4\n2 5\n7 9\n3 6', '3'),
            ]),
            description='''\
В бизнес-центре проводятся N совещаний. Каждое совещание занимает переговорную
от времени start до времени end (включительно). Совещания, начинающиеся в момент
освобождения комнаты, могут её использовать.

Найди минимальное количество переговорных комнат для проведения всех совещаний.

Формат ввода:
  Строка 1: N (1 ≤ N ≤ 10⁵)
  Следующие N строк: start end (0 ≤ start < end ≤ 10⁶)

Формат вывода:
  Одно число — минимальное количество комнат.

Пример:
  Ввод:      Вывод:
  3          2
  0 30
  5 10
  15 20
''',
        ),

        # ══════════════════════════════════════════════════════════
        # ДАННЫЕ
        # ══════════════════════════════════════════════════════════
        Task(
            block='data',
            title='Внедрённые внедрения',
            difficulty='medium',
            order_num=1,
            task_type='python',
            time_limit='1 с',
            memory_limit='256 МБ',
            input_format='stdin',
            output_format='stdout',
            test_cases_json=_tc([
                (
                    "3\nHello world\nSELECT * FROM users WHERE id='1' OR 1=1\nTest",
                    '1'
                ),
                (
                    "4\nDROP TABLE users;\nnormal text\nUNION SELECT password FROM users\nalice@example.com",
                    '2'
                ),
                (
                    "2\nSELECT name FROM products\nINSERT INTO log VALUES (1)",
                    '2'
                ),
                (
                    "1\nsafe input only",
                    '0'
                ),
            ]),
            description='''\
Система безопасности проверяет входящие строки на SQL-инъекции.
Строка считается опасной, если она содержит хотя бы одно из ключевых слов
(без учёта регистра):

  DROP, DELETE, INSERT, UPDATE, UNION, OR 1=1, '--

Подсчитай количество опасных строк среди N входных строк.

Формат ввода:
  Строка 1: N (1 ≤ N ≤ 10⁴)
  Следующие N строк — входные строки.

Формат вывода:
  Одно число — количество опасных строк.

Пример:
  Ввод:                                         Вывод:
  3                                             1
  Hello world
  SELECT * FROM users WHERE id=\'1\' OR 1=1
  Test
''',
        ),

        Task(
            block='data',
            title='Склонированные клоны',
            difficulty='medium',
            order_num=2,
            task_type='sql',
            expected_output='group by name, birth_date having count',
            description='''\
В базе данных есть таблица users со столбцами: id, name, birth_date.

Некоторые пользователи были случайно продублированы при импорте данных —
у них совпадают имя (name) и дата рождения (birth_date).

Напиши SQL-запрос, который выводит все (name, birth_date)-комбинации,
встречающиеся более одного раза, вместе с количеством дубликатов.

Ожидаемые столбцы в результате: name, birth_date, cnt
(cnt — количество строк с такой комбинацией).

Отсортируй по cnt DESC.

Подсказка: используй GROUP BY ... HAVING COUNT(*) > 1.
''',
        ),

        Task(
            block='data',
            title='Вездесущая чашка',
            difficulty='easy',
            order_num=3,
            task_type='python',
            time_limit='1 с',
            memory_limit='256 МБ',
            input_format='stdin',
            output_format='stdout',
            test_cases_json=_tc([
                (
                    '4\nalice 09:15\nbob 09:42\nalice 14:30\nbob 09:58',
                    '9'
                ),
                (
                    '2\nuser1 08:00\nuser2 08:59',
                    '8'
                ),
                (
                    '5\na 23:00\nb 23:59\nc 00:01\nd 23:30\ne 23:10',
                    '23'
                ),
                (
                    '1\nonly 12:00',
                    '12'
                ),
            ]),
            description='''\
Кофейня записывает визиты клиентов. Каждая запись содержит имя клиента
и время визита в формате ЧЧ:ММ. Найди час (0–23), в который кофейня
была наиболее популярна (больше всего визитов). При ничьей выведи
наименьший час.

Формат ввода:
  Строка 1: N (1 ≤ N ≤ 10⁵)
  Следующие N строк: имя время (например: alice 09:15)

Формат вывода:
  Одно число — самый популярный час.

Пример:
  Ввод:          Вывод:
  4              9
  alice 09:15
  bob 09:42
  alice 14:30
  bob 09:58
''',
        ),

        # ══════════════════════════════════════════════════════════
        # БЭКЕНД
        # ══════════════════════════════════════════════════════════
        Task(
            block='backend',
            title='Планеты в зоне жизни',
            difficulty='medium',
            order_num=1,
            task_type='python',
            time_limit='1 с',
            memory_limit='256 МБ',
            input_format='stdin',
            output_format='stdout',
            test_cases_json=_tc([
                ('1.0 1.0',  'YES'),
                ('4.0 1.0',  'NO'),
                ('0.36 0.6', 'YES'),
                ('1.0 2.0',  'NO'),
                ('9.0 3.0',  'YES'),
            ]),
            description='''\
Зона жизни (обитаемая зона) звезды — диапазон расстояний, при котором
на планете может существовать жидкая вода. Формулы для границ зоны:

  inner = sqrt(L / 1.1)
  outer = sqrt(L / 0.53)

где L — светимость звезды в единицах светимости Солнца.

По заданной светимости звезды L и расстоянию от звезды до планеты D (в а.е.)
определи, находится ли планета в зоне жизни: inner ≤ D ≤ outer.

Формат ввода:
  Одна строка: два числа с плавающей точкой L и D.

Формат вывода:
  YES или NO.

Примеры:
  1.0 1.0  →  YES   (зона: 0.953 – 1.374 а.е.)
  4.0 1.0  →  NO    (зона: 1.905 – 2.748 а.е.)
''',
        ),

        Task(
            block='backend',
            title='Поставщики',
            difficulty='hard',
            order_num=2,
            task_type='python',
            time_limit='1 с',
            memory_limit='256 МБ',
            input_format='stdin',
            output_format='stdout',
            test_cases_json=_tc([
                (
                    '3\napple FarmA 1.50\napple FarmB 1.20\nbanana FarmC 0.80',
                    'apple FarmB 1.20\nbanana FarmC 0.80'
                ),
                (
                    '4\nrice RiceWorld 0.90\nrice BulkBuy 0.75\nrice GrainCo 0.80\nwheat GrainCo 0.60',
                    'rice BulkBuy 0.75\nwheat GrainCo 0.60'
                ),
                (
                    '1\ncarrot GardenFarm 2.00',
                    'carrot GardenFarm 2.00'
                ),
            ]),
            description='''\
Компания закупает продукты у разных поставщиков. Для каждого продукта
нужно выбрать поставщика с наименьшей ценой.

Формат ввода:
  Строка 1: N (1 ≤ N ≤ 10⁵) — количество предложений
  Следующие N строк: product supplier price
    (product и supplier — строки без пробелов, price — число с 2 знаками)

Формат вывода:
  По одной строке для каждого уникального продукта в алфавитном порядке:
    product supplier price
  Цену выводи с 2 знаками после запятой.

Пример:
  Ввод:               Вывод:
  3                   apple FarmB 1.20
  apple FarmA 1.50    banana FarmC 0.80
  apple FarmB 1.20
  banana FarmC 0.80
''',
        ),

        # ══════════════════════════════════════════════════════════
        # ФРОНТЕНД
        # ══════════════════════════════════════════════════════════
        Task(
            block='frontend',
            title='Педантичный хомяк',
            difficulty='medium',
            order_num=1,
            task_type='html',
            expected_output='addeventlistener',
            description='''\
Хомяк Хрустик очень педантичен и проверяет каждый символ формы регистрации.
Создай HTML-страницу с формой, где хомяк (в виде сообщения об ошибке)
критикует каждый недочёт в реальном времени.

Требования к форме:
  1. Поле «Имя пользователя»:
     – Минимум 3, максимум 20 символов
     – Только латинские буквы и цифры (a-z, A-Z, 0-9)
  2. Поле «Пароль»:
     – Минимум 8 символов
     – Содержит заглавную букву, строчную букву, цифру и спецсимвол (!@#$%^&*)
  3. Для каждого поля — блок с сообщением об ошибке, который появляется
     при вводе и скрывается при выполнении требований.
  4. Валидация работает мгновенно (oninput или addEventListener('input',...)).
  5. Кнопка «Отправить» заблокирована (disabled), пока оба поля невалидны.

Оцениваются: наличие addEventListener или oninput, логика проверки полей,
динамическая блокировка кнопки.
''',
        ),
    ]

    for t in tasks:
        db.session.add(t)
    db.session.commit()
