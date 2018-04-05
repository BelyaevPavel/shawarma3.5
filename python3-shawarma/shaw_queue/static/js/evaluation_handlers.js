/**
 * Created by paul on 05.02.18.
 */
var chosen_mark = 0;
$(document).ready(function () {
    $('#order-number-input').val('');
    $('#note').val('');
});

function enlight(mark) {
    $('#mark-1').removeClass('chosen-mark-block');
    $('#mark-2').removeClass('chosen-mark-block');
    $('#mark-3').removeClass('chosen-mark-block');
    $('#mark-4').removeClass('chosen-mark-block');
    $('#mark-5').removeClass('chosen-mark-block');
    $('#mark-'+mark).addClass('chosen-mark-block');
    chosen_mark = parseInt(mark);
}


function Evaluate() {
    if (chosen_mark > 0) {
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        });
        $.ajax({
                type: 'POST',
                url: $('#urls').attr('data-evaluate-url'),
                data: {
                    "daily_number": $('#order-number-input').val(),
                    "mark": chosen_mark,
                    "note": $('#note').val()
                },
                dataType: 'json',
                success: function (data) {
                    alert('Спасибо! Мы ценим ваше мнение!');
                    setTimeout(location.reload, 10000);
                },
                complete: function () {
                    location.reload();
                }
            }
        ).fail(function () {
            //alert('У вас нет прав!');
        });
    }
    else {
        alert('Пожалуйста, выберите оценку!');
    }
}