function toggle_right_info(elem) {
    if (
        $(elem)
            .parent()
            .hasClass("show-details")
    ) {
        $(".right-info").removeClass("show-details");
    } else {
        $(".right-info").removeClass("show-details");
        $(elem)
            .parent()
            .addClass("show-details");
    }
}
player_property_img = {
    SK: "coins.png",
    K1: "key1.png",
    K2: "key2.png",
    K3: "key3.png"
};

$(".right-info-btn").click(function() {
    let elem = this;
    if (
        $(elem)
            .parent()
            .hasClass("player-info")
    ) {
        get_player_info()
            .done(function(response) {
                $(".player-info .right-info-details h3").text(
                    response.username
                );
                $(".player-propties").html("");
                for (const key in response.properties) {
                    if (response.properties.hasOwnProperty(key)) {
                        $(".player-propties").append(
                            '<div class="player-proprty"><span><b class="proprty-count">' +
                                response.properties[key] +
                                ' </b>×</span><img src="/static/images/game/' +
                                player_property_img[key] +
                                '" /></div>'
                        );
                        const proprty_count = response.properties[key];
                    }
                }
                toggle_right_info(elem);
            })
            .fail(function(jqXHR, textStatus) {
                let err_message = textStatus;
                if (typeof jqXHR.responseJSON !== "undefined") {
                    err_message = jqXHR.responseJSON.message || textStatus;
                }
                my_alert(err_message, "خطا");
            });
    } else {
        toggle_right_info(elem);
    }
});
