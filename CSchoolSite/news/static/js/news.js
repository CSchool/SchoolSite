function dismiss(id) {
    $.post('', {
        'dismiss': id
    }, function() {
        $('#notification-' + id).slideUp()
    })
}