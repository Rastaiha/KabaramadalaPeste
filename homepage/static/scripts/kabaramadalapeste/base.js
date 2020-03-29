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
    $(modal_id + "_btn").removeData();
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
prop_details = {
    SK: {
        src: "/static/images/game/coins.png",
        persian: "سکه"
    },
    K1: {
        src: "/static/images/game/key1.png",
        persian: "طلایی"
    },
    K2: {
        src: "/static/images/game/key2.png",
        persian: "آبی"
    },
    K3: {
        src: "/static/images/game/key3.png",
        persian: "قرمز"
    },
    VIS: {
        src: "/static/images/game/look.png",
        persian: "بینش غیبی"
    },
    TXP: {
        src: "/static/images/game/attraction.png",
        persian: "سفر اکسپرس"
    },
    CHP: {
        src: "/static/images/game/problem.png",
        persian: "چالش پلاس"
    },
    BLY: {
        src: "/static/images/game/trap.png",
        persian: "زورگیری"
    }
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
                $(".player-info-image").attr("src", response.picture_url);
                $(".player-info .right-info-details h3").text(
                    response.username
                );
                $(".player-propties").html("");
                for (const key in response.properties) {
                    if (response.properties.hasOwnProperty(key)) {
                        $(".player-propties").append(
                            '<div class="player-proprty"><span><b class="proprty-count">' +
                                response.properties[key] +
                                ' </b>×</span><img title="' +
                                prop_details[key].persian +
                                '" src="' +
                                prop_details[key].src +
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
                        let notif_time = new Date(notif.timestamp);
                        let notif_day = notif_time.getDay();
                        let today = new Date().getDay();
                        if (today - notif_day === 0) {
                            let am_pm = "AM";
                            if (notif_time.getHours() > 11) {
                                am_pm = "PM";
                            }
                            notif_time =
                                (notif_time.getHours() % 12) +
                                ":" +
                                notif_time.getMinutes() +
                                " " +
                                am_pm;
                        } else if ((today - notif_day) % 7 === 1) {
                            notif_time = "Yesterday";
                        } else {
                            var weekday = [
                                "Sunday",
                                "Monday",
                                "Tuesday",
                                "Wednesday",
                                "Thursday",
                                "Friday",
                                "Saturday"
                            ];
                            notif_time = weekday[notif_day];
                        }
                        $(".notifications > div").append(
                            '<div class="notification"><div class="circle"></div><span class="time">' +
                                notif_time +
                                "</span><b>" +
                                (notif.description || "پیام ادمین") +
                                "</b><p>" +
                                (notif.data.text || notif.data.message) +
                                "</p></div>"
                        );
                    });
                } else {
                    $(".notifications > div").html(
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

$(".abilities-btns a").click(function() {
    let ability_type = $(this).data("type");
    my_prompt(
        "آیا می‌خواهید از ویژگی " +
            prop_details[ability_type].persian +
            " استفاده کنید؟",
        "استفاده از ویژگی",
        { ability_type: ability_type }
    );
    $("#prompt_modal").modal("show");
});

$("#prompt_modal_btn").click(function() {
    let ability_type = $(this).data("ability_type");
    if (ability_type) {
        use_ability(ability_type)
            .then(() => {
                my_alert(
                    "ویژگی " +
                        prop_details[ability_type].persian +
                        " برای شما فعال شد.",
                    "فعال شدن ویژگی"
                );
            })
            .catch(default_fail);
    }
});

$(".edit-player-image").click(function() {
    $(".new-image-input").click();
});

$(".new-image-input").change(function() {
    if (this.files[0].size > 5000000) {
        this.setCustomValidity("Maximum limit is 4 MB.");
        this.reportValidity();
        this.value = "";
        setTimeout(function() {
            this.setCustomValidity("");
        }, 1000);
    } else {
        $(".new-image-form").submit();
    }
});
