/**
 * Created by paul on 23.05.17.
 */

var currOrder = [];
var total = 0;
var res = ""
var csrftoken = $("[name=csrfmiddlewaretoken]").val();

$(function () {
    $('.subm').on('click', function (event) {
        var confirmation = confirm("Confirm Order?");
        var form = $('.subm');
        if (confirmation == true) {
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken)
                }
            });
            $.ajax({
                type: 'POST',
                url: form.attr('data-send-url'),
                data: {"order_content": JSON.stringify(currOrder)},
                dataType: 'json',
                success: function (data) {
                    alert('Success!');
                    $('.response').text(data.received);
                    res = data.received;
                    currOrder = [];
                    DrawOrderTable();
                    CalculateTotal();
                }
            }
            );
        }
        else {
            event.preventDefault();
        }
    });
});


function Remove(index) {
    var quantity = $('#count-to-remove-'+index).val();
    if (currOrder[index]['quantity']-quantity<=0)
        currOrder.splice(index, 1);
    else
        currOrder[index]['quantity'] = parseInt(currOrder[index]['quantity'])-parseInt(quantity);
    CalculateTotal();
    DrawOrderTable();
}

function Add(id, title, price) {
    var quantity = $('#count-'+id).val();
    var note = $('#note-'+id).val();
    var index = FindItem(id, note);
    if (index == null){
        currOrder.push(
            {
                'id': id,
                'title': title,
                'price': price,
                'quantity': quantity,
                'note': note
            }
        );
    }
    else {
        currOrder[index]['quantity'] = parseInt(quantity)+parseInt(currOrder[index]['quantity']);
    }
    CalculateTotal();
    DrawOrderTable();
}

function FindItem(id, note) {
    var index = null;
    for (var i = 0; i < currOrder.length; i++) {
        if (currOrder[i]['id']==id && currOrder[i]['note'] == note) {
            index = i;
            console.log('true'+index);
            break;
        }
        else
            console.log('false');
    }
    return index;
}

function DrawOrderTable() {
    $('table.currentOrderTable tbody tr').remove();
    for (var i = 0; i < currOrder.length; i++) {
        $('table.currentOrderTable').append(
            '<tr class="currentOrderRow" index="' + i + '"><td class="currentOrderTitleCell">' +
            '<p>'+currOrder[i]['title'] + '</p><p class="noteText">'+currOrder[i]['note']+'</p>'+
            '</td><td class="currentOrderActionCell">' +'x'+currOrder[i]['quantity']+
            '<input type="text" value="1" class="quantityInput" id="count-to-remove-' + i + '">' +
            '<button class="btnRemove" onclick="Remove(' + i + ')">Depricate</button>' +
            '</td></tr>'
        );
    }
}

function DrawQueueTable() {

}

function CalculateTotal() {
    total = 0;
    for (var i = 0; i < currOrder.length; i++) {
        total += currOrder[i]['price']*currOrder[i]['quantity'];
    }
    $('p.totalDisplay').text(total);
}

function Take(id) {
    var row = $('[index=' + id + ']');
    var url = $('#free-items').attr('data-take-url');
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
            'maker_id': 1
        },
        dataType: 'json',
        success: function (data) {
            alert('Success!' + data);
            row.addClass('inProduction');
            $('[index=' + id + '] button.btnTake').prop('disabled', true);
        }
    });
}

function ToGrill(id) {
    $('table#items-grill tbody').append(
        '<tr class="currentOrderRow" index="' + i + '"><td class="currentOrderTitleCell">' +
        '<p>' + currOrder[i]['title'] + '</p><p class="noteText">' + currOrder[i]['note'] + '</p>' +
        '</td><td class="currentOrderActionCell">' + 'x' + currOrder[i]['quantity'] +
        '<input type="text" value="1" class="quantityInput" id="count-to-remove-' + i + '">' +
        '<button class="btnRemove" onclick="Remove(' + i + ')">Depricate</button>' +
        '</td></tr>');
}