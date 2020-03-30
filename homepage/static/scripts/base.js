$('a[href^="#"]').click(function() {
    if ($(this).attr("href") !== "#") {
        $("html, body").animate(
            {
                scrollTop: $($(this).attr("href")).offset().top
            },
            500
        );
    }
});
