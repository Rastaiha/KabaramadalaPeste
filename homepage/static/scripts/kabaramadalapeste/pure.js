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

function show_jazire_info(jazire) {
    pos = get_jazire_info_position(jazire);
    jazire_info.addClass("hide");
    jazire_info.removeClass("show");
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
