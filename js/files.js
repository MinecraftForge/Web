/*
 Implementation for various utilities on the files site.
 */

$(document).ready(function () {
    $('[data-toggle=tooltip]').tooltipster({
        theme: 'tooltipster-shadow',
        position: 'bottom',
        animation: 'grow'
    });
    $('[data-toggle=popup]').tooltipster({
        theme: 'tooltipster-shadow',
        position: 'bottom',
        animation: 'grow',
        contentAsHTML: true,
        interactive: true
    });
    $('.download-list .download-links li').each(function () {
        if ($(this).find('.info-tooltip').length > 0) {
            var info = $(this).children('.info-tooltip');
            $(this).children('.info-link').tooltipster('content', info.html());
        }
    });

});

window.onload = function () {
    if (location.hostname != 'files.minecraftforge.net') {
        var elems = document.getElementsByTagName('a');
        for (var i = 0; i < elems.length; i++)
            elems[i]['href'] = elems[i]['href'].replace('files.minecraftforge.net', location.hostname);
    }
};
