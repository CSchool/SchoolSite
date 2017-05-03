$(document).ready(function() {
    var enrolledTable = $("#enrolledTable");

    var enrolledDatatable = enrolledTable.DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": dataUrl,
        "language": {
            "url": langUrl,
        },
        "searching": true,
        "columnDefs": [
            {"targets": [3, 4, 5], "visible": false},
            {"targets": [1, 2], "orderable": false},
            {"targets": "_all", "visible": true, "searching": true}
        ],
        "createdRow": function(row, data, index) {
            $(row).addClass(data[3]);
        },
        "initComplete": function () {
            $('#enrolledTable_filter').hide()
            function add_select(ct, cs) {
                var select = $('<select class="form-control"><option value=""><b>--- ' + ct.header().innerText + ' ---</b></option></select>')
                    .appendTo($(ct.header()).empty())
                    .on('change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );

                        window.cs = cs;
                        window.val = val;

                        cs
                            .search(val ? val : '', false, false, false)
                            .draw();
                    });

                var d = ct.data().map(function (e, i) {
                    return [e, cs.data()[i]]
                });

                var flags = [];

                d.sort().each(function (d) {
                    if (flags[d[1]])
                        return;
                    flags[d[1]] = true;
                    select.append('<option value="' + d[1] + '">' + d[0] + '</option>')
                });
            }
            add_select(this.api().column(1), this.api().column(4));
            add_select(this.api().column(2), this.api().column(5));
        }
    })
});