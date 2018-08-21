/*
 Initializes theme switching
 Either call before enabling toggler or in the document head
 */

window.forge = {
    THEME_LIGHT: 'light',
    THEME_DARK: 'dark',
    swapThemeCSS: function (activeTheme) {
        var oldTheme = activeTheme === window.forge.THEME_LIGHT ? window.forge.THEME_DARK : window.forge.THEME_LIGHT;
        var themeables = document.querySelectorAll('link[data-type=themed]');
        themeables.forEach(function (el) {
            var oldValue = el.getAttribute('href');
            el.setAttribute('href', oldValue.replace(oldTheme, activeTheme));
        });
    }
};

if (!localStorage.theme) {
    localStorage.theme = window.forge.THEME_LIGHT;
}

window.forge.swapThemeCSS(localStorage.theme);
