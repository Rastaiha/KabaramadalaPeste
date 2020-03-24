// Konva.pixelRatio = 1;
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

function init_margin() {
    if (typeof data.layer.margin === "undefined") {
        data.layer.margin = {
            x: 30,
            y: 30
        };
    }
}

function init_layer() {
    data.layer = new Konva.Layer({
        draggable: true
    });

    data.layer.on("dragend mouseup mouseover", function() {
        document.body.style.cursor = "grab";
    });

    data.layer.on("dragstart click touchend", function() {
        jazire_info.addClass("hide");
        jazire_info.removeClass("show");
        change_target(data.layer, null);
    });

    init_margin();

    data.layer.on("dragstart dragmove mousedown", function() {
        document.body.style.cursor = "grabbing";
        data.layer.margin.x = Math.max(
            30,
            Math.min(
                data.layer.margin.x,
                Math.max(
                    data.layer.x(),
                    data.stage.width() - data.back.width - data.layer.x()
                )
            )
        );
        data.layer.margin.y = Math.max(
            30,
            Math.min(
                data.layer.margin.y,
                Math.max(
                    data.layer.y(),
                    data.stage.height() - data.back.height - data.layer.y()
                )
            )
        );
        if (data.layer.x() > data.layer.margin.x) {
            data.layer.x(data.layer.margin.x);
        }
        if (data.layer.y() > data.layer.margin.y) {
            data.layer.y(data.layer.margin.y);
        }
        if (
            data.layer.x() <
            data.stage.width() - data.back.width - data.layer.margin.x
        ) {
            data.layer.x(
                data.stage.width() - data.back.width - data.layer.margin.x
            );
        }
        if (
            data.layer.y() <
            data.stage.height() - data.back.height - data.layer.margin.y
        ) {
            data.layer.y(
                data.stage.height() - data.back.height - data.layer.margin.y
            );
        }
    });

    data.stage.add(data.layer);
}

function init_backgronud() {
    data.back.elem = new Konva.Image({
        x: Math.floor(data.back.x),
        y: Math.floor(data.back.y),
        image: data.images[data.back.src],
        width: Math.floor(data.back.width),
        height: Math.floor(data.back.height),
        perfectDrawEnabled: false
    });
    data.layer.add(data.back.elem);
}

let jazire_info = $(".jazire-info");

function change_target(target = null) {
    if (target !== "reset_shadow") {
        data.target = target;
    }

    data.jazireha.forEach(jazire => {
        if (data.target === jazire) {
            jazire.elem.setAttrs({
                scale: { x: 1.02, y: 1.02 },
                shadowColor: "yellow",
                shadowEnabled: true,
                shadowBlur: 2,
                shadowOpacity: 2,
                shadowOffset: { x: 2, y: 2 }
            });
        } else if (
            data.target &&
            typeof data.target.neighborhoods !== "undefined" &&
            data.target.neighborhoods.includes(jazire.id)
        ) {
            jazire.elem.setAttrs({
                scale: { x: 1, y: 1 },
                shadowColor: "#cccccc",
                shadowEnabled: true,
                shadowBlur: 1,
                shadowOpacity: 1,
                shadowOffset: { x: 1, y: 1 }
            });
        } else {
            jazire.elem.setAttrs({
                scale: { x: 1, y: 1 },
                shadowEnabled: false
            });
        }
        data.layer.batchDraw();
    });
}

function hover_jazire(jazire) {
    if (data.target !== jazire) {
        jazire.elem.setAttrs({
            scale: { x: 1.01, y: 1.01 },
            shadowColor: "yellow",
            shadowEnabled: true,
            shadowBlur: 1,
            shadowOpacity: 1,
            shadowOffset: { x: 1, y: 1 }
        });
    }
}

function init_jazireha() {
    data.jazireha
        .sort((a, b) => (a.zIndex > b.zIndex ? 1 : -1))
        .forEach(jazire => {
            jazire.elem = new Konva.Image({
                x: Math.floor(jazire.x * data.back.width),
                y: Math.floor(jazire.y * data.back.height),
                image: data.images[jazire.src],
                width: Math.floor(jazire.width * data.back.width),
                height: Math.floor(jazire.height * data.back.height),
                shadowEnabled: false,
                perfectDrawEnabled: false
            });

            jazire.elem.on("click tap", function(e) {
                document.body.style.cursor = "pointer";
                if (data.target !== jazire) {
                    change_target(jazire);
                    show_jazire_info(jazire);
                }
                if (typeof e !== "undefined") {
                    e.evt.preventDefault();
                    e.cancelBubble = true;
                }
            });

            jazire.elem.on("dragstart dragmove mouseover", function(e) {
                document.body.style.cursor = "pointer";
                hover_jazire(jazire);
                data.layer.batchDraw();
                if (typeof e !== "undefined") {
                    e.evt.preventDefault();
                    e.cancelBubble = true;
                }
            });

            jazire.elem.on("mouseout", function(e) {
                change_target("reset_shadow");
                document.body.style.cursor = "grab";
            });

            data.layer.add(jazire.elem);
        });
}

function init_ways() {
    data.ways.elem = new Konva.Image({
        x: Math.floor(data.back.x),
        y: Math.floor(data.back.y),
        image: data.images[data.ways.src],
        width: Math.floor(data.back.width),
        height: Math.floor(data.back.height),
        listening: false,
        perfectDrawEnabled: false
    });
    data.layer.add(data.ways.elem);
}

function init_ship() {
    data.ship.elem = new Konva.Image({
        x: Math.floor(data.ship.x * data.back.width),
        y: Math.floor(data.ship.y * data.back.height),
        image: data.images[data.ship.src],
        width: Math.floor(data.ship.width * data.back.width),
        height: Math.floor(data.ship.height * data.back.height),
        perfectDrawEnabled: false
    });
    let ox = Math.random() * 200 + 500;
    let oy = Math.random() * 200 + 500;
    let or = Math.random() * 200 + 100;
    var anim = new Konva.Animation(function(frame) {
        data.ship.elem.offsetX(Math.sin(frame.time / ox));
        data.ship.elem.offsetY(Math.sin(frame.time / oy));
        data.ship.elem.rotate(Math.sin(frame.time / or) / 10);
    }, data.layer);
    data.ship.elem.on("mouseover", function(e) {
        document.body.style.cursor = "pointer";
        if (typeof e !== "undefined") {
            e.evt.preventDefault();
            e.cancelBubble = true;
        }
    });
    data.ship.elem.on("click tap", function(e) {
        document.body.style.cursor = "pointer";
        show_player_info();
        if (typeof e !== "undefined") {
            e.evt.preventDefault();
            e.cancelBubble = true;
        }
    });
    data.layer.add(data.ship.elem);
    anim.start();
}

function init_game() {
    data.stage = new Konva.Stage({
        container: "game-container",
        width: data.width,
        height: data.height
    });

    init_layer();
    init_backgronud();
    init_jazireha();
    init_ways();

    init_ship();
    data.layer.batchDraw();
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
