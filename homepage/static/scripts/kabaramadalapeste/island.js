let data = {
    width: $(window).width(),
    height: $(window).height(),
    back: {
        src: "island_empty.jpg"
    },
    e: {
        ganj: {
            src: "gc.png",
            x: 0.2,
            y: 0.76,
            width: 0.135,
            height: 0.22
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

function get_keys_string(treasure_keys) {
    let keys = "";
    let is_first = true;
    for (const key in data.treasure_keys) {
        if (data.treasure_keys.hasOwnProperty(key)) {
            if (data.treasure_keys[key]) {
                if (!is_first) {
                    keys += "، ";
                }
                keys +=
                    data.treasure_keys[key] +
                    " عدد کلید نوع " +
                    key.replace("K", "");
                is_first = false;
            }
        }
    }
    keys = keys.replace(/،([^،]*)$/, " و" + "$1");
    return keys;
}

function set_click_listener(key, elem) {
    switch (key) {
        case "ganj":
            elem.on("click tap", function() {
                if (!data.did_open_treasure) {
                    let title = "باز کردن گنج";
                    // let keys = get_keys_string(data.treasure_keys);
                    let keys = data.treasure_keys_persian;
                    let question =
                        "برای باز کردن این گنج باید " +
                        keys +
                        " مصرف کنی." +
                        " می‌خوای این کارو بکنی؟";
                    my_prompt(question, title, {
                        kind: "ganj"
                    });
                    $("#prompt_modal").modal("show");
                } else {
                    my_alert("این گنج رو قبلا باز کردی.", "گنج");
                }
            });
            break;
        case "bill":
            elem.on("click tap", function() {
                if (!data.did_spade) {
                    settings()
                        .then(response => {
                            my_prompt(
                                "برای بیل‌زدن باید " +
                                    response.island_spade_cost +
                                    " زیتون بدی. می‌خوای این کارو بکنی؟",
                                "بیل‌زدن",
                                {
                                    kind: "bill"
                                }
                            );
                            $("#prompt_modal").modal("show");
                        })
                        .catch(default_fail);
                } else {
                    my_alert("قبلاً اینجا رو بیل زدی!", "بیل‌زدن");
                }
            });
            break;
        case "eskelet":
            elem.on("click tap", function() {
                switch (data.submit_status) {
                    case "No":
                        if (!data.did_accept_challenge) {
                            my_prompt("آماده‌ای برای چالش؟", "چالش", {
                                kind: "challenge"
                            });
                        } else {
                            my_prompt("بازگشت به چالش.", "چالش", {
                                kind: "back_to_challenge"
                            });
                        }
                        $("#prompt_modal").modal("show");
                        break;
                    case "Pending":
                        my_alert("در حال تصحیح", "چالش");
                        break;
                    case "Correct":
                        my_alert("آفرین چالش رو درست حل کردی.", "چالش");
                        break;
                    case "Wrong":
                        my_alert("جوابت غلط بوده!", "چالش");
                        break;
                }
            });
            break;
    }
}

$("#prompt_modal_btn").click(function() {
    if ($(this).data("kind")) {
        switch ($(this).data("kind")) {
            case "ganj":
                open_treasure()
                    .then(response => {
                        data.did_open_treasure = true;
                        change_image(data.e.ganj.elem, "go1.png");
                        setTimeout(function() {
                            // let keys = get_keys_string(response.treasure_rewards);
                            let keys = response.treasure_rewards_persian;
                            my_alert(
                                "شما " + keys + " دریافت کردید.",
                                "باز کردن گنج"
                            );
                        }, 1000);
                    })
                    .catch(default_fail);
                break;
            case "bill":
                spade()
                    .then(response => {
                        if (response.found) {
                            my_alert(
                                "پسته رو پیدا کردی!!! تبریک می‌گم.",
                                "پسته"
                            );
                        } else {
                            my_alert("متاسفانه اینجا خالیه.", "پسته");
                        }
                        data.did_spade = true;
                    })
                    .catch(default_fail);
                break;
            case "challenge":
                accept_challenge()
                    .then(() => {
                        window.location.href = "/game/challenge/";
                    })
                    .catch(default_fail);
                break;
            case "back_to_challenge":
                window.location.href = "/game/challenge/";
                break;

            default:
                break;
        }
        $("#prompt_modal").modal("hide");
    }
});

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
            set_click_listener(key, element.elem);
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

function change_image(elem, src) {
    elem.image(data.images[src]);
    data.layer.batchDraw();
}

get_player_info()
    .then(response => {
        if (!response.currently_anchored) {
            window.location.href = "/game/";
        }
        data.island_id = response.current_island_id;
    })
    .then(() => get_island_info(data.island_id))
    .then(response => {
        data.treasure_keys = response.treasure_keys;
        data.treasure_keys_persian = response.treasure_keys_persian;
        data.did_open_treasure = response.did_open_treasure;
        data.is_spade_available = response.is_spade_available;
        if (data.did_open_treasure) {
            data.e.ganj.src = "go2.png";
        }
        if (!data.is_spade_available) {
            data.e.bill.width = 0;
            data.e.bill.height = 0;
        }
        data.did_accept_challenge = response.did_accept_challenge;
        data.did_spade = response.did_spade;
        data.submit_status = response.submit_status;
    })
    .then(() => {
        data.back.width = data.width;
        data.back.height = (data.back.width / 1200) * 685;
        if (data.width / 1200 < data.height / 685) {
            data.back.height = data.height;
            data.back.width = (data.back.height / 685) * 1200;
        }

        data.back.x = (data.width - data.back.width) / 3.5;
        data.back.y = data.height - data.back.height;

        let sources = [data.back.src, "go1.png", "go2.png", "gc.png"];
        for (const key in data.e) {
            if (data.e.hasOwnProperty(key)) {
                const element = data.e[key];
                sources.push(element.src);
            }
        }
        loadImages(sources).then(init_game);
    })
    .catch(default_fail);

$(window).on("resize", function() {
    if (!isMobile) {
        $("#resize_modal").modal();
    }
});
$("#resize_modal_btn").click(function() {
    location.reload(false);
});
