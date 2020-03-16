var Countdown = {
    $el: $(".countdown"),
    countdown_interval: null,
    total_seconds: (new Date(2020, 2, 28, 8) - new Date()) / 1000,
    init: function() {
        this.$ = {
            days: this.$el.find(".bloc-time.days .figure"),
            hours: this.$el.find(".bloc-time.hours .figure"),
            minutes: this.$el.find(".bloc-time.min .figure"),
            seconds: this.$el.find(".bloc-time.sec .figure")
        };
        var so = this;
        $.ajax({
            url: "/get_countdown_api/",
            async: false,
            success: function (data) {
                so.total_seconds = (new Date(data.year, data.month, data.day, data.hour) - Date.now()) / 1000;
            },
            error: function (data) {
                console.log(data.responseText);
            }
        });
        this.values = {};
        let delta = this.total_seconds;
        this.values.days = Math.floor(delta / 86400);
        delta -= this.values.days * 86400;
        this.values.hours = Math.floor(delta / 3600) % 24;
        delta -= this.values.hours * 3600;
        this.values.minutes = Math.floor(delta / 60) % 60;
        delta -= this.values.minutes * 60;
        this.values.seconds = delta;
        this.count();
    },

    count: function() {
        var that = this,
            $day_1 = this.$.days.eq(0),
            $day_2 = this.$.days.eq(1),
            $hour_1 = this.$.hours.eq(0),
            $hour_2 = this.$.hours.eq(1),
            $min_1 = this.$.minutes.eq(0),
            $min_2 = this.$.minutes.eq(1),
            $sec_1 = this.$.seconds.eq(0),
            $sec_2 = this.$.seconds.eq(1);
        this.countdown_interval = setInterval(function() {
            if (that.total_seconds > 0) {
                --that.values.seconds;
                if (that.values.minutes >= 0 && that.values.seconds < 0) {
                    that.values.seconds = 59;
                    --that.values.minutes;
                }
                if (that.values.hours >= 0 && that.values.minutes < 0) {
                    that.values.minutes = 59;
                    --that.values.hours;
                }
                if (that.values.days >= 0 && that.values.hours < 0) {
                    that.values.hours = 23;
                    --that.values.days;
                }

                // Update DOM values
                that.update_ui(that.values.days, $day_1, $day_2);
                that.update_ui(that.values.hours, $hour_1, $hour_2);
                that.update_ui(that.values.minutes, $min_1, $min_2);
                that.update_ui(that.values.seconds, $sec_1, $sec_2);

                --that.total_seconds;
            } else {
                clearInterval(that.countdown_interval);
            }
        }, 1000);
    },

    animateFigure: function($el, value) {
        var that = this,
            $top = $el.find(".top"),
            $bottom = $el.find(".bottom"),
            $back_top = $el.find(".top-back"),
            $back_bottom = $el.find(".bottom-back");
        $back_top.find("span").html(value);
        $back_bottom.find("span").html(value);

        TweenMax.to($top, 0.8, {
            rotationX: "-180deg",
            transformPerspective: 300,
            ease: Quart.easeOut,
            onComplete: function() {
                $top.html(value);

                $bottom.html(value);

                TweenMax.set($top, {
                    rotationX: 0
                });
            }
        });

        TweenMax.to($back_top, 0.8, {
            rotationX: 0,
            transformPerspective: 300,
            ease: Quart.easeOut,
            clearProps: "all"
        });
    },
    persian_number: ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"],
    update_ui: function(value, $el_1, $el_2) {
        var val_1 = this.persian_number[value.toString().charAt(0)],
            val_2 = this.persian_number[value.toString().charAt(1)],
            fig_1_value = $el_1.find(".top").html(),
            fig_2_value = $el_2.find(".top").html();

        if (value >= 10) {
            if (fig_1_value !== val_1) this.animateFigure($el_1, val_1);
            if (fig_2_value !== val_2) this.animateFigure($el_2, val_2);
        } else {
            if (fig_1_value !== "۰") this.animateFigure($el_1, "۰");
            if (fig_2_value !== val_1) this.animateFigure($el_2, val_1);
        }
    }
};
Countdown.init();
