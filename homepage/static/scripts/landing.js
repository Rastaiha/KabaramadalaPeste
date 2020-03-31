$(".show-stat").click(function() {
    if ($(".stat-img-container").hasClass("show")) {
        $(".stat-img-container").addClass("hide");
        $(".stat-img-container").removeClass("show");
    } else {
        $(".stat-img-container").removeClass("hide");
        $(".stat-img-container").addClass("show");
        $(".navbar-collapse").collapse("hide");
    }
});

$(".close-stat").click(function() {
    $(".stat-img-container").addClass("hide");
    $(".stat-img-container").removeClass("show");
});

$(".download-stat").click(function() {});

$(".share-stat").click(function() {
    text = $(".share-input").val();
    text = text.replace('\n', ' ');
    img_url =
        window.location.protocol +
        "//" +
        window.location.host +
        $(".stat-img").data("back");
    switch ($(this).data("site")) {
        case "telegram":
            url =
                "https://telegram.me/share/url?url=" +
                img_url +
                "&text=" +
                text;
            break;
        case "twitter":
            url =
                "https://twitter.com/intent/tweet?&text=" +
                text +
                " " +
                img_url;
            break;
        case "whatsapp":
            url = "https://api.whatsapp.com/send?text=" + text + " " + img_url;
            break;

        case "linkedin":
            url =
                "https://www.linkedin.com/shareArticle?mini=true&url=" +
                img_url +
                "&title=کابارآمادالاپسته" +
                "&summary=" +
                text;
            break;

        default:
            break;
    }
    window.open(url, "_blank");
});
