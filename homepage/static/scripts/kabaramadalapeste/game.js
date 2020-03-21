function loadImages(sources) {
    return new Promise(resolve => {
        data.images = {};
        var loadedImages = 0;
        var numImages = sources.length;
        for (let i = 0; i < sources.length; i++) {
            const src = sources[i];
            data.images[src] = new Image();
            data.images[src].onload = function() {
                if (++loadedImages >= numImages) {
                    resolve();
                }
            };
            data.images[src].src = "/static/images/game/" + src;
        }
    });
}

function init_backgronud(layer) {
    data.back.elem = new Konva.Image({
        x: data.back.x,
        y: data.back.y,
        image: data.images[data.back.src],
        width: data.back.width,
        height: data.back.height
    });
    layer.on("dragstart dragmove mousedown", function() {
        document.body.style.cursor = "grabbing";
        if (layer.x() > 30) {
            layer.x(30);
        }
        if (layer.y() > 30) {
            layer.y(30);
        }
        if (layer.x() < data.stage.width() - data.back.elem.width() - 30) {
            layer.x(data.stage.width() - data.back.elem.width() - 30);
        }
        if (layer.y() < data.stage.height() - data.back.elem.height() - 30) {
            layer.y(data.stage.height() - data.back.elem.height() - 30);
        }
    });
    layer.add(data.back.elem);
}

let jazire_info = $(".jazire-info");

function change_target(layer, target = null) {
    if (target !== "reset_shadow") {
        data.target = target;
    }

    data.jazireha.forEach(jazire => {
        console.log(data.target);
        if (data.target !== jazire) {
            jazire.elem.scale({ x: 1, y: 1 });
            jazire.elem.shadowEnabled(false);
        } else {
            jazire.elem.scale({ x: 1.01, y: 1.01 });
            jazire.elem.shadowColor("#cccccc");
            jazire.elem.shadowEnabled(true);
        }
        layer.draw();
    });
}
function hover_jazire(jazire) {
    if (data.target !== jazire) {
        jazire.elem.scale({ x: 1.01, y: 1.01 });
        jazire.elem.shadowColor("#333333");
        jazire.elem.shadowEnabled(true);
    }
}

function init_jazireha(layer) {
    data.jazireha
        .sort((a, b) => (a.zIndex > b.zIndex ? 1 : -1))
        .forEach(jazire => {
            jazire.elem = new Konva.Image({
                x: jazire.x * data.back.width,
                y: jazire.y * data.back.height,
                image: data.images[jazire.src],
                width: jazire.width * data.back.width,
                height: jazire.height * data.back.height,
                shadowBlur: 2,
                shadowOpacity: 2,
                shadowOffset: { x: 2, y: 2 },
                shadowEnabled: false
            });

            jazire.elem.on("click touchend", function(e) {
                document.body.style.cursor = "pointer";
                if (data.target !== jazire) {
                    change_target(layer, jazire);
                    jazire_info.addClass("hide");
                    jazire_info.removeClass("show");
                    setTimeout(() => {
                        let x =
                                jazire.elem.x() +
                                layer.x() +
                                jazire.elem.width() +
                                10,
                            y =
                                jazire.elem.y() +
                                layer.y() +
                                jazire.elem.height() / 2;
                        if (
                            data.stage.width() / 2 <
                            jazire.elem.x() + layer.x()
                        ) {
                            x -= 150 + jazire.elem.width() / 2 + 10;
                        }
                        if (
                            data.stage.height() / 2 <
                            jazire.elem.y() + layer.y()
                        ) {
                            y -=
                                jazire_info.height() / 2 +
                                jazire.elem.height() / 2;
                        }
                        x = Math.max(
                            10,
                            Math.min(x, data.stage.width() - 150 - 30)
                        );
                        y = Math.max(
                            10,
                            Math.min(
                                y,
                                data.stage.height() - jazire_info.height() - 30
                            )
                        );
                        jazire_info.css("left", x + "px");
                        jazire_info.css("top", y + "px");

                        jazire_info.removeClass("hide");
                        jazire_info.addClass("show");
                    }, 100);
                }

                e.evt.preventDefault();
                e.cancelBubble = true;
            });
            jazire.elem.on("dragstart dragmove mouseover", function(e) {
                document.body.style.cursor = "pointer";
                hover_jazire(jazire);
                layer.draw();
                e.evt.preventDefault();
                e.cancelBubble = true;
            });
            jazire.elem.on("mouseout", function(e) {
                change_target(layer, "reset_shadow");
                document.body.style.cursor = "grab";
            });
            layer.add(jazire.elem);
        });
}

function init_ways(layer) {
    data.ways.elem = new Konva.Image({
        x: data.back.x,
        y: data.back.y,
        image: data.images[data.ways.src],
        width: data.back.width,
        height: data.back.height,
        listening: false
    });
    layer.add(data.ways.elem);
}

function init_ship(layer) {
    data.ship.elem = new Konva.Image({
        x: data.ship.x * data.back.width,
        y: data.ship.y * data.back.height,
        image: data.images[data.ship.src],
        width: data.ship.width * data.back.width,
        height: data.ship.height * data.back.height,
        shadowColor: "#4a1311",
        shadowBlur: 4,
        shadowOpacity: 4,
        shadowOffset: { x: 2, y: 2 },
        shadowEnabled: true
    });
    let ox = Math.random() * 200 + 500;
    let oy = Math.random() * 200 + 500;
    let or = Math.random() * 200 + 500;
    var anim = new Konva.Animation(function(frame) {
        data.ship.elem.offsetX(Math.sin(frame.time / ox));
        data.ship.elem.offsetY(Math.sin(frame.time / oy));
        data.ship.elem.rotate(Math.sin(frame.time / or) / 10);
    }, layer);

    layer.add(data.ship.elem);
    anim.start();
}

function init_game() {
    data.stage = new Konva.Stage({
        container: "game-container",
        width: data.width,
        height: data.height
    });
    let layer = new Konva.Layer({
        draggable: true
    });

    layer.on("dragend mouseup mouseover", function() {
        document.body.style.cursor = "grab";
    });

    layer.on("dragstart click", function() {
        jazire_info.addClass("hide");
        jazire_info.removeClass("show");
        change_target(layer, null);
    });

    init_backgronud(layer);
    init_jazireha(layer);
    init_ways(layer);
    init_ship(layer);

    data.stage.add(layer);
    layer.draw();
}

let sources = [
    data.back.src,
    data.ways.src,
    data.ganj.src,
    data.ganj_open.src,
    data.seagull.src,
    data.ship.src
];
data.jazireha.forEach(jazire => {
    sources.push(jazire.src);
});

loadImages(sources).then(init_game);
