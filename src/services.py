import json
import os
import subprocess
import tempfile

from config import MAX_STDERR_LENGTH, SUBPROCESS_TIMEOUT


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
        if task_type in ("sql", "html"):
            return self._check_keyword(task, code)

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

    def _run_single_test(self, index, code, tc):
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as tmp:
                tmp.write(code)
                tmp_path = tmp.name

            proc = subprocess.run(
                ["python3", tmp_path],
                input=tc.get("input", ""),
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT,
            )
            os.unlink(tmp_path)

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

    def _check_answer(self, task, code):
        answer = code.strip().lower()
        expected = (task.expected_output or "").strip().lower()
        passed = answer == expected
        return SubmissionResult(
            passed=passed,
            score=100 if passed else 0,
            result_text=code.strip(),
        )

    def _check_keyword(self, task, code):
        expected = (task.expected_output or "").strip().lower()
        answer = code.strip().lower()
        passed = expected in answer
        return SubmissionResult(
            passed=passed,
            score=100 if passed else 0,
            result_text="Ответ принят" if passed else "Ответ не совпадает с ожидаемым",
        )
