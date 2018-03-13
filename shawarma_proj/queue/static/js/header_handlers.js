/**
 * Created by paul on 13.07.17.
 */
$(document).ready(function () {
    console.log('ready');
    AdjustElements();
});
$(window).resize(AdjustElements);

function AdjustElements() {
    var header_buttons = $('div.header-buttons');
    var header_buttons_count = header_buttons.length;
    var who_logged = $('#header-who-logged');
    var window_width = $(window).width();
    var window_height = $(window).height();
    var buttons_width = (window_width - who_logged.width()) / header_buttons_count-10;
    header_buttons.width(buttons_width);
}

function logout() {
    var url = $('#header-urls').attr('logout-url');
    var confirmation = confirm("Выйти из системы?");
    if (confirmation) {
        location.href = url;
    }
}