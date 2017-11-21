/**
 * Created by paul on 21.07.17.
 */
$(document).ready(function () {
        refresher();
    }
);
var ready_order_numbers = [];

function refresher() {
    console.log('Refreshed');
    $.ajax({
        url: $('#urls').attr('data-refresh-url'),
        success: function (data) {
            $('#page-content').html(data['html']);
            updated_ready_numbers = JSON.parse(data['ready']);
            difference = updated_ready_numbers.filter(function (el) {
                return !ready_order_numbers.includes(el)
            });
            console.log(difference);
            //sound_number(difference);
            for(var i=0; i<updated_ready_numbers.length; i++)
            {
                sound_number(updated_ready_numbers[i]);
                $.ajaxSetup({
                    beforeSend: function (xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken)
                    }
                });
                $.ajax({
                        type: 'POST',
                        url: $('#urls').attr('data-cancel-order-url'),
                        data: {"id": order_id},
                        dataType: 'json',
                        success: function (data) {
                            alert('Заказ отменён!');
                        }
                    }
                ).fail(function () {
                    // alert('У вас нет прав!');
                });
            }
        },
        complete: function () {
            setTimeout(refresher, 10000);
        }
    });
}

function sound_number(difference) {
    $.each(difference, function (index, value) {
        setTimeout(function () {
            aux_str = '#speaker-' + value;
            console.log(aux_str);
            console.log('Playing...');
            setTimeout(function () {
                $('#speaker-order')[0].play();
            }, 0);
            $('#speaker-order')[0].load();
            setTimeout(function () {
                $('#speaker-number')[0].play();
            }, 750);
            $('#speaker-number')[0].load();
            setTimeout(function () {
                $(aux_str)[0].play();
            }, 1500);
            $(aux_str)[0].load();
        }, 3000 * index);
    });
    ready_order_numbers = $.merge(ready_order_numbers, difference);
}
