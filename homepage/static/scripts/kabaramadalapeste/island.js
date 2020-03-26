let data = {
    width: $(window).width(),
    height: $(window).height(),
    back: {
        src: "island_empty.jpg"
    },
    e: {
        ganj: {
            src: "g.png",
            x: 0.21,
            y: 0.764,
            width: 0.13,
            height: 0.175
        },
        bill: {
            src: "bill.png",
            x: 0.43,
            y: 0.56,
            width: 0.1,
            height: 0.22
        },
        eskelet: {
            src: "s.png",
            x: 0.34,
            y: 0.67,
            width: 0.05,
            height: 0.08
        }
    }
};

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

function init_game() {
    data.stage = new Konva.Stage({
        container: "island-container",
        width: data.width,
        height: data.height
    });

    data.layer = new Konva.Layer();

    data.back.elem = new Konva.Image({
        x: Math.floor(data.back.x),
        y: Math.floor(data.back.y),
        image: data.images[data.back.src],
        width: Math.floor(data.back.width),
        height: Math.floor(data.back.height)
    });
    data.layer.add(data.back.elem);
    for (const key in data.e) {
        if (data.e.hasOwnProperty(key)) {
            const element = data.e[key];
            element.elem = new Konva.Image({
                x: Math.floor(element.x * data.back.width + data.back.x),
                y: Math.floor(element.y * data.back.height + data.back.y),
                image: data.images[element.src],
                width: Math.floor(element.width * data.back.width),
                height: Math.floor(element.height * data.back.height),
                shadowColor: "yellow",
                shadowEnabled: true
            });
            element.elem.on("mouseover", function() {
                document.body.style.cursor = "pointer";
                this.setAttrs({
                    shadowBlur: 40,
                    shadowOpacity: 20
                });
                data.layer.batchDraw();
            });
            element.elem.on("mouseout", function() {
                document.body.style.cursor = "default";
                this.setAttrs({
                    shadowBlur: 10,
                    shadowOpacity: 2
                });
                data.layer.batchDraw();
            });
            data.layer.add(element.elem);
        }
    }

    let start = new Date();
    function animate() {
        let delta = new Date() - start;
        for (const key in data.e) {
            if (data.e.hasOwnProperty(key)) {
                const element = data.e[key];
                let num = 6 * Math.sin((delta * 2 * Math.PI) / 500) + 6;
                element.elem.setAttrs({
                    shadowBlur: num,
                    shadowOpacity: 2
                });
            }
        }
        data.layer.batchDraw();
        if (delta < 1500) {
            requestAnimationFrame(animate);
        }
    }
    animate();

    data.stage.add(data.layer);
    data.layer.batchDraw();
}

data.back.width = data.width;
data.back.height = (data.back.width / 1200) * 685;
if (data.width / 1200 < data.height / 685) {
    data.back.height = data.height;
    data.back.width = (data.back.height / 685) * 1200;
}

data.back.x = (data.width - data.back.width) / 3.5;
data.back.y = data.height - data.back.height;

let sources = [data.back.src];
for (const key in data.e) {
    if (data.e.hasOwnProperty(key)) {
        const element = data.e[key];
        sources.push(element.src);
    }
}
loadImages(sources).then(init_game);

$(window).on("resize", function() {
    $("#resize_modal").modal();
});
$("#resize_modal_btn").click(function() {
    location.reload(false);
});
