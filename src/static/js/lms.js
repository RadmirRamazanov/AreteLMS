(function () {
    var data = window.LMS_DATA || {};

    var blockFill = document.getElementById('blockFill');
    if (blockFill) {
        var bPct = parseInt(blockFill.dataset.pct || data.blockPct || 0, 10);
        setTimeout(function () { blockFill.style.width = bPct + '%'; }, 120);
    }

    var totalFill = document.getElementById('totalFill');
    if (totalFill) {
        var tPct = parseInt(totalFill.dataset.pct || data.totalPct || 0, 10);
        setTimeout(function () { totalFill.style.width = tPct + '%'; }, 200);
    }
})();
