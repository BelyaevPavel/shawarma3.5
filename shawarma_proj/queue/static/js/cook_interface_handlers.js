/**
 * Created by paul on 10.07.17.
 */

$(document).ready(function () {
    $('#cook_interface').addClass('header-active');
    AdjustLineHeight();
    GrillRefresher();
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
    var url = $('#urls').attr('data-next-url');
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
            $('div.next-to-prepare-container').html(data['html']);
        },
        complete: function () {
            setTimeout(NextRefresher, 10000);
        }
    });
}


function AdjustLineHeight() {

}

function TakeItem(id) {
    var url = $('#urls').attr('data-take-url');
    var confirmation = confirm("Начать готовить?");
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
                    //alert('Успех!');
                }
                else {
                    alert('Ужа делается ' + data['staff_maker'] + '!');
                }
            },
            complete: function () {
                location.reload();
            }
        }).fail(function () {
                    alert('У вас нет права добавлять заказ!');
                });
    }

}

function ItemToGrill(id) {
    var url = $('#urls').attr('data-grill-url');
    var confirmation = confirm("Поместить в гриль?");
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
    var confirmation = confirm("Извлечь из гриля?");
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
                alert('Положите в заказ №' + data['order_number']);
            },
            complete: function () {
                location.reload();
            }
        });
    }
}
