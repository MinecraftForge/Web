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
        var find = 'files.minecraftforge.net'
        var replace = location.hostname
        
        if (location.protocol == 'file:') {
            find = /https?:\/\/files\.minecraftforge\.net/i
            replace = location.pathname.substring(0, location.pathname.indexOf('test/out/') + 'test/out'.length)
        }
        //console.log('Converting hostname from ' + find.toString() + ' to ' + replace)
        
        var elems = document.getElementsByTagName('a')
        for (var i = 0; i < elems.length; i++)
            elems[i]['href'] = elems[i]['href'].replace(find, replace)
    }
};
