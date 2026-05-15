import json
import os
import shutil
import subprocess
import sys
import tempfile

from config import MAX_STDERR_LENGTH, SUBPROCESS_TIMEOUT

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_TEST_DATA_DIR = os.path.join(_PROJECT_ROOT, "static", "data")


class SubmissionResult:
    def __init__(self, passed, score, result_text):
        self.passed = passed
        self.score = score
        self.result_text = result_text


class SubmissionEvaluator:
    def evaluate(self, task, code):
        task_type = task.task_type

        if task_type == "python":
            return self._check_python(task, code)
        if task_type == "answer":
            return self._check_answer(task, code)
        if task_type == "sql":
            return self._check_keyword(task, code)
        if task_type == "backend":
            return self._check_backend(task, code)
        if task_type in ("html", "frontend"):
            return self._check_frontend(task, code)

        return SubmissionResult(
            passed=False,
            score=0,
            result_text="Неизвестный тип задачи",
        )

    def _load_test_cases(self, task):
        if task.test_cases_json:
            try:
                return json.loads(task.test_cases_json)
            except (json.JSONDecodeError, TypeError):
                pass

        if task.expected_output is not None:
            return [{"input": "", "output": task.expected_output}]

        return []

    def _check_python(self, task, code):
        test_cases = self._load_test_cases(task)
        if not test_cases:
            return SubmissionResult(passed=False, score=0, result_text="Нет тест-кейсов")

        passed_count = 0
        result_lines = []
        total = len(test_cases)

        for i, tc in enumerate(test_cases, start=1):
            line = self._run_single_test(i, code, tc)
            result_lines.append(line)
            if line == f"Тест {i}: OK":
                passed_count += 1

        score = int(passed_count / total * 100) if total > 0 else 0
        passed = passed_count == total and total > 0
        return SubmissionResult(
            passed=passed,
            score=score,
            result_text="\n".join(result_lines),
        )

    def _resolve_test_input(self, raw_input, work_dir):
        if not raw_input.startswith("@file:"):
            return raw_input

        rel_path = raw_input[6:].strip()
        src = os.path.join(_TEST_DATA_DIR, rel_path)
        if not os.path.isfile(src):
            raise FileNotFoundError(f"Тестовый файл не найден: {rel_path}")

        filename = os.path.basename(rel_path)
        dst = os.path.join(work_dir, filename)
        shutil.copy2(src, dst)
        return filename + "\n"

    def _run_single_test(self, index, code, tc):
        work_dir = tempfile.mkdtemp()
        try:
            tmp_path = os.path.join(work_dir, "solution.py")
            with open(tmp_path, "w", encoding="utf-8") as tmp:
                tmp.write(code)

            stdin_data = self._resolve_test_input(tc.get("input", ""), work_dir)

            proc = subprocess.run(
                [sys.executable, tmp_path],
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT,
                cwd=work_dir,
            )

            if proc.returncode != 0:
                stderr = proc.stderr.strip()[:MAX_STDERR_LENGTH]
                return f"Тест {index}: Ошибка выполнения\n{stderr}"

            actual = proc.stdout.strip()
            expected = tc.get("output", "").strip()

            if actual == expected:
                return f"Тест {index}: OK"

            return (
                f"Тест {index}: Неверный ответ\n"
                f"Ожидалось: {expected}\n"
                f"Получено: {actual}"
            )

        except subprocess.TimeoutExpired:
            return f"Тест {index}: Превышено время выполнения ({SUBPROCESS_TIMEOUT} с)"
        except Exception as exc:
            return f"Тест {index}: Ошибка: {exc}"
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def _check_answer(self, task, code):
        answer = code.strip().lower()
        expected = (task.expected_output or "").strip().lower()
        passed = answer == expected
        return SubmissionResult(
            passed=passed,
            score=100 if passed else 0,
            result_text=code.strip(),
        )

    def _missing_keywords(self, expected, answer):
        keywords = (expected or "").strip().lower().split()
        return [kw for kw in keywords if kw not in answer.lower()]

    def _check_keyword(self, task, code):
        missing = self._missing_keywords(task.expected_output, code)
        passed = not missing
        return SubmissionResult(
            passed=passed,
            score=100 if passed else 0,
            result_text=(
                "SQL-запрос содержит обязательные элементы"
                if passed
                else f"Не найдены обязательные элементы: {', '.join(missing)}"
            ),
        )

    def _check_backend(self, task, code):
        answer = code.strip().lower()
        frameworks = [
            "flask",
            "fastapi",
            "aiohttp",
            "uvicorn",
            "starlette",
            "@app.route",
            "app.route",
            "app.get",
            "app.post",
            "router.",
        ]
        has_framework = any(marker in answer for marker in frameworks)
        missing = self._missing_keywords(task.expected_output, code)
        if not has_framework:
            missing = ["flask/fastapi/aiohttp"] + missing
        passed = not missing
        return SubmissionResult(
            passed=passed,
            score=100 if passed else 0,
            result_text=(
                "В решении найдены маршруты API и признаки Flask/FastAPI/aiohttp"
                if passed
                else "Не найдены: " + ", ".join(missing)
            ),
        )

    def _check_frontend(self, task, code):
        missing = self._missing_keywords(task.expected_output, code)
        passed = not missing
        return SubmissionResult(
            passed=passed,
            score=100 if passed else 0,
            result_text=(
                "HTML/JS содержит обязательные функции и элементы"
                if passed
                else f"Не найдены обязательные элементы: {', '.join(missing)}"
            ),
        )
