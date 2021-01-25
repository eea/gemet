$ = django.jQuery;
$(document).ready(function () {
    $('input.start-import').click(function (event) {
        url = window.location.href.split("admin")[0] + "import/" + $(this)[0].id + "/start/";
        $.ajax({
            url: url, success: function (result) {
                alert("Import started successfully.");
                location.reload();
            }
        });
    });
});
