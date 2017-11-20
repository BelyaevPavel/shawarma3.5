/**
 * Created by paul on 12.07.17.
 */
function ReadyOrder(id) {
    var url = $('#urls').attr('data-ready-url');
    var confirmation = confirm("Заказ готов?");
    if (confirmation) {
        console.log(id + ' ' + url);
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        });
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'id': id,
                'servery_choose': $('[name=servery_choose]:checked').val()
            },
            dataType: 'json',
            success: function (data) {
                location.href = $('#current-queue').parent().attr('href');
                //if (data['success']) {
                //    alert('Success!');
                //}
            }
        });
    }
}

function PrintOrder(order_id) {
    var url = '/queue/order/print/'+order_id+'/';
    window.open(url, 'Печать заказа ' + order_id)
}

function CancelItem(id) {
    var url = $('#urls').attr('data-cancel-item-url');
    var confirmation = confirm("Исключить из заказа?");
    if (confirmation) {
        console.log(id + ' ' + url);
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        });
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'id': id
            },
            dataType: 'json',
            success: function (data) {
                // if (data['success']) {
                //     alert('Успех!');
                // }
            },
            complete: function () {
                location.reload();
            }
        });
    }
}


function FinishCooking(id) {
    var url = $('#urls').attr('data-finish-item-url');
    console.log(id + ' ' + url);
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    });
    $.ajax({
        type: 'POST',
        url: url,
        data: {
            'id': id
        },
        dataType: 'json',
        success: function (data) {
            alert('Success!' + data);
        },
        complete: function () {
            location.reload();
        }
    });
}