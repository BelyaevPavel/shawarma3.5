/**
 * Created by paul on 23.05.17.
 */

var currOrder = [];
var total = 0;
function Remove(index) {
    $('tr[index="' + index + '"]').remove();
    currOrder.splice(index, 1);
    CalculateTotal();
    DrawTable();
    $('p.totalDisplay').text(total);
}

function Add(id, title, price) {
    currOrder.push([id, title, price]);
    CalculateTotal();
    DrawTable();
    $('p.totalDisplay').text(total);
}

function DrawTable() {
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

function CalculateTotal() {
    total = 0;
    for (var i = 0; i < currOrder.length; i++) {
        total += currOrder[i][2];
    }
}