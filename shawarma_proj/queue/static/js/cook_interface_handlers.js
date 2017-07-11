/**
 * Created by paul on 10.07.17.
 */
$(document).ready(AdjustLineHeight);
$(window).resize(AdjustLineHeight);

function AdjustLineHeight() {
   $('div.next-to-prepare-item').css('line-height', $('div.next-to-prepare-item').css('height'));
   $('div.in-progress-item').css('line-height', $('div.in-progress-item').css('height'));
}

function TakeItem(id) {
    var url = $('#urls').attr('data-take-url');
    var confirmation = confirm("Take item?");
    if(confirmation){
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

function ItemToGrill(id) {
    var url = $('#urls').attr('data-grill-url');
    var confirmation = confirm("Grill item?");
    if(confirmation) {
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
    if(confirmation) {
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
            }
        });
    }
}