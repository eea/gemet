$ = django.jQuery;
$(document).ready(function () {
    $('input.start-import').click(function () {
        url = window.location.origin + "/import/" + $(this)[0].id + "/start/";
        $.ajax({ url: url });
        location.reload();
    });
});
