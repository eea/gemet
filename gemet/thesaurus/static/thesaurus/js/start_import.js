$ = django.jQuery;
$(document).ready(function () {
    $('input.start-import').click(function () {
        url = window.location.href.split("admin")[0] + "import/" + $(this)[0].id + "/start/";
        $.ajax({
            url: url, success: function (result) {
                location.reload();
            }
        });
    });
});
