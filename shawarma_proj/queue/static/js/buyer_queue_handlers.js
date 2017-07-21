/**
 * Created by paul on 21.07.17.
 */
$(document).ready( function () {
    refresher();
}
);

function refresher() {
    console.log('Refreshed');
    $.ajax({
        url: $('#urls').attr('data-refresh-url'),
        success: function (data) {
            $('#page-content').html(data['html']);
        },
        complete: function () {
            setTimeout(refresher, 10000);
        }
    });
}
