/**
 * Created by paul on 03.11.17.
 */
/**
 * Created by paul on 10.07.17.
 */

$(document).ready(function () {
    $('#cook_interface').addClass('active');
    AdjustLineHeight();
    //GrillRefresher();
    NextRefresher();
});
$(window).resize(AdjustLineHeight);


function GrillRefresher() {
    var url = $('#urls').attr('data-grill-timer-url');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    });
    $.ajax({
        type: 'POST',
        url: url,
        dataType: 'json',
        success: function (data) {
            $('div.in-grill-container').html(data['html']);
            var timer_text = $('div.in-grill-container .in-grill-timer');
            timer_text.text(function () {
                return this + " !";
            })
        },
        complete: function () {
            setTimeout(GrillRefresher, 10000);
        }
    });
}

function NextRefresher() {
    console.log("NextRefresher");
    var url = $('#urls').attr('data-ajax');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    });
    $.ajax({
        type: 'POST',
        url: url,
        dataType: 'json',
        data: {'id': '0'},
        success: function (data) {
            console.log("success");
            console.log(data['html']);
            $('div#inner-content').html(JSON.parse(data['html']));
        },
        complete: function () {
            setTimeout(NextRefresher, 10000);
        }
    }).fail(function () {
            alert('У вас нет прав!');
        });
}


function AdjustLineHeight() {

}

function TakeItem(id) {
    var url = $('#urls').attr('data-take-url');
    var confirmation = true;
    console.log(confirmation);
    if (confirmation) {
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
                if (data['success']) {
                    $('#product_id_'+id.toString()).addClass('in-progress-item');
                    $('#product_id_'+id.toString()).attr('onclick', 'FinishItemCooking('+id+')');
                    //alert('Успех!');
                }
                else {
                    alert('Ужа делается ' + data['staff_maker'] + '!');
                }
            },
            complete: function () {
                location.reload();
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                alert(textStatus + ' ' + errorThrown + ' ' + XMLHttpRequest);
            }
        }).fail(function () {
                    alert('Some error...');
                });
    }

}

function ItemToGrill(id) {
    var url = $('#urls').attr('data-grill-url');
    var confirmation = true;
    if (confirmation) {
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
                //alert('Успех!' + data);
            },
            complete: function () {
                location.reload();
            }
        });
    }
}

function FinishItemCooking(id) {
    var url = $('#urls').attr('data-finish-url');
    var confirmation = true;
    if (confirmation) {
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
                    $('#product_id_'+id.toString()).addClass('in-grill-slot');
                //alert('Положите в заказ №' + data['order_number']);
            },
            complete: function () {
                location.reload();
            }
        });
    }
}

function FinishAllContent(id) {
    var url = $('#urls').attr('data-finish-all-content-url');
    var confirmation = true;
    if (confirmation) {
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
                //alert('Положите в заказ №' + data['order_number']);
            },
            complete: function () {
                location.reload();
            }
        });
    }
}
