/* jshint esversion: 6 */

function is_time(string) {
    return /^[0-2][0-9]:[0-5][0-9]$/.test(string);
}

function message_reset() {
    const message_div = $("#form-message");
    message_div.removeClass(function (index, className) {
        return (className.match(/(^|\s)alert-\S+/g) || []).join(' ');
    });
    message_div.text("");
}

function message_hide() {
    const message_div = $("#form-message");
    message_div.hide();
    message_reset();
}

function message_display(msg_type, content) {
    message_reset();
    const message_div = $("#form-message");
    message_div.addClass("alert-" + msg_type);
    message_div.text(content);
    message_div.show();
}

$("#form-parameters").submit(function (event) {
    event.preventDefault();

    var form = $(this);
    var url = form.attr('action');

    var days = [];
    $.each($("input[name='days']:checked"), function () {
        days.push($(this).val());
    });
    if (days.length <= 0) {
        message_display("warning", "Veuillez cocher au moins un jour");
    } else if (!is_time($("#day_start_time").val())) {
        message_display("warning", "L'heure de début des cours est incorrecte.");
    } else if (!is_time($("#day_end_time").val())) {
        message_display("warning", "L'heure de fin des cours est incorrecte.");
    } else if (!is_time($("#morning_end_time").val())) {
        message_display("warning", "L'heure de début du déjeuner est incorrecte.");
    } else if (!is_time($("#afternoon_start_time").val())) {
        message_display("warning", "L'heure de fin du déjeuner est incorrecte.");
    } else if ($("#day_start_time").val() > $("#day_end_time").val()) {
        message_display("warning", "L'heure de début des cours doit précéder l'heure de fin des cours.");
    } else if ($("#lunch_break_start_time").val() > $("#afternoon_start_time").val()) {
        message_display("warning", "L'heure de début du déjeuner doit précéder l'heure de fin du déjeuner.");
    } else if ($("#day_start_time").val()> $("#morning_end_time").val() || $("#afternoon_start_time").val() > $("#day_end_time").val()) {
        message_display("warning", "La période du déjeuner doit être pendant la période des cours.");
    }
    else {
        const button_html = $("#button-submit").html();
        $("#button-cancel").addClass('disabled');
        $("#button-submit").addClass('disabled');
        $("#button-submit").html("<i class=\"fas fa-spinner fa-pulse\"></i>");
        $.ajax({
            type: "POST",
            url: url,
            data: form.serializeArray(),
            success: function (response) {
                switch (response.status) {
                    case 'OK':
                        window.location.href = parametersUrl;
                        break;
                    case 'ERROR':
                        $("#button-submit").html(button_html);
                        $("#button-submit").removeClass('disabled');
                        $("#button-cancel").removeClass('disabled');
                        message_display("warning", response.message);
                        break;
                    case 'UNKNOWN':
                        $("#button-submit").html(button_html);
                        $("#button-submit").removeClass('disabled');
                        $("#button-cancel").removeClass('disabled');
                        message_display("warning", response.message);
                }

            },
            error: function (error) {
                $("#button-submit").html(button_html);
                message_display("warning", "Une erreur est survenue. Veuillez réessayer.");
            },
        });
    }
});
