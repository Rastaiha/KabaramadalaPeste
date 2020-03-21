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
        if (layer.x() > 100) {
            layer.x(100);
        }
        if (layer.y() > 100) {
            layer.y(100);
        }
        if (layer.x() < data.stage.width() - data.back.elem.width() - 100) {
            layer.x(data.stage.width() - data.back.elem.width() - 100);
        }
        if (layer.y() < data.stage.height() - data.back.elem.height() - 100) {
            layer.y(data.stage.height() - data.back.elem.height() - 100);
        }
    });

    layer.on("dragstart click", function() {
        jazire_info.addClass("hide");
        jazire_info.removeClass("show");
    });
    layer.add(data.back.elem);
}

let jazire_info = $(".jazire-info");

function init_jazireha(layer) {
    data.jazireha.forEach(jazire => {
        jazire.elem = new Konva.Image({
            x: jazire.x * data.back.width,
            y: jazire.y * data.back.height,
            image: data.images[jazire.src],
            width: jazire.width * data.back.width,
            height: jazire.height * data.back.height,
            shadowColor: "black",
            shadowBlur: 2,
            shadowOpacity: 2,
            shadowOffset: { x: 2, y: 2 },
            shadowEnabled: false
        });
        jazire.elem.on("click touchend", function(e) {
            document.body.style.cursor = "pointer";
            jazire_info.addClass("hide");
            jazire_info.removeClass("show");
            setTimeout(() => {
                let x = jazire.elem.x() + layer.x() + jazire.elem.width() + 10,
                    y = jazire.elem.y() + layer.y() + jazire.elem.height() / 2;
                if (data.stage.width() / 2 < jazire.elem.x() + layer.x()) {
                    x -= 150 + jazire.elem.width() / 2 + 10;
                }
                if (data.stage.height() / 2 < jazire.elem.y() + layer.y()) {
                    y -= jazire_info.height() / 2 + jazire.elem.height() / 2;
                }
                x = Math.max(10, Math.min(x, data.stage.width() - 150 - 30));
                y = Math.max(
                    10,
                    Math.min(y, data.stage.height() - jazire_info.height() - 30)
                );
                jazire_info.css("left", x + "px");
                jazire_info.css("top", y + "px");

                jazire_info.removeClass("hide");
                jazire_info.addClass("show");
            }, 100);

            e.evt.preventDefault();
            e.cancelBubble = true;
        });
        jazire.elem.on("dragstart dragmove mouseover", function(e) {
            document.body.style.cursor = "pointer";
            jazire.elem.scale({ x: 1.01, y: 1.01 });
            jazire.elem.shadowEnabled(true);
            layer.draw();
            e.evt.preventDefault();
            e.cancelBubble = true;
        });
        jazire.elem.on("mouseout", function(e) {
            jazire.elem.scale({ x: 1, y: 1 });
            jazire.elem.shadowEnabled(false);
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
        data.jazireha.forEach(jazire => {
            jazire.elem.scale({ x: 1, y: 1 });
            jazire.elem.shadowEnabled(false);
            layer.draw();
        });
    });

    init_backgronud(layer);
    init_jazireha(layer);
    init_ways(layer);

    data.stage.add(layer);
    layer.draw();
}

let sources = [data.back.src, data.ways.src];
data.jazireha.forEach(jazire => {
    sources.push(jazire.src);
});

loadImages(sources).then(init_game);
