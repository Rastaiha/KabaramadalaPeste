my_alert_obj = {};
function my_alert(
    message,
    title = "",
    dataset = {},
    modal_id = "#alert_modal"
) {
    if ($(modal_id).hasClass("show")) {
        if (typeof my_alert_obj[modal_id] === "undefined") {
            my_alert_obj[modal_id] = [];
            $(modal_id).on("hidden.bs.modal", function(e) {
                alert_obj = my_alert_obj[modal_id].pop();
                if (alert_obj) {
                    $(modal_id + " .modal-message").text(alert_obj.message);
                    $(modal_id + " .modal-title").text(alert_obj.title);
                    $(modal_id + "_btn").data(dataset);
                    $(modal_id).modal("show");
                }
            });
        }
        my_alert_obj[modal_id].push({
            message: message,
            title: title
        });
    } else {
        $(modal_id + " .modal-message").text(message);
        $(modal_id + " .modal-title").text(title);
        $(modal_id + "_btn").data(dataset);
        $(modal_id).modal("show");
    }
}

function my_prompt(question, title, dataset = {}, modal_id = "#prompt_modal") {
    $(modal_id + "_btn").data(dataset);
    $(modal_id + " .modal-title").text(title);
    $(modal_id + " .modal-question").html(question);
}

let recevied_slugs = [];

function check_notification() {
    notifications_unread_list()
        .then(response => {
            response.unread_list.forEach(notif => {
                if (!recevied_slugs.includes(notif.slug)) {
                    my_alert(
                        notif.data.text || notif.data.message,
                        notif.description || "پیام ادمین",
                        {
                            slug: notif.slug
                        }
                    );
                    recevied_slugs.push(notif.slug);
                }
            });
        })
        .catch(default_fail);
    setTimeout(check_notification, 30000);
}
check_notification();

$("#alert_modal_btn").click(function() {
    let slug = $(this).data("slug");
    if (slug) {
        mark_as_read(slug);
    }
});

function default_fail(jqXHR, textStatus) {
    if (textStatus === "error") {
        textStatus = "ایراد در ارتباط.";
    }
    let err_message = textStatus || "خطا";
    if (typeof jqXHR.responseJSON !== "undefined") {
        err_message = jqXHR.responseJSON.message || textStatus || "خطا";
    }
    if (
        err_message === "ایراد در ارتباط." &&
        $("#alert_modal").hasClass("show") &&
        $("#alert_modal .modal-message").text() === err_message
    ) {
        return;
    }
    my_alert(err_message, "خطا");
}

function toggle_right_info(elem) {
    if (
        $(elem)
            .parent()
            .hasClass("show-details")
    ) {
        $(".right-info").removeClass("show-details");
    } else {
        $(".right-info").removeClass("show-details");
        $(elem)
            .parent()
            .addClass("show-details");
    }
}
player_property_img = {
    SK: "coins.png",
    K1: "key1.png",
    K2: "key2.png",
    K3: "key3.png",
    VIS: "look.png",
    TXP: "attraction.png",
    CHP: "problem.png",
    BLY: "trap.png"
};

$(".right-info-btn").click(function() {
    let elem = this;
    if (
        $(elem)
            .parent()
            .hasClass("player-info")
    ) {
        get_player_info()
            .then(response => {
                $(".player-info .right-info-details h3").text(
                    response.username
                );
                $(".player-propties").html("");
                for (const key in response.properties) {
                    if (response.properties.hasOwnProperty(key)) {
                        $(".player-propties").append(
                            '<div class="player-proprty"><span><b class="proprty-count">' +
                                response.properties[key] +
                                ' </b>×</span><img src="/static/images/game/' +
                                player_property_img[key] +
                                '" /></div>'
                        );
                    }
                }
                toggle_right_info(elem);
            })
            .catch(default_fail);
    } else if (
        $(elem)
            .parent()
            .hasClass("notification-box")
    ) {
        notifications_all_list()
            .then(response => {
                if (response.all_count > 0) {
                    $(".notifications > div").html('<div class="line"></div>');
                    response.all_list.forEach(notif => {
                        $(".notifications > div").append(
                            '<div class="notification"><div class="circle"></div><span class="time">9:24 AM</span><b>' +
                                (notif.description || "پیام ادمین") +
                                "</b><p>" +
                                (notif.data.text || notif.data.message) +
                                "</p></div>"
                        );
                    });
                } else {
                    $(".notifications > div").append(
                        '<div class="notification">هیچ پیامی برای شما ارسال نشده</div>'
                    );
                }
                toggle_right_info(elem);
            })
            .catch(default_fail);
    } else {
        toggle_right_info(elem);
    }
});
