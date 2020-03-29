let isMobile = false;
if (
    /(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(
        navigator.userAgent
    ) ||
    /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(
        navigator.userAgent.substr(0, 4)
    )
) {
    isMobile = true;
}

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
