(function () {
    var data = window.TASK_DATA || {};
    var TASK_ID = data.taskId;
    var lastCode = data.lastCode || null;

    window.clearEditor = function () {
        document.getElementById('codeInput').value = '';
    };

    window.restoreCode = function () {
        if (lastCode) {
            document.getElementById('codeInput').value = lastCode;
        }
    };

    window.togglePrevCode = function (btn) {
        var wrap = document.getElementById('prevCode');
        if (!wrap) return;
        var open = wrap.classList.toggle('open');
        btn.textContent = open ? 'Скрыть код' : 'Показать код';
    };

    window.submitSolution = async function () {
        var code = document.getElementById('codeInput').value.trim();
        if (!code) {
            showResult(false, 'Доработать', 'Введите решение перед отправкой', 0);
            return;
        }

        var btn = document.getElementById('submitBtn');
        var btnText = document.getElementById('btnText');
        var btnIcon = document.getElementById('btnIcon');

        btn.disabled = true;
        btnText.textContent = 'Проверяем...';
        if (btnIcon) {
            btnIcon.outerHTML = '<div class="spinner" id="btnIcon"></div>';
        }

        try {
            var res = await fetch('/api/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: TASK_ID, code: code })
            });
            var d = await res.json();

            if (d.attempts_exceeded) {
                showResult(false, 'Доработать', d.error, 0);
                btn.disabled = true;
                return;
            }

            showResult(d.passed, d.message, d.result || '', d.score || 0);

            if (d.passed) {
                setTimeout(function () { location.reload(); }, 1800);
            }
        } catch (e) {
            showResult(false, 'Доработать', 'Ошибка соединения: ' + e.message, 0);
        } finally {
            var currentBtn = document.getElementById('submitBtn');
            if (currentBtn && !currentBtn.disabled) {
                currentBtn.disabled = false;
            } else if (currentBtn) {
                currentBtn.disabled = false;
                btnText.textContent = 'Отправить решение';
                var spinner = document.getElementById('btnIcon');
                if (spinner && spinner.className === 'spinner') {
                    spinner.outerHTML = '<svg id="btnIcon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>';
                }
            }
        }
    };

    function showResult(passed, message, output, score) {
        var panel = document.getElementById('resultPanel');
        var verdict = document.getElementById('resultVerdict');
        var scoreEl = document.getElementById('resultScore');
        var out = document.getElementById('resultOutput');

        panel.className = 'result-panel visible ' + (passed ? 'pass' : 'fail');
        verdict.className = 'result-verdict ' + (passed ? 'pass' : 'fail');
        verdict.textContent = message;
        scoreEl.textContent = score !== undefined ? score + '/100 баллов' : '';
        out.textContent = output || (passed ? 'Все тесты пройдены!' : 'Проверьте правильность решения');
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    var codeInput = document.getElementById('codeInput');
    if (codeInput) {
        codeInput.addEventListener('keydown', function (e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                var s = this.selectionStart, end = this.selectionEnd;
                this.value = this.value.substring(0, s) + '    ' + this.value.substring(end);
                this.selectionStart = this.selectionEnd = s + 4;
            }
        });
    }
})();
