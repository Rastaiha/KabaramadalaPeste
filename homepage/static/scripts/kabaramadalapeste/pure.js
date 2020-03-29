function get_island_info_position(island) {
    let x = island.elem.x() + data.layer.x() + island.elem.width() + 10,
        y = island.elem.y() + data.layer.y() + island.elem.height() / 2;
    if (data.stage.width() / 2 < island.elem.x() + data.layer.x()) {
        x -= 150 + island.elem.width() / 2 + 10;
    }
    if (data.stage.height() / 2 < island.elem.y() + data.layer.y()) {
        y -= island_info.height() / 2 + island.elem.height() / 2;
    }
    return {
        x: Math.max(10, Math.min(x, data.stage.width() - 150 - 30)),
        y: Math.max(
            10,
            Math.min(y, data.stage.height() - island_info.height() - 30)
        )
    };
}

function get_island(island_id) {
    island_id = parseInt(island_id);
    for (let i = 0; i < data.islands.length; i++) {
        const island = data.islands[i];
        if (island.id === island_id) {
            return island;
        }
    }
}

function update_sttings(response) {
    data.move_price = response.move_price;
    data.put_anchor_price = response.put_anchor_price;
}

function update_island_info(response) {
    if (response.island_id === 20 && data.ship.island_id === 20) {
        island_info.addClass("in_bandargah");
    } else {
        island_info.removeClass("in_bandargah");
    }
    if (response.island_id === 20) {
        island_info.addClass("bandargah");
        island_info.find(".island-name span").text("بندرگاه");
    } else {
        island_info.removeClass("bandargah");
        island_info.find(".island-name span").text("جزیره " + response.name);
    }
    island_info.find(".island_kind span").text(response.challenge_name);
    island_info.find(".island_persons span").text(response.participants_inside);
    switch (response.submit_status) {
        case "No":
            island_info.find(".island-info-question span").text("حل نشده");
            break;
        case "Pending":
            island_info.find(".island-info-question span").text("درحال تصحیح");
            break;
        case "Correct":
            island_info.find(".island-info-question span").text("پاسخ صحیح");
            break;
        case "Wrong":
            island_info.find(".island-info-question span").text("پاسخ نادرست");
            break;
    }
    if (response.did_open_treasure) {
        island_info.find(".island-info-ganj").removeClass("can-see-keys");
        island_info.find(".island-info-ganj span").text("باز شده");
        island_info
            .find(".island-info-ganj img")
            .attr("src", "/static/images/game/ganj_open.png");
    } else {
        if (response.treasure_keys !== "unknown") {
            island_info.find(".island-info-ganj").addClass("can-see-keys");
            island_info
                .find(".need-keys")
                .data("treasure_keys_persian", response.treasure_keys_persian);
        } else {
            island_info.find(".island-info-ganj").removeClass("can-see-keys");
        }
        island_info.find(".island-info-ganj span").text("باز نشده");
        island_info
            .find(".island-info-ganj img")
            .attr("src", "/static/images/game/ganj.png");
    }
    let check_time = " لحظه";
    if (response.judge_estimated_minutes) {
        check_time = response.judge_estimated_minutes + " دقیقه";
    }
    island_info.find(".island-info-check-time span").text(check_time);
}

$(".need-keys").click(function() {
    my_alert($(this).data("treasure_keys_persian"), "کلید‌های مورد نیاز");
});

function is_current_island(island_id) {
    return island_id === data.ship.island_id;
}

function is_neighbor(island_id) {
    return get_island(data.ship.island_id).neighborhoods.includes(island_id);
}

function update_island_info_btn(island_id) {
    return get_player_info().then(player_info => {
        let action = "";
        let btn_text = "";
        if (is_current_island(island_id)) {
            action = "langar";
            if (player_info.currently_anchored) {
                btn_text = "بازگشت به جزیره";
            } else if (island_id === 20) {
                action = "invest";
                btn_text = "سرمایه‌گذاری";
            } else {
                btn_text = "لنگر انداختن";
            }
        } else if (player_info.has_free_travel || is_neighbor(island_id)) {
            action = "travel";
            if (player_info.currently_anchored) {
                btn_text = "سفر و برداشتن لنگر";
            } else {
                btn_text = "سفر";
            }
        }
        island_info.find(".island-info-action a").data("kind", action);
        island_info.find(".island-info-action a").text(btn_text);

        if (action) {
            island_info
                .find(".island-info-action a")
                .css("display", "inline-block");
        } else {
            island_info.find(".island-info-action a").css("display", "none");
        }
        return {
            action: action,
            player_info: player_info,
            island_id: island_id
        };
    });
}

function update_modal(response) {
    let title = "";
    let question = "";
    if (
        response.action === "langar" &&
        !response.player_info.currently_anchored
    ) {
        title = "لنگر انداختن";
        question =
            "هزینه لنگر انداختن " +
            data.put_anchor_price +
            " سکه است. آیا مایل به آن هستید؟";
    } else if (response.action === "travel") {
        if (response.player_info.currently_anchored) {
            title = "سفر و برداشتن لنگر";
            question =
                "هزینه سفر " +
                data.move_price +
                " سکه است. آیا مایل به آن هستید؟" +
                "</br><small style='color:#222; font-weight: 300'>" +
                "دقت کنید لنگر شما از جزیره‌ای که در آن هستید برداشته خواهد شد." +
                "</small>";

            if (response.player_info.has_free_travel) {
                question =
                    "هزینه سفر رایگان است. آیا مایل به آن هستید؟" +
                    "</br><small style='color:#222; font-weight: 300'>" +
                    "دقت کنید لنگر شما از جزیره‌ای که در آن هستید برداشته خواهد شد." +
                    "</small>";
            }
        } else {
            title = "سفر";
            question =
                "هزینه سفر " +
                data.move_price +
                " سکه است. آیا مایل به آن هستید؟";
            if (response.player_info.has_free_travel) {
                question = "هزینه سفر رایگان است. آیا مایل به آن هستید؟";
            }
        }
    }
    my_prompt(question, title, {
        kind: response.action,
        island_id: response.island_id
    });
    return response.island_id;
}

function is_currently_anchored() {
    return get_player_info().then(player_info => {
        return player_info.currently_anchored;
    });
}

function hide_island_info() {
    if (island_info.hasClass("show")) {
        island_info.removeClass("show");
        island_info.addClass("hide");
    }
}

function show_island_info(island) {
    setTimeout(() => {
        pos = get_island_info_position(island);
        island_info.css("left", pos.x + "px");
        island_info.css("top", pos.y + "px");
        island_info.removeClass("hide");
        island_info.addClass("show");
    }, 100);
}

function update_and_show_island_info(island) {
    settings()
        .then(update_sttings)
        .then(hide_island_info)
        .then(() => update_island_info_btn(island.id))
        .then(update_modal)
        .then(get_island_info)
        .then(update_island_info)
        .then(() => show_island_info(island))
        .catch(default_fail);
}

function show_player_info() {
    $(".player-info .right-info-btn").click();
}

function travel(island_id) {
    data.ship.island_id = island_id;
    island = get_island(island_id);
    data.ship.elem.x(island.elem.x() - 15);
    data.ship.elem.y(island.elem.y() - 15);
}

$("#prompt_modal_btn").click(function() {
    if ($(this).data("kind") === "travel") {
        let island_id = $(this).data("island_id");
        move_to(island_id)
            .then(() => travel(island_id))
            .catch(default_fail);
        $("#prompt_modal").modal("hide");
        hide_island_info();
        change_target(null);
    } else if ($(this).data("kind") === "langar") {
        is_currently_anchored()
            .then(currently_anchored => {
                if (!currently_anchored) {
                    return put_anchor();
                }
            })
            .then(() => (window.location.href = "/game/island/"))
            .catch(default_fail);
        $("#prompt_modal").modal("hide");
        hide_island_info();
        change_target(null);
    } else if ($(this).data("kind") === "invest") {
        $("#prompt_modal").modal("hide");
        invest(invest_input.value)
            .then(() => {
                my_alert("سرمایه‌گذاریت انجام شد.", "سرمایه‌گذاری");
            })
            .catch(default_fail);
    }
});
let invest_input = document.getElementById("invest_input");

$(".island-info-action a").click(function() {
    if ($(this).data("kind") === "langar") {
        is_currently_anchored()
            .then(currently_anchored => {
                if (currently_anchored) {
                    window.location.href = "/game/island/";
                } else {
                    $("#prompt_modal").modal("show");
                }
            })
            .catch(default_fail);
    } else if ($(this).data("kind") === "invest") {
        if (invest_input.checkValidity()) {
            my_prompt(
                "آیا می‌خوای بر روی بندرگاه " +
                    invest_input.value +
                    " سکه سرمایه‌گذاری کنی؟",
                "سرمایه‌گذاری",
                {
                    kind: "invest"
                }
            );
            $("#prompt_modal").modal("show");
        } else {
            invest_input.setCustomValidity(invest_input.validationMessage);
            invest_input.reportValidity();
            setTimeout(function() {
                invest_input.setCustomValidity("");
            }, 1000);
        }
    } else {
        $("#prompt_modal").modal("show");
    }
});

function get_other_players() {
    all_players_info().then(other_players => {
        for (let i = 0; i < data.op.length; i++) {
            data.op[i].un = "";
            data.op[i].pp = "";
            data.op[i].elem.setAttrs({
                x: -100,
                y: -100
            });
        }
        for (let i = 0; i < other_players.length; i++) {
            island = get_island(other_players[i].ii);
            let direction = Math.floor(Math.random() * 4);
            let x = island.elem.x();
            let y = island.elem.y();
            if (direction === 0) {
                x += Math.floor(Math.random() * island.elem.width());
            }
            if (direction === 1) {
                y += Math.floor(Math.random() * island.elem.height());
            }
            if (direction === 2) {
                x += island.elem.width();
                y += Math.floor(Math.random() * island.elem.height());
            }
            if (direction === 3) {
                y += island.elem.height();
                x += Math.floor(Math.random() * island.elem.width());
            }
            data.op[i].elem.setAttrs({
                x: x,
                y: y
            });
            data.op[i].un = other_players[i].un;
            data.op[i].pp = other_players[i].pp;
        }
    });

    setTimeout(get_other_players, 60000);
}
