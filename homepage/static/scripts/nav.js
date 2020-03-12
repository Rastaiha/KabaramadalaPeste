$(window).scroll(function(event) {
    let scroll = $(window).scrollTop();
    if (scroll > 10) {
        $(".my-nav").addClass("active-nav");
    } else {
        $(".my-nav").removeClass("active-nav");
    }
});
