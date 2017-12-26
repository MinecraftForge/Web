/*
 Implementation for sidebars used on the Forge sites.
 */
$(document).ready(function () {
    $('.sidebar-sticky').Stickyfill();
    $('.scroll-pane').jScrollPane({
        autoReinitialise: true,
        verticalGutter: 0,
        hideFocus: true
    });
    $('.open-sidebar').click(function (e) {
        $('.sidebar-sticky').addClass('active-sidebar');
        $('body').addClass('sidebar-active');
        e.preventDefault();
    });
    $('.close-sidebar').click(function (e) {
        $('.sidebar-sticky').removeClass('active-sidebar');
        $('body').removeClass('sidebar-active');
        e.preventDefault();
    });
    // Collapsible elements implementation
    $('.collapsible,.nav-collapsible').each(function () {
        var item = $(this);
        var toggle = item.parent().find('.toggle-collapsible');
        var showText = item.data('show-text') ? item.data('show-text') : 'Show';
        var hideText = item.data('hide-text') ? item.data('hide-text') : 'Hide';
        var toggleStyle = item.data('toggle-style') ? item.data('toggle-style') : 'display';
        var isCollapsed = function() {
            return toggleStyle == 'class' ? item.hasClass('collapsed') : item.css('display') == 'none';
        };
        var changeState = function(state) {
            if (toggleStyle == 'class') {
                if (state) {
                    item.removeClass('collapsed');
                    item.addClass('expanded');
                } else {
                    item.removeClass('expanded');
                    item.addClass('collapsed');
                }
            } else {
                item.css('display', state ? 'block' : 'none');
            }
        };
        if (!item.hasClass('nav-collapsible-open')) {
            changeState(false);
        } else {
            changeState(true);
            var icons = toggle.find('.collapsible-icon');
            var texts = toggle.find('.collapsible-text');
            icons.removeClass('fa-plus');
            icons.addClass('fa-minus');
            texts.html(showText);
        }
        toggle.click(function (e) {
            var icon = toggle.find('.collapsible-icon');
            var text = toggle.find('.collapsible-text');
            if (isCollapsed()) {
                changeState(true);
                icon.addClass('fa-minus');
                icon.removeClass('fa-plus');
                text.html(hideText);
            } else {
                changeState(false);
                icon.addClass('fa-plus');
                icon.removeClass('fa-minus');
                text.html(showText);
            }
            e.preventDefault();
        });
    });
});