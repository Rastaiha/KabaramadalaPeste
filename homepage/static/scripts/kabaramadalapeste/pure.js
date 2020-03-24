function get_jazire_info_position(jazire) {
    let x = jazire.elem.x() + data.layer.x() + jazire.elem.width() + 10,
        y = jazire.elem.y() + data.layer.y() + jazire.elem.height() / 2;
    if (data.stage.width() / 2 < jazire.elem.x() + data.layer.x()) {
        x -= 150 + jazire.elem.width() / 2 + 10;
    }
    if (data.stage.height() / 2 < jazire.elem.y() + data.layer.y()) {
        y -= jazire_info.height() / 2 + jazire.elem.height() / 2;
    }
    return {
        x: Math.max(10, Math.min(x, data.stage.width() - 150 - 30)),
        y: Math.max(
            10,
            Math.min(y, data.stage.height() - jazire_info.height() - 30)
        )
    };
}

function get_jazire(jazire_id) {
    jazire_id = parseInt(jazire_id);
    for (let i = 0; i < data.jazireha.length; i++) {
        const jazire = data.jazireha[i];
        if (jazire.id === jazire_id) {
            return jazire;
        }
    }
}

function show_jazire_info(jazire) {
    pos = get_jazire_info_position(jazire);
    jazire_info.addClass("hide");
    jazire_info.removeClass("show");
    jazire_info.find(".jazire-name span").text(jazire.name);
    jazire_info.find(".jazire_kind span").text("معما");
    jazire_info
        .find(".jazire_persons span")
        .text(Math.floor(Math.random() * 30));

    let is_solved = Math.floor(Math.random() * 4);
    switch (is_solved) {
        case 0:
            jazire_info.find(".jazire-info-question span").text("حل نشده");
            break;
        case 1:
            jazire_info.find(".jazire-info-question span").text("در دست تصحیح");
            break;
        case 2:
            jazire_info.find(".jazire-info-question span").text("جواب صحیح");
            break;
        case 3:
            jazire_info.find(".jazire-info-question span").text("جواب غلط");
            break;
        default:
            jazire_info.find(".jazire-info-question span").text("حل نشده");
            break;
    }

    let is_open = Math.floor(Math.random() * 2);
    if (is_open) {
        jazire_info.find(".jazire-info-ganj span").text("باز شده");
        jazire_info
            .find(".jazire-info-ganj img")
            .attr("src", "/static/images/game/ganj_open.png");
    } else {
        jazire_info.find(".jazire-info-ganj span").text("باز نشده");
        jazire_info
            .find(".jazire-info-ganj img")
            .attr("src", "/static/images/game/ganj.png");
    }

    let check_time = " لحظه";
    let check_time_random = Math.floor(Math.random() * 4) * 5;
    if (check_time_random) {
        check_time = check_time_random + " دقیقه";
    }
    jazire_info.find(".jazire-info-check-time span").text(check_time);

    if (jazire.id === data.ship.jazire_id) {
        jazire_info.find(".jazire-info-action a").text("لنگر انداختن");
        $("#travel_modal .modal-title").text("لنگر انداختن");
        $("#travel_modal .modal-question").text(
            "هزینه لنگر انداختن ۲ سکه می‌باشد. آیا مایل به آن هستید؟"
        );
        jazire_info
            .find(".jazire-info-action a")
            .css("display", "inline-block");
        $("#travel_modal_btn").data("kind", "langar");
        $("#travel_modal_btn").data("jazire_id", jazire.id);
    } else if (
        get_jazire(data.ship.jazire_id).neighborhoods.includes(jazire.id)
    ) {
        jazire_info.find(".jazire-info-action a").text("سفر");
        $("#travel_modal .modal-title").text("سفر");
        $("#travel_modal .modal-question").text(
            "هزینه سفر ۲ سکه می‌باشد. آیا مایل به آن هستید؟"
        );
        jazire_info
            .find(".jazire-info-action a")
            .css("display", "inline-block");
        $("#travel_modal_btn").data("kind", "travel");
        $("#travel_modal_btn").data("jazire_id", jazire.id);
    } else {
        jazire_info.find(".jazire-info-action a").data("target", "");
        jazire_info.find(".jazire-info-action a").text("");
        jazire_info.find(".jazire-info-action a").css("display", "none");
        $("#travel_modal_btn").data("kind", "");
        $("#travel_modal_btn").data("jazire_id", "");
    }

    setTimeout(() => {
        jazire_info.css("left", pos.x + "px");
        jazire_info.css("top", pos.y + "px");

        jazire_info.removeClass("hide");
        jazire_info.addClass("show");
    }, 100);
}

function show_player_info() {
    $(".player-info .right-info-btn").click();
}

$("#travel_modal_btn").click(function() {
    if ($(this).data("kind") === "travel") {
        jazire_info.addClass("hide");
        jazire_info.removeClass("show");
        change_target(null);
        $("#travel_modal").modal("hide");
        data.ship.jazire_id = $(this).data("jazire_id");
        jazire = get_jazire($(this).data("jazire_id"));
        data.ship.elem.x(jazire.elem.x() - 10);
        data.ship.elem.y(jazire.elem.y() - 10);
    }
});
