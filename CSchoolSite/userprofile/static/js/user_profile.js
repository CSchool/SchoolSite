$(document).ready(function () {


    var relationshipTable = $('#relationshipTable');

    var relationshipDatatable = relationshipTable.DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": dataUrl,
        "searching": false,
        "language": {
            "url": langUrl
        },
         columnDefs: [
            {width: "10%", orderable: false, searchable: false, targets: 3},
            {className: "text-center", targets: "_all"}
        ]
    });
});