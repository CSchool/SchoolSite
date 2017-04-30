$(document).ready(function () {


    var relationshipTable = $('#relationshipTable');

    var relationshipDatatable = relationshipTable.DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": dataUrl,
        "language": {
            "url": langUrl
        },
        "searching": false,
         columnDefs: [
            {width: "10%", orderable: false, searchable: false, targets: 2},
            {orderable: false, searchable: false, targets: 1},
            {className: "text-center", targets: "_all"}
        ]
    });

    function formatSeconds(x) {
        if (x < 0)
            return '00:00';
        var m = Math.floor(x / 60);
        var s = Math.floor(x % 60);
        var f = function(q) {return (q < 10) ? '0' + q.toString() : q.toString()};
        return f(m) + ':' + f(s);
    }

    var timeRemaining = 0;
    var timeTicking = false;

    CHILD = 'child';
    PARENT = 'parent';

    var redo = null;

    setInterval(function() {
        if (!timeTicking) return;
        timeRemaining--;
        $('#addRelativeCodeTime').text(formatSeconds(timeRemaining));
        if (timeRemaining <= 0) {
            timeTicking = false;
            if (redo) redo();
        }
    }, 1000);

    $('#addRelativeModal').on("hidden.bs.modal", function () {
        timeTicking = false;
        redo = null;
        $('#addRelativeModalTitle').text('');
        $('#addRelativeCode').text('');
        $('#addRelativeCodeTime').text('');
    });

    function showRelModal(rel, title) {
        $('#addRelativeModal').modal('toggle');
        $('#addRelativeModalTitle').text(title);
        redo = function() {
            $.post(codeUrl, {
                'reltype': rel
            }, function(data) {
                $('#addRelativeCodeTime').text(formatSeconds(Math.floor(data['valid_for'])));
                $('#addRelativeCode').text(data['code']);
                timeRemaining = Math.floor(data['valid_for']);
                timeTicking = true;
            })
        };
        redo();
    }

    $('#addChildButton').click(function() {
        return showRelModal(CHILD, $(this).text())
    });
    $('#addParentButton').click(function() {
        return showRelModal(PARENT, $(this).text())
    });



    function showRedeemModal() {
        $('#redeemCodeModal').modal('toggle');
        $('#redeemCodeInitials').text('');
        $('#redeemCodeNotice').text('');
        $('#redeemCodeInfo').hide();
        $('#redeemCodeSubmit').prop('disabled', true);
        $('#redeemCodeInput').val('')
    }

    $('#redeemCodeButton').click(function() {
        return showRedeemModal();
    });

    $('#redeemCodeInput').on('input', function() {
        var val = $(this).val();
        $.post(infoUrl, {
            'code': val
        }, function(data) {
            if (data['found']) {
                $('#redeemCodeInitials').text(data['name']);
                $('#redeemCodeNotice').text(data['reltype']);
                $('#redeemCodeInfo').show();
                $('#redeemCodeSubmit').prop('disabled', false);
            } else {
                $('#redeemCodeInfo').hide();
                $('#redeemCodeSubmit').prop('disabled', true);
            }
        })
    });
});