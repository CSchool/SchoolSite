$(document).ready(function () {

    var relativesTable = $('#relativesTable');

    var relativesDatatable = relativesTable.DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": dataUrl,
         columnDefs: [
            {width: "5%", orderable: false, searchable: false, targets: 3},
            {className: "text-center", targets: "_all"}
        ]
    });

    relativesTable.on('click', 'button', function () {
        var id = $(this).data('relative');
        var row = relativesDatatable.row($(this).parents('tr'));
        var relative_cell = relativesDatatable.cell(row, 3).node();

        var relative_value = ($('select', relative_cell).val());

        $.ajax({
            url: requestUrl,
            type: "POST",
            data: JSON.stringify({relative_id: id}),
            cache:false,
            dataType: "json",
            success: function(resp){
                relativesDatatable.draw(false);
                console.log(resp);
            }
        });
    });
});