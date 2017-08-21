/**
 * Created by paul on 23.07.17.
 */
$(document).ready(function () {
    var test = $('#person-prod-cooked');
    Plotly.plot(test, [{
        x: [1, 2, 3, 4, 5],
        y: [1, 2, 4, 8, 16]}], {
        margin: { t: 0 } }
    );
});