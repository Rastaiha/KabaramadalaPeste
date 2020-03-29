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
    data.layer2 = new Konva.Layer();

    data.layer.on("dragend mouseup mouseover", function() {
        document.body.style.cursor = "grab";
        data.layer2.x(data.layer.x());
        data.layer2.y(data.layer.y());
    });

    data.layer.on("dragstart click touchend", function() {
        island_info.addClass("hide");
        island_info.removeClass("show");
        change_target(null);
        data.layer2.x(data.layer.x());
        data.layer2.y(data.layer.y());
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
        data.layer2.x(data.layer.x());
        data.layer2.y(data.layer.y());
    });

    data.stage.add(data.layer);
    data.stage.add(data.layer2);
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

let island_info = $(".island-info");

function change_target(target = null) {
    if (target !== "reset_shadow") {
        data.target = target;
    }

    data.islands.forEach(island => {
        if (data.target === island) {
            island.elem.setAttrs({
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
            data.target.neighborhoods.includes(island.id)
        ) {
            island.elem.setAttrs({
                scale: { x: 1, y: 1 },
                shadowColor: "#cccccc",
                shadowEnabled: true,
                shadowBlur: 1,
                shadowOpacity: 1,
                shadowOffset: { x: 1, y: 1 }
            });
        } else {
            island.elem.setAttrs({
                scale: { x: 1, y: 1 },
                shadowEnabled: false
            });
        }
        data.layer.batchDraw();
    });
}

function hover_island(island) {
    if (data.target !== island) {
        island.elem.setAttrs({
            scale: { x: 1.01, y: 1.01 },
            shadowColor: "yellow",
            shadowEnabled: true,
            shadowBlur: 1,
            shadowOpacity: 1,
            shadowOffset: { x: 1, y: 1 }
        });
    }
}

function init_islands() {
    data.islands
        .sort((a, b) => (a.zIndex > b.zIndex ? 1 : -1))
        .forEach(island => {
            island.elem = new Konva.Image({
                x: Math.floor(island.x * data.back.width),
                y: Math.floor(island.y * data.back.height),
                image: data.images[island.src],
                width: Math.floor(island.width * data.back.width),
                height: Math.floor(island.height * data.back.height),
                shadowEnabled: false,
                perfectDrawEnabled: false
            });

            island.elem.on("click tap", function(e) {
                document.body.style.cursor = "pointer";
                if (typeof data.ship === "undefined") {
                    set_start_island(island.id)
                        .then(() => init_ship_data(island.id))
                        .then(init_ship)
                        .catch(default_fail);
                } else if (data.target !== island) {
                    change_target(island);
                    update_and_show_island_info(island);
                }

                if (typeof e !== "undefined") {
                    e.evt.preventDefault();
                    e.cancelBubble = true;
                }
            });

            island.elem.on("dragstart dragmove mouseover", function(e) {
                document.body.style.cursor = "pointer";
                hover_island(island);
                data.layer.batchDraw();
                if (typeof e !== "undefined") {
                    e.evt.preventDefault();
                    e.cancelBubble = true;
                }
            });

            island.elem.on("mouseout", function(e) {
                change_target("reset_shadow");
                document.body.style.cursor = "grab";
            });

            data.layer.add(island.elem);
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
        x: Math.floor(data.ship.x),
        y: Math.floor(data.ship.y),
        image: data.images[data.ship.src],
        width: Math.floor(data.ship.width * data.back.width),
        height: Math.floor(data.ship.height * data.back.height),
        perfectDrawEnabled: false
    });

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

    data.layer2.add(data.ship.elem);

    let start = new Date();

    let ox = Math.random() * 200 + 500;
    let oy = Math.random() * 200 + 500;
    let or = Math.random() * 200 + 100;
    function animate() {
        let delta = new Date() - start;
        data.ship.elem.offsetX(Math.sin(delta / ox));
        data.ship.elem.offsetY(Math.sin(delta / oy));
        data.ship.elem.rotate(Math.sin(delta / or) / 10);
        data.layer2.batchDraw();
        requestAnimationFrame(animate);
    }
    animate();
}

function init_ship_data(island_id) {
    let island = get_island(island_id);
    data.ship = {
        x: island.elem.x() - 15,
        y: island.elem.y() - 15,
        src: "ship.png",
        width: 0.06,
        height: 0.065,
        island_id: island_id
    };
}

function init_other_animation() {
    let start = new Date();
    function animate() {
        let delta = new Date() - start;
        for (const key in data.op) {
            if (data.op.hasOwnProperty(key)) {
                const element = data.op[key];
                if(typeof element.elem !== "undefined"){

                    element.elem.offsetX(Math.sin(delta / element.ox));
                    element.elem.offsetY(Math.sin(delta / element.oy));
                    element.elem.rotate(Math.sin(delta / element.or) / 10);
                }
            }
        }
        data.layer2.batchDraw();
        requestAnimationFrame(animate);
    }
    animate();
}

function init_game() {
    data.stage = new Konva.Stage({
        container: "game-container",
        width: data.width,
        height: data.height
    });

    init_layer();
    init_backgronud();

    get_player_info()
        .then(response => {
            if (response.current_island_id) {
                init_ship_data(response.current_island_id);
                init_ship();
            } else {
                my_alert(
                    "در ابتدای بازی شما باید جزیره‌ای را برای شروع انتخاب کنید.",
                    "انتخاب جزیره اولیه"
                );
            }
        })
        .catch(default_fail);

    init_islands();
    init_ways();

    data.op = {};
    get_other_players();
    init_other_animation();

    if (typeof data.ship !== "undefined") {
        data.ship.elem.moveToTop();
    }

    data.layer.batchDraw();
    data.layer2.batchDraw();
}

let sources = [
    data.back.src,
    data.ways.src,
    data.ganj.src,
    data.ganj_open.src,
    data.seagull.src,
    "ship.png"
];
data.islands.forEach(island => {
    sources.push(island.src);
});

loadImages(sources).then(init_game);
