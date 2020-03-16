let team = [];
var is_inited = false;

function init() {
    if (is_inited) {
        return;
    }
    is_inited = true;
    $.ajax({
        url: "/get_all_members_api/",
        async: false,
        success: function(data) {
            team = data.data;
        },
        error: function(data) {
            console.log(data.responseText);
        }
    });
}

function show_list(team_members, container) {
    init();
    for (let i = 0; i < team_members.length; i++) {
        let description = "";
        if (team_members[i].description) {
            description =
                "<hr/>" + "<small>" + team_members[i].description + "</small>";
        }
        $(container).append(
            '<div class="team-wrapper"><div class="team-member-card"><div><div><img src="' +
                team_members[i].image +
                '" /><div class="team-member-title">' +
                team_members[i].title +
                '</div></div><div class="team-member-details"><div class="team-member-name">' +
                team_members[i].name +
                description +
                "</div></div></div></div></div>"
        );
    }
}

function random_team_list() {
    init();
    function getRandom(arr, n) {
        var result = new Array(n),
            len = arr.length,
            taken = new Array(len);
        while (n--) {
            var x = Math.floor(Math.random() * len);
            result[n] = arr[x in taken ? taken[x] : x];
            taken[x] = --len in taken ? taken[len] : len;
        }
        return result;
    }
    show_list(getRandom(team, Math.min(4, team.length)), ".random-team-list");
}

function filter_list(title, container) {
    init();
    let selected_team = [];
    for (let i = 0; i < team.length; i++) {
        if (team[i].title === title) {
            selected_team.push(team[i]);
        }
    }
    show_list(selected_team, container);
}
