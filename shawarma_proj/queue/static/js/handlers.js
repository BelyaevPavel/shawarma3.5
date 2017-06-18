/**
 * Created by paul on 23.05.17.
 */

var currOrder = [];
var total = 0;
$(function () {
        $('form#order_content').on('submit', function(event){
            var confirmation = confirm("Confirm Order?");
            if (confirmation==true){
                $("#order_content").submit();
            }
            else {
                event.preventDefault();
            }
        });
    });


function ConfirmOrder(e) {
    var confirmation = confirm("Confirm Order?");
    if (confirmation==true){
        $("#order_content").submit();
    }
    else {
        e.preventDefault();
    }
}

function Remove(index) {
    $('tr[index="' + index + '"]').remove();
    currOrder.splice(index, 1);
    CalculateTotal();
    DrawOrderTable();
    $('p.totalDisplay').text(total);
    var id_string = "";
    for (var i = 0; i < currOrder.length; i++) {
        id_string += currOrder[i][0] + ',';
    }
    $('input[name=id_collector]').attr('value', id_string);
}

function Add(id, title, price) {
    currOrder.push([id, title, price]);
    CalculateTotal();
    DrawOrderTable();
    $('p.totalDisplay').text(total);
    var id_string = "";
    for (var i = 0; i < currOrder.length; i++) {
        id_string += currOrder[i][0] + ',';
    }
    $('input[name=id_collector]').attr('value', id_string);
}

function DrawOrderTable() {
    $('table.currentOrderTable tbody tr').remove();
    for (var i = 0; i < currOrder.length; i++) {
        $('table.currentOrderTable').append(
            '<tr class="currentOrderRow" index="' + i + '"><td class="currentOrderTitleCell">' +
            currOrder[i][1] + '</td><td class="currentOrderActionCell">' +
            '<button class="btnRemove" onclick="Remove(' + i + ')">-</button>' +
            '</td></tr>'
        );
    }
}

function DrawQueueTable() {

}

function CalculateTotal() {
    total = 0;
    for (var i = 0; i < currOrder.length; i++) {
        total += currOrder[i][2];
    }
}