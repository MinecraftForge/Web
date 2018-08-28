/*
 Initializes theme switching
 Either call before enabling toggler or in the document head
 */

window.forge = {
    THEME_LIGHT: 'light',
    THEME_DARK: 'dark',
    swapThemeCSS: function (activeTheme) {
        var stylesheets = document.styleSheets;
        var length = stylesheets.length;
        var i;

        for(i = 0; i < length; i++) {
            var ss = stylesheets[i];
            if (!ss.ownerNode.dataset.theme) {
                continue;
            }
            ss.disabled = ss.ownerNode.dataset.theme !== activeTheme;
        }

    }
};

if (!localStorage.theme) {
    localStorage.theme = window.forge.THEME_LIGHT;
}

window.forge.swapThemeCSS(localStorage.theme);
