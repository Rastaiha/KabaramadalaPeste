var csrftoken = $("[name=csrfmiddlewaretoken]").val();
function csrfSafeMethod(method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function settings() {
    return $.ajax("/game/settings/");
}

function get_player_info() {
    return $.ajax("/game/participant_info/").then(response => {
        if (typeof response === "string") window.location.href = "/";
        return response;
    });
}

function all_players_info() {
    return $.ajax("/game/all_participants_info/");
}

function get_island_info(island_id) {
    return $.ajax("/game/island_info/" + island_id + "/").then(response => {
        response.island_id = island_id;
        return response;
    });
}

function set_start_island(dest_island_id) {
    return $.ajax({
        method: "POST",
        url: "/game/set_start_island/" + dest_island_id + "/"
    });
}

function move_to(dest_island_id) {
    return $.ajax({
        method: "POST",
        url: "/game/move_to/" + dest_island_id + "/"
    });
}

function put_anchor() {
    return $.ajax({
        method: "POST",
        url: "/game/put_anchor/"
    });
}

function open_treasure() {
    return $.ajax({
        method: "POST",
        url: "/game/open_treasure/"
    });
}

function accept_challenge() {
    return $.ajax({
        method: "POST",
        url: "/game/accept_challenge/"
    });
}

function spade() {
    return $.ajax({
        method: "POST",
        url: "/game/spade/"
    });
}

function create_offer() {
    return $.ajax({
        method: "POST",
        url: "/game/create_offer/"
    });
}

function notifications_all_list() {
    return $.ajax("/notifications/api/all_list/");
}

function notifications_unread_list() {
    return $.ajax("/notifications/api/unread_list/");
}

function mark_as_read(slug) {
    return $.ajax("/notifications/mark-as-read/" + slug + "/");
}

function create_offer(form) {
    return $.ajax({
        method: "POST",
        url: "/game/create_offer/",
        data: form.serialize()
    });
}

function get_all_offers(form) {
    return $.ajax("/game/get_all_offers/");
}

function get_my_offers() {
    return $.ajax("/game/get_my_offers/");
}

function delete_offer(pk) {
    return $.ajax({
        method: "POST",
        url: "/game/delete_offer/" + pk + "/"
    });
}

function accept_offer(pk) {
    return $.ajax({
        method: "POST",
        url: "/game/accept_offer/" + pk + "/"
    });
}

function invest(amount) {
    return $.ajax({
        method: "POST",
        url: "/game/invest/",
        data: {
            amount: amount
        }
    });
}
