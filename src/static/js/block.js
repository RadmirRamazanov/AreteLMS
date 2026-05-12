(function () {
    window.addEventListener('load', function () {
        var fill = document.getElementById('progressFill');
        if (fill) {
            var pct = parseInt(fill.dataset.pct || 0, 10);
            fill.style.width = '0%';
            requestAnimationFrame(function () {
                setTimeout(function () { fill.style.width = pct + '%'; }, 120);
            });
        }
    });
})();
