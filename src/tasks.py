import json


def _cases(pairs):
    return json.dumps([{"input": i, "output": o} for i, o in pairs])


TASK_DEFINITIONS = [
    {
        "block": "theory",
        "title": "Большая цифра",
        "difficulty": "easy",
        "order_num": 1,
        "task_type": "answer",
        "attempts_limit": 3,
        "expected_output": "238",
        "time_limit": None,
        "memory_limit": None,
        "input_format": None,
        "output_format": None,
        "test_cases_json": None,
        "description": """\
<h3>Большая цифра</h3>
<p>Дано выражение, записанное в <strong>250-ричной</strong> системе счисления, в котором одна из цифр
каждого числа заменена на <strong>x</strong> (цифра <strong>x</strong> имеет одно и то же значение в каждом числе):</p>
<pre>98x76x5 + 1x435</pre>
<p>Определите <strong>наибольшее</strong> значение <strong>x</strong> (0 ≤ x ≤ 249), при котором значение выражения
кратно числу <strong>147</strong>.</p>
<p>В ответ запишите <strong>только число</strong>. Решение прикладывать не нужно.</p>
<p><strong>Важно:</strong> у вас есть только <strong>2 попытки</strong>. Засчитывается лучший результат.</p>
""",
    },
    {
        "block": "theory",
        "title": "Архиватор битовых строк",
        "difficulty": "hard",
        "order_num": 2,
        "task_type": "python",
        "time_limit": "1 секунда",
        "memory_limit": "64 Мб",
        "input_format": "stdin",
        "output_format": "stdout",
        "attempts_limit": None,
        "expected_output": None,
        "test_cases_json": _cases(
            [
                ("01001", "0 1 0 2\n0.625000"),
                ("0", "0\n1.000000"),
                ("1110", "1 2 0\n0.800000"),
                ("10101", "1 0 2 1\n0.625000"),
                ("000", "0 2\n1.000000"),
            ]
        ),
        "description": """\
<h3>Архиватор битовых строк</h3>
<p><strong>Ограничение времени:</strong> 1 с &nbsp;|&nbsp; <strong>Память:</strong> 64 Мб</p>
<p>Для сжатия строк из символов <code>0</code> и <code>1</code> используется алгоритм, похожий на LZW.</p>
<h4>1. Инициализация таблицы</h4>
<ul>
<li><code>"0" → 0</code>, <code>"1" → 1</code></li>
<li>Следующий свободный код — <strong>2</strong></li>
</ul>
<h4>2. Процесс кодирования</h4>
<p>Пусть <code>P</code> — текущая подстрока (в начале пустая). Для каждого символа <code>C</code>:</p>
<ul>
<li>если <code>P+C</code> уже в таблице → <code>P = P+C</code>;</li>
<li>иначе → вывести код для <code>P</code>, добавить <code>P+C</code> с новым кодом, <code>P = C</code>.</li>
</ul>
<p>После всех символов вывести код для оставшегося <code>P</code>.</p>
<h4>3. Битовое представление</h4>
<p>Начинаем с <strong>1 бита</strong> на код. Когда в таблице появляется код со значением <code>2<sup>k</sup></code>,
все <em>последующие</em> коды кодируются <code>k+1</code> битами.</p>
<h4>Формат ввода</h4>
<p>Одна строка <code>S</code> из <code>0</code> и <code>1</code>.</p>
<h4>Формат вывода</h4>
<p>Две строки:</p>
<ol>
<li>коды через пробел;</li>
<li>коэффициент сжатия = (длина строки в битах) / (сумма бит всех кодов), 6 знаков после запятой.</li>
</ol>
<h4>Пример</h4>
<pre>Ввод:  01001
Вывод: 0 1 0 2
       0.625000</pre>
<p><em>Разбор:</em> коды [0,1,0,2], биты 1+2+2+3=8, коэффициент 5/8=0.625.</p>
""",
    },
    {
        "block": "algorithms",
        "title": "Алиса и ловля насекомых",
        "difficulty": "medium",
        "order_num": 1,
        "task_type": "python",
        "time_limit": "1 секунда",
        "memory_limit": "256 Мб",
        "input_format": "stdin",
        "output_format": "stdout",
        "attempts_limit": None,
        "expected_output": None,
        "test_cases_json": _cases(
            [
                ("3 6 8 7", "3"),
                ("5 4 4 5", "-1"),
                ("1 1 10 5", "1"),
                ("10 2 9 5", "8"),
                ("1000000 1 1000000 2", "2"),
            ]
        ),
        "description": """\
<h3>Алиса и ловля насекомых</h3>
<p><strong>Время:</strong> 1 с &nbsp;|&nbsp; <strong>Память:</strong> 256 Мб</p>
<p>На планете Шелезяка живут A-ножки (по <strong>A</strong> ног) и B-букашки (по <strong>B</strong> ног).
Алиса поймала <strong>N</strong> A-ножек, B-букашек пока нет.</p>
<p>Найдите <strong>минимальное</strong> число B-букашек, которое нужно поймать, чтобы среднее число ног
у всех пойманных насекомых стало <strong>не меньше C</strong>. Если невозможно — выведите <code>-1</code>.</p>
<h4>Формат ввода</h4>
<p>Четыре целых: <code>N A B C</code> (1 ≤ N,A,B,C ≤ 10<sup>6</sup>).</p>
<h4>Формат вывода</h4>
<p>Одно целое число.</p>
<h4>Примеры</h4>
<pre>Ввод: 3 6 8 7   →  3
Ввод: 5 4 4 5   →  -1</pre>
<p><em>Пояснение к примеру 1:</em> 3·6 + 3·8 = 42 ноги на 6 насекомых → среднее 7.</p>
<p><em>К примеру 2:</em> у обоих видов по 4 ноги, среднее всегда 4 &lt; 5.</p>
""",
    },
    {
        "block": "algorithms",
        "title": "Винни-Пух и шарики",
        "difficulty": "medium",
        "order_num": 2,
        "task_type": "python",
        "time_limit": "0.5 секунд",
        "memory_limit": "256 Мб",
        "input_format": "stdin",
        "output_format": "stdout",
        "attempts_limit": None,
        "expected_output": None,
        "test_cases_json": _cases(
            [
                ("1\n6 1 3", "5"),
                ("1\n1 2 6", "4"),
                ("2\n6 1 3\n1 2 6", "5\n4"),
                ("3\n10 2 1\n5 3 2\n20 1 5", "3\n2\n8"),
            ]
        ),
        "description": """\
<h3>Винни-Пух и шарики</h3>
<p><strong>Время:</strong> 0.5 с &nbsp;|&nbsp; <strong>Память:</strong> 256 Мб</p>
<p>Винни-Пух весит <strong>N</strong> г. Если взять <strong>k</strong> шариков, подъёмная сила —
<code>k²·A</code> граммов, но каждый шарик весит <strong>B</strong> граммов (чистая сила: <code>k²·A − k·B</code>).</p>
<p>Для <strong>T</strong> независимых тестов найдите минимальное <strong>k</strong>, при котором медведь поднимается в воздух.</p>
<h4>Формат ввода</h4>
<p><code>T</code>, затем <code>T</code> строк: <code>N A B</code> (1 ≤ N,A,B ≤ 10<sup>6</sup>).</p>
<h4>Формат вывода</h4>
<p>По одному числу на тест.</p>
<pre>Пример 1:  N=6, A=1, B=3  →  k=5
Пример 2:  N=1, A=2, B=6  →  k=4</pre>
""",
    },
    {
        "block": "algorithms",
        "title": "Бизнес-центр",
        "difficulty": "hard",
        "order_num": 3,
        "task_type": "python",
        "time_limit": "1.5 секунд",
        "memory_limit": "256 Мб",
        "input_format": "stdin",
        "output_format": "stdout",
        "attempts_limit": None,
        "expected_output": None,
        "test_cases_json": _cases(
            [
                ("2 3 4\n1 100 1\n1 1 1", "7"),
                ("2 2 2\n1 5\n2 6", "10"),
                ("1 1 3\n7", "21"),
            ]
        ),
        "description": """\
<h3>Бизнес-центр</h3>
<p><strong>Время:</strong> 1.5 с &nbsp;|&nbsp; <strong>Память:</strong> 256 Мб</p>
<p><strong>K</strong> этажей, на каждом сетка <strong>N×M</strong> офисов. Старт: (1;1) на 1-м этаже.
Финиш: (N;M) на K-м этаже.</p>
<p>За ход можно:</p>
<ul>
<li>перейти на офис с координатой <strong>j+1</strong> (восток);</li>
<li>перейти на офис с координатой <strong>i+1</strong> (юг);</li>
<li>подняться на лифте на этаж выше (те же i, j).</li>
</ul>
<p>При входе в офис (i;j) на <em>любом</em> этаже платите <code>A<sub>ij</sub></code> рублей (включая старт).</p>
<h4>Формат ввода</h4>
<p><code>N M K</code>, затем матрица <code>A</code> (0 ≤ A<sub>ij</sub> ≤ 1000).</p>
<h4>Формат вывода</h4>
<p>Минимальная суммарная стоимость пути.</p>
<pre>2 3 4
1 100 1
1 1 1
→ 7</pre>
""",
    },
    {
        "block": "data",
        "title": "Внедрённые внедрения",
        "difficulty": "easy",
        "order_num": 1,
        "task_type": "answer",
        "time_limit": "1 секунда",
        "memory_limit": "64 Мб",
        "input_format": None,
        "output_format": None,
        "attempts_limit": 2,
        "expected_output": "professor_prank",
        "test_cases_json": None,
        "description": """\
<h3>Внедрённые внедрения</h3>
<p><strong>Время:</strong> 1 с &nbsp;|&nbsp; <strong>Память:</strong> 64 Мб</p>
<p>Профессор К. добавил в таблицу показателей лишний признак и переименовал столбцы.
Распределение «лишнего» признака не похоже на остальные.</p>
<p>Скачайте набор, найдите столбец-выброс и введите его имя <strong>точно как в таблице</strong>.</p>
<p>Пример для тренировки:
<a href="/static/data/vnedreniya_sample.csv" download>vnedreniya_sample.csv</a></p>
<p><strong>2 попытки.</strong> Засчитывается лучшая.</p>
""",
    },
    {
        "block": "data",
        "title": "Склонированные клоны",
        "difficulty": "hard",
        "order_num": 2,
        "task_type": "sql",
        "time_limit": "1 секунда",
        "memory_limit": "64 Мб",
        "input_format": "input.txt",
        "output_format": "output.txt",
        "attempts_limit": None,
        "expected_output": "case when root leaf inner parent_id",
        "test_cases_json": None,
        "description": """\
<h3>Склонированные клоны</h3>
<p><strong>Время:</strong> 1 с &nbsp;|&nbsp; <strong>Память:</strong> 64 Мб</p>
<p>Таблица <code>clones(clone_id, parent_id)</code>. Напишите запрос SQLite, возвращающий
<code>clone_id</code> и <code>status</code>:</p>
<ul>
<li><code>root</code> — «нулевой пациент» (нет родителя среди клонов, <code>parent_id IS NULL</code>);</li>
<li><code>leaf</code> — копия без потомков;</li>
<li><code>inner</code> — всё остальное.</li>
</ul>
<pre>clone_id | parent_id
---------|----------
1        | 3
2        | 3
3        | NULL</pre>
<p>Используйте <code>CASE WHEN</code>, подзапросы или JOIN. Отправьте один SQL-запрос.</p>
""",
    },
    {
        "block": "data",
        "title": "Вездесущая чашка",
        "difficulty": "hard",
        "order_num": 3,
        "task_type": "python",
        "time_limit": "1 секунда",
        "memory_limit": "64 Мб",
        "input_format": "input.txt",
        "output_format": "stdout",
        "attempts_limit": None,
        "expected_output": None,
        "test_cases_json": _cases([("@file:cup_sample.txt", "322.49")]),
        "description": """\
<h3>Вездесущая чашка</h3>
<p><strong>Время:</strong> 1 с &nbsp;|&nbsp; <strong>Память:</strong> 64 Мб</p>
<ol>
<li>На stdin — путь к текстовому файлу с наблюдениями.</li>
<li>Отсортировать записи по времени.</li>
<li>Из подряд идущих записей с одинаковыми (x,y) оставить только самую раннюю.</li>
<li>Для каждой записи — Евклидово расстояние до <em>следующей</em> записи с другими координатами.</li>
<li>Взять 5 максимальных расстояний, вывести их произведение (2 знака после запятой).</li>
</ol>
<p>Формат строки: <code>ГГГГ-ММ-ДД ЧЧ:ММ:СС; x; y</code> (разделитель <code>; </code>).</p>
<p>Доступны <code>numpy</code> и <code>pandas</code>. Пример:
<a href="/static/data/cup_sample.txt" download>cup_sample.txt</a></p>
""",
    },
    {
        "block": "backend",
        "title": "Планеты в зоне жизни",
        "difficulty": "hard",
        "order_num": 1,
        "task_type": "backend",
        "time_limit": "5 секунд",
        "memory_limit": "159 Мб",
        "input_format": None,
        "output_format": None,
        "attempts_limit": None,
        "expected_output": "post /planets borrow 422 inhabitation delete isbn condition rented",
        "test_cases_json": None,
        "description": """\
<h3>Планеты в зоне жизни</h3>
<p><strong>Время:</strong> 5 с &nbsp;|&nbsp; <strong>Память:</strong> ~159 Мб</p>
<p>REST-сервис учёта планет (допустимы <strong>Flask</strong>, <strong>FastAPI</strong>, <strong>aiohttp</strong> + uvicorn).</p>
<h4>Эндпоинты</h4>
<ul>
<li><code>POST /planets</code> — JSON: <code>isbn, title, star, condition</code>
(earth, superearth, smallearth, hotearth, coldearth). Ответ: <code>copy_id</code> (plain-text, с 1 без пропусков).</li>
<li><code>GET /planets?isbn=</code> или <code>?star=</code> — список JSON: <code>isbn, condition, rented</code>.</li>
<li><code>POST /planets/{copy_id}/borrow</code> — аренда; при гонке один успех, второй → <strong>422</strong>.</li>
<li><code>POST /planets/{copy_id}/inhabitation</code> — непригодна для жизни.</li>
<li><code>DELETE /planets/{copy_id}</code> — списание (ограничения по <code>condition</code>).</li>
</ul>
<h4>Как сдаётся на Arete LMS</h4>
<p>Вставьте <strong>код сервиса</strong> (Python/Java/C++) в редактор. Автопроверка <em>не запускает</em> ваш сервер —
ищет маршруты и признаки выбранного фреймворка в тексте. На олимпиаде проверка полная (HTTP-тесты).</p>
<pre>POST /planets {"isbn":"123","title":"name","star":"sun","condition":"earth"} → 1
POST /planets/1/borrow (дважды) → второй раз 422</pre>
""",
    },
    {
        "block": "backend",
        "title": "Поставщики",
        "difficulty": "hard",
        "order_num": 2,
        "task_type": "backend",
        "time_limit": "10 секунд",
        "memory_limit": "159 Мб",
        "input_format": None,
        "output_format": None,
        "attempts_limit": None,
        "expected_output": "get /info/ 8080 product 8882",
        "test_cases_json": None,
        "description": """\
<h3>Поставщики</h3>
<p><strong>Время:</strong> 10 с &nbsp;|&nbsp; <strong>Память:</strong> ~159 Мб</p>
<p>Прокси на порту <strong>8080</strong>: <code>GET /info/&lt;PRODUCT_NAME&gt;</code> (без учёта регистра).
Upstream: <code>localhost:8882</code> — цепочка <code>/product/</code>, <code>/product/&lt;id&gt;/</code>.</p>
<p>Формат ответа: <code>detail (product_id): PRICE</code>, сортировка по ID.</p>
<p>Учтите: таймауты, 404, rate limit, пустое тело, обрыв соединения.</p>
<p>Фреймворки: Flask / FastAPI / aiohttp. Библиотеки: requests, httpx и т.д.</p>
<pre>curl http://127.0.0.1:8882/product/
m1;rocket;9000RUB;Rocket s9 pro ultra 2 days delivery

GET localhost:8080/info/rocket →
Rocket s9 pro ultra 2 days delivery (m1): 9000RUB</pre>
<p><em>На LMS:</em> статическая проверка кода (маршрут, порт 8080, обращение к 8882).</p>
""",
    },
    {
        "block": "frontend",
        "title": "Педантичный хомяк",
        "difficulty": "hard",
        "order_num": 1,
        "task_type": "frontend",
        "time_limit": "10 секунд",
        "memory_limit": "640 Мб",
        "input_format": "input.json",
        "output_format": "output.png",
        "attempts_limit": None,
        "expected_output": "drawdigits makeiterator showgrid symbol.iterator setcolor #matrix 380 100",
        "test_cases_json": None,
        "description": """\
<h3>Педантичный хомяк</h3>
<p><strong>Время:</strong> 10 с &nbsp;|&nbsp; <strong>Память:</strong> 640 Мб &nbsp;|&nbsp;
Ввод: input.json, вывод: output.png (на олимпиаде)</p>
<p>На чистом <strong>JavaScript</strong> — матрица <code>#matrix</code> <strong>380×100 px</strong>,
сетка <strong>19×5</strong> ячеек. Цифры 0–9 — шаблоны <strong>3×5</strong>, между цифрами ≥1 пустой столбец.
Лента сдвигается параметром <code>offsetColumns</code> с циклическим переносом через края.</p>
<p><strong>Макет цифр (должен совпадать):</strong></p>
<p><img src="/static/hamster_digits_layout.png" alt="Макет цифр 0–9" style="max-width:100%;border-radius:12px;border:1px solid rgba(139,92,246,0.35);"></p>
<h4>Обязательные функции</h4>
<ol>
<li><code>window.drawDigits({ digits, offsetColumns, color, showGrid })</code>
+ каррирование <code>drawDigits(digits)(offset, opts)</code> + API <code>.setColor()</code>.</li>
<li><code>window.showGrid(on)</code> — сетка через класс, размеры матрицы не ломать.</li>
<li><code>window.makeIterator(config)</code> с <code>Symbol.iterator</code> для сценариев кадров.</li>
</ol>
<p>Решение — <strong>один HTML-файл</strong> (стили и скрипты внутри). Тестируется в Chrome.</p>
<p><em>На LMS:</em> проверка наличия функций и <code>#matrix</code> в тексте HTML (без запуска браузера).</p>
""",
    },
]
