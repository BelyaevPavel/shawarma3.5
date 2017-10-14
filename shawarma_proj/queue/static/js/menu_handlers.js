/**
 * Created by paul on 15.07.17.
 */
$(document).ready(function () {
    $('#menu').addClass('active');
});

var currOrder = [];
var total = 0;
var res = ""
var csrftoken = $("[name=csrfmiddlewaretoken]").val();

$('.next-to-prepare-item').on

$(function () {
    $('.subm').on('click', function (event) {
        var confirmation = confirm("Подтвердить заказ?");
        var form = $('.subm');
        var is_paid = true;
        if ($('#is_paid').attr('checked') != 'checked')
            is_paid = false;
        var paid_with_cash = true;
        if ($('#paid_with_cash').attr('checked') != 'checked')
            paid_with_cash = false;
        if (confirmation == true) {
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken)
                }
            });
            $.ajax({
                    type: 'POST',
                    url: form.attr('data-send-url'),
                    data: {
                        "order_content": JSON.stringify(currOrder),
                        "is_paid": JSON.stringify(is_paid),
                        "paid_with_cash": JSON.stringify(paid_with_cash)
                    },
                    dataType: 'json',
                    success: function (data) {
                        alert('Заказ добавлен!');
                        currOrder = [];
                        DrawOrderTable();
                        CalculateTotal();
                    }
                }
            ).fail(function () {
                alert('У вас нет права добавлять заказ!');
            });
        }
        else {
            event.preventDefault();
        }
    });
});


function Remove(index) {
    var quantity = $('#count-to-remove-' + index).val();
    if (currOrder[index]['quantity'] - quantity <= 0)
        currOrder.splice(index, 1);
    else
        currOrder[index]['quantity'] = parseInt(currOrder[index]['quantity']) - parseInt(quantity);
    CalculateTotal();
    DrawOrderTable();
}

function Add(id, title, price) {
    var quantity = $('#count-' + id).val();
    var note = $('#note-' + id).val();
    $('#note-' + id).val('');
    $('#count-' + id).val('1');
    var index = FindItem(id, note);
    if (index == null) {
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
        currOrder[index]['quantity'] = parseInt(quantity) + parseInt(currOrder[index]['quantity']);
    }
    CalculateTotal();
    DrawOrderTable();
}

function FindItem(id, note) {
    var index = null;
    for (var i = 0; i < currOrder.length; i++) {
        if (currOrder[i]['id'] == id && currOrder[i]['note'] == note) {
            index = i;
            break;
        }
    }
    return index;
}

function DrawOrderTable() {
    $('table.currentOrderTable tbody tr').remove();
    for (var i = 0; i < currOrder.length; i++) {
        $('table.currentOrderTable').append(
            '<tr class="currentOrderRow" index="' + i + '"><td class="currentOrderTitleCell">' +
            '<div>' + currOrder[i]['title'] + '</div><div class="noteText">' + currOrder[i]['note'] + '</div>' +
            '</td><td class="currentOrderActionCell">' + 'x' + currOrder[i]['quantity'] +
            '<input type="text" value="1" class="quantityInput" id="count-to-remove-' + i + '">' +
            '<button class="btnRemove" onclick="Remove(' + i + ')">Убрать</button>' +
            '</td></tr>'
        );
    }
}

function CalculateTotal() {
    total = 0;
    for (var i = 0; i < currOrder.length; i++) {
        total += currOrder[i]['price'] * currOrder[i]['quantity'];
    }
    $('p.totalDisplay').text(total);
}