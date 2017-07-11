/**
 * Created by paul on 10.07.17.
 */
$(document).ready(function refresher() {
    $.ajax({
        url: 'ajax/current_queue_ajax.html',
        success: function (data) {
            $('div.content').html(data);
        },
        complete: function () {
            setTimeout(refresher, 10000);
            console.log('Refreshed.')
        }
    });
});

function CloseOrder(order_id) {
    var confirmation = confirm("Close Order?");
    if (confirmation == true) {
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        });
        $.ajax({
            type: 'POST',
            url: form.attr('data-send-url'),
            data: {"order_id": order_id},
            dataType: 'json',
            success: function (data) {
                alert('Success! ' + data.received);
                $('.response').text();
                res = data.received;
            }
        }
        ).fail(function () {
                alert('You have no permission!');
            });
    }
    else {
        event.preventDefault();
    }
}
