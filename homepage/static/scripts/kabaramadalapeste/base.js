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
$(".right-info-btn").click(function() {
    let elem = this;
    if (
        $(elem)
            .parent()
            .hasClass("player-info")
    ) {
        get_player_info()
            .done(function(response) {
                console.log(response);
                $(".player-info .right-info-details h3").text(
                    response.username
                );
                $(".player-propties").html("");
                for (const key in response.properties) {
                    if (response.properties.hasOwnProperty(key)) {
                        $(".player-propties").append(
                            '<div class="player-proprty"><span><b class="proprty-count">' +
                                response.properties[key] +
                                ' </b>×</span><img src="/static/images/game/coins.png" /></div>'
                        );
                        const proprty_count = response.properties[key];
                    }
                }
                toggle_right_info(elem);
            })
            .fail(function(jqXHR, textStatus) {
                my_alert(textStatus, "خطا");
            });
    } else {
        toggle_right_info(elem);
    }
});
