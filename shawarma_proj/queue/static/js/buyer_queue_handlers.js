/**
 * Created by paul on 21.07.17.
 */
var ready_order_numbers = [];
var csrftoken = $("[name=csrfmiddlewaretoken]").val();
$(document).ready(function () {
        refresher();
    }
);

function refresher() {
    console.log('Refreshed');
    $.ajax({
        url: $('#urls').attr('data-refresh-url'),
        success: function (data) {
            $('#page-content').html(data['html']);
            var updated_ready_numbers = JSON.parse(data['ready']);
            var voiced_flags = JSON.parse(data['voiced']);
            var difference = updated_ready_numbers.filter(function (el) {
                return !ready_order_numbers.includes(el)
            });
            process_numbers(updated_ready_numbers, voiced_flags);
            console.log(difference);
            //sound_number(difference);
            /*for(var i=0; i<updated_ready_numbers.length; i++)
             {
             setTimeout(function () {
             aux = updated_ready_numbers[i];
             console.log(aux);
             sound_number(updated_ready_numbers[i]);
             $.ajaxSetup({
             beforeSend: function (xhr, settings) {
             xhr.setRequestHeader("X-CSRFToken", csrftoken)
             }
             });
             $.ajax({
             type: 'POST',
             url: $('#urls').attr('data-unvoice-url'),
             data: {"id": updated_ready_numbers[i]},
             dataType: 'json',
             success: function (data) {
             }
             }
             ).fail(function () {
             // alert('У вас нет прав!');
             });
             }, 3000);
             }*/

        },
        complete: function () {
            setTimeout(refresher, 10000);
        }
    });
}

function process_numbers(updated_ready_numbers, voiced_flags) {
    $.each(updated_ready_numbers, function (index, value) {
        setTimeout(function () {
            if (!voiced_flags[index]) {
                aux = value;
                console.log(aux);
                sound_number(value);
                $.ajaxSetup({
                    beforeSend: function (xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken)
                    }
                });
                $.ajax({
                        type: 'POST',
                        url: $('#urls').attr('data-unvoice-url'),
                        data: {"daily_number": value},
                        dataType: 'json',
                        success: function (data) {
                            console.log('Success ' + aux);
                        }
                    }
                ).fail(function () {
                    console.log('Failed ' + aux);
                });
            }
        }, 3000 * index);
    });
}

function sound_number(value) {
    var str_value = value.toString();
    var aux_str_100 = '';
    var aux_str_10 = '';
    var aux_str = '#speaker-' + value;
    if (value > 20 && value % 10 != 0)
    {
        if (str_value.length==3){
            aux_str_100 = '#speaker-' + parseInt(str_value[0])*100;
            aux_str_10 = '#speaker-' + parseInt(str_value[1])*10;
            aux_str = '#speaker-' + str_value[2];
            console.log(aux_str_100);
            console.log(aux_str_10);
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
                $(aux_str_100)[0].play();
            }, 1500);
            setTimeout(function () {
                $(aux_str_10)[0].play();
            }, 2250);
            setTimeout(function () {
                $(aux_str)[0].play();
            }, 3000);
            $(aux_str)[0].load();
        }
        else {
            aux_str_10 = '#speaker-' + parseInt(str_value[0])*10;
            aux_str = '#speaker-' + str_value[1];
            console.log(aux_str_10);
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
                $(aux_str_10)[0].play();
            }, 1500);
            setTimeout(function () {
                $(aux_str)[0].play();
            }, 2250);
            $(aux_str)[0].load();
        }

    }
    else {
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
    }
    //ready_order_numbers = ready_order_numbers.push(value);
}
