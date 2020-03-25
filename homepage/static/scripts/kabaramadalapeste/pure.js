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

function show_island_info(island) {
    pos = get_island_info_position(island);
    island_info.addClass("hide");
    island_info.removeClass("show");
    island_info.find(".island-name span").text(island.name);
    island_info.find(".island_kind span").text("معما");
    island_info
        .find(".island_persons span")
        .text(Math.floor(Math.random() * 30));

    let is_solved = Math.floor(Math.random() * 4);
    switch (is_solved) {
        case 0:
            island_info.find(".island-info-question span").text("حل نشده");
            break;
        case 1:
            island_info.find(".island-info-question span").text("در دست تصحیح");
            break;
        case 2:
            island_info.find(".island-info-question span").text("جواب صحیح");
            break;
        case 3:
            island_info.find(".island-info-question span").text("جواب غلط");
            break;
        default:
            island_info.find(".island-info-question span").text("حل نشده");
            break;
    }

    let is_open = Math.floor(Math.random() * 2);
    if (is_open) {
        island_info.find(".island-info-ganj span").text("باز شده");
        island_info
            .find(".island-info-ganj img")
            .attr("src", "/static/images/game/ganj_open.png");
    } else {
        island_info.find(".island-info-ganj span").text("باز نشده");
        island_info
            .find(".island-info-ganj img")
            .attr("src", "/static/images/game/ganj.png");
    }

    let check_time = " لحظه";
    let check_time_random = Math.floor(Math.random() * 4) * 5;
    if (check_time_random) {
        check_time = check_time_random + " دقیقه";
    }
    island_info.find(".island-info-check-time span").text(check_time);

    if (island.id === data.ship.island_id) {
        island_info.find(".island-info-action a").text("لنگر انداختن");
        $("#travel_modal .modal-title").text("لنگر انداختن");
        $("#travel_modal .modal-question").text(
            "هزینه لنگر انداختن ۲ سکه است. آیا مایل به آن هستید؟"
        );
        island_info
            .find(".island-info-action a")
            .css("display", "inline-block");
        $("#travel_modal_btn").data("kind", "langar");
        $("#travel_modal_btn").data("island_id", island.id);
    } else if (
        get_island(data.ship.island_id).neighborhoods.includes(island.id)
    ) {
        island_info.find(".island-info-action a").text("سفر");
        $("#travel_modal .modal-title").text("سفر");
        $("#travel_modal .modal-question").text(
            "هزینه سفر ۲ سکه است. آیا مایل به آن هستید؟"
        );
        island_info
            .find(".island-info-action a")
            .css("display", "inline-block");
        $("#travel_modal_btn").data("kind", "travel");
        $("#travel_modal_btn").data("island_id", island.id);
    } else {
        island_info.find(".island-info-action a").data("target", "");
        island_info.find(".island-info-action a").text("");
        island_info.find(".island-info-action a").css("display", "none");
        $("#travel_modal_btn").data("kind", "");
        $("#travel_modal_btn").data("island_id", "");
    }

    setTimeout(() => {
        island_info.css("left", pos.x + "px");
        island_info.css("top", pos.y + "px");

        island_info.removeClass("hide");
        island_info.addClass("show");
    }, 100);
}

function show_player_info() {
    $(".player-info .right-info-btn").click();
}

$("#travel_modal_btn").click(function() {
    if ($(this).data("kind") === "travel") {
        island_info.addClass("hide");
        island_info.removeClass("show");
        change_target(null);
        $("#travel_modal").modal("hide");
        data.ship.island_id = $(this).data("island_id");
        island = get_island($(this).data("island_id"));
        data.ship.elem.x(island.elem.x() - 10);
        data.ship.elem.y(island.elem.y() - 10);
    } else if ($(this).data("kind") === "langar") {
        window.location.href = "/game/island/";
    }
});
