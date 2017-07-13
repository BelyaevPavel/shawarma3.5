/**
 * Created by paul on 10.07.17.
 */
$(document).ready(function () {
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
            console.log(data);
            $('div.in-grill-container').html(data['html']);
        },
        complete: function () {
            setTimeout(GrillRefresher, 5000);
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
            setTimeout(NextRefresher, 5000);
        }
    });
}


function AdjustLineHeight() {
    var ni_div = $('div.item-title');
    var ip_div = $('div.item-note');
    var ni_height = ni_div.height();
    $('div.item-title').lineHeight = '84px';
    ip_div.lineHeight = ip_div.height();
}

function TakeItem(id) {
    var url = $('#urls').attr('data-take-url');
    var confirmation = confirm("Take item?");
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
                if (data['success']) {
                    alert('Success!');
                }
                else {
                    alert('Already taken by ' + data['staff_maker'] + '!');
                }
            },
            complete: function () {
                location.reload();
            }
        });
    }

}

function ItemToGrill(id) {
    var url = $('#urls').attr('data-grill-url');
    var confirmation = confirm("Grill item?");
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
                alert('Success!' + data);
            },
            complete: function () {
                location.reload();
            }
        });
    }
}

function FinishItemCooking(id) {
    var url = $('#urls').attr('data-finish-url');
    var confirmation = confirm("Finish item?");
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
                alert('Success!' + data);
            },
            complete: function () {
                location.reload();
            }
        });
    }
}