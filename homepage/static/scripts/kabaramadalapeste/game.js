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
        if (layer.x() > 0) {
            layer.x(0);
        }
        if (layer.y() > 0) {
            layer.y(0);
        }
        if (layer.x() < data.stage.width() - data.back.elem.width()) {
            layer.x(data.stage.width() - data.back.elem.width());
        }
        if (layer.y() < data.stage.height() - data.back.elem.height()) {
            layer.y(data.stage.height() - data.back.elem.height());
        }
    });
    layer.add(data.back.elem);
}

function init_jazireha(layer) {
    data.jazireha.forEach(jazire => {
        jazire.elem = new Konva.Image({
            x: jazire.x,
            y: jazire.y,
            image: data.images[jazire.src],
            width: jazire.width,
            height: jazire.height
        });
        jazire.elem.on(
            "dragstart dragmove mousedown mouseup mouseover",
            function(e) {
                document.body.style.cursor = "pointer";
                console.log(jazire.elem.x(), jazire.elem.y(), jazire.src);
                e.evt.preventDefault();
                e.cancelBubble = true;
            }
        );
        jazire.elem.on("mouseout", function(e) {
            document.body.style.cursor = "grab";
        });
        layer.add(jazire.elem);
    });
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

    init_backgronud(layer);
    init_jazireha(layer);

    data.stage.add(layer);
    layer.draw();
}

let sources = [data.back.src];
data.jazireha.forEach(jazire => {
    sources.push(jazire.src);
});

loadImages(sources).then(init_game);
