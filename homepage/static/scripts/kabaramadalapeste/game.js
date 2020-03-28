$(window).on("resize", function() {
    $("#resize_modal").modal();
});
$("#resize_modal_btn").click(function() {
    location.reload(false);
});
let gps_start = 0,
    gps_animation_mode,
    dx,
    dy;

function gps_anime() {
    if (gps_start !== 0) {
        let delta = new Date() - gps_start;
        if (gps_animation_mode) {
            if (delta > 300) {
                data.layer.x(dx);
                data.layer2.x(dx);
                data.layer.batchDraw();
                data.layer2.batchDraw();
                gps_start = 0;
            } else {
                data.layer.x(10 * Math.sin((delta * 2 * Math.PI) / 10) + dx);
                data.layer2.x(data.layer.x());
                data.layer.batchDraw();
                data.layer2.batchDraw();
            }
        } else {
            if (delta > 1000) {
                gps_start = 0;
            } else {
                data.layer.x(
                    (data.layer.x() * (1000 - delta)) / 1000 +
                        (dx * delta) / 1000
                );
                data.layer.y(
                    (data.layer.y() * (1000 - delta)) / 1000 +
                        (dy * delta) / 1000
                );
                data.layer2.x(data.layer.x());
                data.layer2.y(data.layer.y());
                data.layer.batchDraw();
                data.layer2.batchDraw();
            }
        }
    }
    requestAnimationFrame(gps_anime);
}
setTimeout(function() {
    gps_anime();
}, 1000);
$(".gps").click(function() {
    dx =
        data.stage.width() / 2 -
        data.ship.elem.x() -
        data.ship.elem.width() / 2;
    dy =
        data.stage.height() / 2 -
        data.ship.elem.y() -
        data.ship.elem.height() / 2;

    data.layer.margin.x = Math.max(
        data.layer.margin.x,
        dx,
        data.stage.width() - data.back.width - dx
    );
    data.layer.margin.y = Math.max(
        data.layer.margin.y,
        dy,
        data.stage.height() - data.back.height - dy
    );
    gps_animation_mode = 0;
    if (
        Math.abs(dx - data.layer.x()) < 1 &&
        Math.abs(dy - data.layer.y()) < 1
    ) {
        gps_animation_mode = 1;
    }
    gps_start = new Date();
});
