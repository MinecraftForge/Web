$(document).ready(function () {
    $("pre.highlight code[class*='language-']").each(function () {
        var className = this.className.match(/language-([A-Za-z0-9+-]+)/);
        if (className) {
            $(this).removeClass(className[0]);
            $(this).addClass(className[1].toLowerCase());
        }
    });
    hljs.initHighlighting();
});