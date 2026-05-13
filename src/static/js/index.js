(function () {
    const codeLines = [
        { num: 1, content: '<span class="code-keyword">def</span> <span class="code-function">solve</span>(n):' },
        { num: 2, content: '    <span class="code-comment"># Быстрое решение</span>' },
        { num: 3, content: '    <span class="code-keyword">ㅤㅤif</span> n <= <span class="code-variable">1</span>:' },
        { num: 4, content: '        <span class="code-keyword">ㅤㅤㅤㅤreturn</span> n' },
        { num: 5, content: '    <span class="code-keyword">ㅤㅤreturn</span> <span class="code-function">solve</span>(n-<span class="code-variable">1</span>) + <span class="code-function">solve</span>(n-<span class="code-variable">2</span>)' },
        { num: 6, content: '' },
        { num: 7, content: '<span class="code-function">print</span>(<span class="code-function">solve</span>(<span class="code-variable">10</span>))  <span class="code-comment"># ✓ Тесты пройдены</span>' }
    ];

    function typeCode() {
        const container = document.getElementById('codeContent');
        if (!container) return;
        container.innerHTML = '';
        codeLines.forEach(function (line, index) {
            setTimeout(function () {
                const el = document.createElement('div');
                el.className = 'code-line';
                el.innerHTML = '<span class="line-number">' + line.num + '</span><span>' + line.content + '</span>';
                el.style.opacity = '0';
                el.style.transform = 'translateX(-10px)';
                container.appendChild(el);
                setTimeout(function () {
                    el.style.transition = 'all 0.3s ease';
                    el.style.opacity = '1';
                    el.style.transform = 'translateX(0)';
                }, 50);
            }, index * 220);
        });
    }

    setTimeout(typeCode, 800);

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) entry.target.classList.add('animate-in');
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.feature-card').forEach(function (el) {
        el.style.opacity = '0';
        observer.observe(el);
    });
})();
