import os

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from config import ALLOWED_UPLOAD_EXTENSIONS, MAX_UPLOAD_BYTES
from models import BLOCKS, Submission, Task, db
from services import SubmissionEvaluator

api_bp = Blueprint("api", __name__, url_prefix="/api")

_evaluator = SubmissionEvaluator()


def _task_to_dict(task):
    return {
        "id": task.id,
        "block": task.block,
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "difficulty": task.difficulty,
        "order_num": task.order_num,
        "max_score": task.max_score,
        "attempts_limit": task.attempts_limit,
        "time_limit": task.time_limit,
        "memory_limit": task.memory_limit,
        "input_format": task.input_format,
        "output_format": task.output_format,
    }


def _submission_to_dict(sub):
    return {
        "id": sub.id,
        "task_id": sub.task_id,
        "passed": sub.passed,
        "score": sub.score,
        "result": sub.result,
        "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
    }


@api_bp.route("/v1/blocks", methods=["GET"])
def get_blocks():
    blocks = []
    for key, info in BLOCKS.items():
        count = Task.query.filter_by(block=key).count()
        blocks.append(
            {
                "key": key,
                "name": info["name"],
                "icon": info["icon"],
                "description": info["description"],
                "task_count": count,
            }
        )
    return jsonify(blocks)


@api_bp.route("/v1/tasks", methods=["GET"])
def get_tasks():
    block_filter = request.args.get("block")
    query = Task.query

    if block_filter:
        if block_filter not in BLOCKS:
            return jsonify({"error": "Блок не найден"}), 404
        query = query.filter_by(block=block_filter)

    tasks = query.order_by(Task.block, Task.order_num).all()
    return jsonify([_task_to_dict(t) for t in tasks])


@api_bp.route("/v1/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(_task_to_dict(task))


@api_bp.route("/v1/me", methods=["GET"])
@login_required
def get_me():
    user = current_user
    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    )


@api_bp.route("/v1/me/progress", methods=["GET"])
@login_required
def get_my_progress():
    progress = []
    total_solved = 0
    total_tasks = 0

    for key, info in BLOCKS.items():
        count = Task.query.filter_by(block=key).count()
        solved = current_user.solved_in_block(key)
        progress.append(
            {
                "block": key,
                "name": info["name"],
                "total": count,
                "solved": solved,
            }
        )
        total_solved += solved
        total_tasks += count

    return jsonify(
        {
            "blocks": progress,
            "total_tasks": total_tasks,
            "total_solved": total_solved,
        }
    )


@api_bp.route("/v1/me/submissions", methods=["GET"])
@login_required
def get_my_submissions():
    subs = (
        Submission.query.filter_by(user_id=current_user.id)
        .order_by(Submission.submitted_at.desc())
        .limit(50)
        .all()
    )
    return jsonify([_submission_to_dict(s) for s in subs])


@api_bp.route("/submit", methods=["POST"])
@login_required
def submit():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Нет данных"}), 400

    task_id = data.get("task_id")
    code = data.get("code", "").strip()

    if not task_id or not code:
        return jsonify({"error": "Необходимо указать task_id и код"}), 400

    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Задача не найдена"}), 404

    if task.attempts_limit:
        used = Submission.query.filter_by(
            task_id=task_id, user_id=current_user.id
        ).count()
        if used >= task.attempts_limit:
            return jsonify(
                {
                    "error": (
                        f"Исчерпан лимит попыток ({task.attempts_limit})."
                        " Больше отправок нет."
                    ),
                    "attempts_exceeded": True,
                }
            ), 403

    result = _evaluator.evaluate(task, code)

    submission = Submission(
        user_id=current_user.id,
        task_id=task_id,
        code=code,
        result=result.result_text,
        passed=result.passed,
        score=result.score,
    )
    db.session.add(submission)
    db.session.commit()

    verdict_msg = (
        f"Зачтено {result.score}/100 баллов" if result.passed else "Доработать"
    )

    return jsonify(
        {
            "passed": result.passed,
            "score": result.score,
            "result": result.result_text,
            "message": verdict_msg,
            "verdict": "accepted" if result.passed else "rejected",
        }
    )


@api_bp.route("/v1/upload-code", methods=["POST"])
@login_required
def upload_code():
    if "file" not in request.files:
        return jsonify({"error": "Файл не найден в запросе"}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "Имя файла пустое"}), 400

    ext = os.path.splitext(file.filename)[1].lstrip(".").lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_UPLOAD_EXTENSIONS))
        return jsonify({"error": f"Разрешены только форматы: {allowed}"}), 400

    raw = file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        return jsonify({"error": "Файл слишком большой (максимум 1 МБ)"}), 413

    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        return jsonify({"error": "Файл должен быть в кодировке UTF-8"}), 422

    return jsonify({"content": content, "filename": file.filename})
