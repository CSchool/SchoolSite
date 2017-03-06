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

        $.ajax({
            url: requestUrl,
            type: "POST",
            data: JSON.stringify({relative_id: id}),
            cache:false,
            dataType: "json",
            success: function(resp){
                console.log(resp);
            }
        });
        //$.get(requestUrl, {relative_id: id});
    });
});