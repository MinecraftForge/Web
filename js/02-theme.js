/*
 Enables switching themes on the fly.
 */

(function () {
    var THEME_LIGHT = 'light';
    var THEME_DARK = 'dark';

    function swapThemeCSS(activeTheme) {
        var oldTheme = activeTheme === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;
        $('link[data-type=themed]').each(function () {
            var oldValue = $(this).attr('href');
            $(this).attr('href', oldValue.replace(oldTheme, activeTheme));
        });
    }

    if (!localStorage.theme) {
        localStorage.theme = THEME_LIGHT;
    }
    swapThemeCSS(localStorage.theme);

    $(document).ready(function () {
        var toggle = $('.theme-switch input');
        toggle.prop('checked', localStorage.theme === THEME_DARK);
        toggle.change(function () {
            localStorage.theme = $(this).is(':checked') ? THEME_DARK : THEME_LIGHT;
            swapThemeCSS(localStorage.theme);
        });
    });
})();