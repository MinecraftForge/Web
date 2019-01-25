// Deal with Google ad consent and ad blockers

function giveConsent() {
    localStorage.consent = 'accepted';
    window.themeSwitchToggle();
    $('.theme-switch-wrapper').removeClass('hidden');
    $('.privacy-disclaimer').remove();
    (adsbygoogle = window.adsbygoogle || []).requestNonPersonalizedAds = 0;
    (adsbygoogle = window.adsbygoogle || []).pauseAdRequests = 0;
}

function revokeConsent() {
    localStorage.consent = 'declined';
    $('.privacy-disclaimer').remove();
    (adsbygoogle = window.adsbygoogle || []).requestNonPersonalizedAds = 1;
    (adsbygoogle = window.adsbygoogle || []).pauseAdRequests = 0;
}

(adsbygoogle = window.adsbygoogle || []).pauseAdRequests = 1;
$('.adsbygoogle').each(function () {
    window.adsbygoogle.push({});
});

$(document).ready(function() {
    $('body').addClass('loading-done');
    var consent = localStorage.consent;

    if (consent === 'accepted') {
        giveConsent();
    } else if (consent === 'declined') {
        //$('.theme-switch-wrapper').remove();
        revokeConsent();
    } else if (localStorage.consent === undefined) {
        // Display the disclaimer by default, in case the request fails completely
        $('.privacy-disclaimer').css('display', 'block');
        $('.theme-switch-wrapper').addClass('hidden');
        $.get({url: 'https://ssl.geoplugin.net/json.gp?k=7a35ee7cc6f992e4', dataType: 'json'})
            .done(function (data) {
                // If we're not in the EU, simply give consent, otherwise keep asking
                if (data.geoplugin_inEU !== 1) {
                    giveConsent();
                }
            });
    }

    $('.btn-privacy-disclaimer-accept').click(function (e) {
        e.preventDefault();
        giveConsent();
    });

    $('.btn-privacy-disclaimer-decline').click(function (e) {
        e.preventDefault();
        revokeConsent();
    });

    function updatePrivacyStatus() {
        if (localStorage.consent === 'accepted') {
            $('.privacy-status').html('You have <strong>accepted</strong> personalized ads and usage of local storage.');
        } else if (localStorage.consent === 'declined') {
            $('.privacy-status').html('You <strong>do not allow</strong> personalized ads or usage of local storage.');
        } else {
            $('.privacy-status').text('You have yet to choose one of the options.')
        }
    }

    updatePrivacyStatus();

    $('.btn-privacy-settings-accept').click(function (e) {
        e.preventDefault();
        giveConsent();
        updatePrivacyStatus();
    });

    $('.btn-privacy-settings-decline').click(function (e) {
        e.preventDefault();
        revokeConsent();
        updatePrivacyStatus();
    });
});
