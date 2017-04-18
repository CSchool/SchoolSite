$(document).ready(function () {

    var relativesTable = $('#relativesTable');

    var relativesDatatable = relativesTable.DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": dataUrl,
        "language": {
            "url": langUrl
        },
         columnDefs: [
            {width: "5%", orderable: false, searchable: false, targets: 3},
            {className: "text-center", targets: "_all"}
        ]
    });

    relativesTable.on('click', '.datatables_send_parent', function () {
        var id = $(this).data('relative');

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

    relativesTable.on('click', '.datatables_send_child', function () {
        var id = $(this).data('child');

        $.ajax({
            url: requestUrl,
            type: "POST",
            data: JSON.stringify({child_id: id}),
            cache:false,
            dataType: "json",
            success: function(resp){
                relativesDatatable.draw(false);
                console.log(resp);
            }
        });
    });
});