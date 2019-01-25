/*
 Enables switching themes on the fly.
 Initialize by calling window.themeSwitchToggle() from $(document).ready
 */

window.themeSwitchToggle = function () {
    var toggle = $('.theme-switch input');
    toggle.prop('checked', localStorage.theme === window.forge.THEME_DARK);
    toggle.change(function () {
        localStorage.theme = $(this).is(':checked') ? window.forge.THEME_DARK : window.forge.THEME_LIGHT;
        window.forge.swapThemeCSS(localStorage.theme);
    });
};
