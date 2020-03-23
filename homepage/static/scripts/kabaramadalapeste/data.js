let data = {
    width: $(window).width(),
    height: $(window).height(),
    back: {
        x: 0,
        y: 0,
        src: "BG.jpg"
    },
    ways: {
        src: "ways.png"
    },
    ganj: {
        x: 0.012,
        y: 0.04,
        src: "ganj.png",
        width: 0.03,
        height: 0.04
    },
    ganj_open: {
        x: 0.012,
        y: 0.03,
        src: "ganj_open.png",
        width: 0.03,
        height: 0.04
    },
    seagull: {
        src: "seagull.png",
        width: 0.05,
        height: 0.05
    },
    ship: {
        x: 0.1,
        y: 0.1,
        src: "ship.png",
        width: 0.05,
        height: 0.055
    },
    players: [
        {
            x: 0.2,
            y: 0.2,
            src: "ship.png",
            width: 0.025,
            height: 0.026
        },
        {
            x: 0.25,
            y: 0.2,
            src: "ship.png",
            width: 0.025,
            height: 0.026
        },
        {
            x: 0.23,
            y: 0.25,
            src: "ship.png",
            width: 0.025,
            height: 0.026
        }
    ],
    jazireha: [
        {
            id: 1,
            x: 0.842,
            y: 0.036,
            width: 0.111,
            height: 0.092,
            src: "1.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 2,
            x: 0.93,
            y: 0.13,
            width: 0.036,
            height: 0.115,
            src: "2.png",
            ganj_closed: false,
            zIndex: 10
        },
        {
            id: 3,
            x: 0.646,
            y: 0.037,
            width: 0.093,
            height: 0.115,
            src: "3.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 4,
            x: 0.755,
            y: 0.102,
            width: 0.109,
            height: 0.181,
            src: "4.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 5,
            x: 0.487,
            y: 0.03,
            width: 0.135,
            height: 0.208,
            src: "5.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 6,
            x: 0.576,
            y: 0.198,
            width: 0.123,
            height: 0.19,
            src: "6.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 7,
            x: 0.787,
            y: 0.315,
            width: 0.084,
            height: 0.21,
            src: "7.png",
            ganj_closed: false,
            zIndex: 10
        },
        {
            id: 8,
            x: 0.871,
            y: 0.239,
            width: 0.072,
            height: 0.17,
            src: "8.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 9,
            x: 0.883,
            y: 0.41,
            width: 0.099,
            height: 0.325,
            src: "9.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 10,
            x: 0.93,
            y: 0.77,
            width: 0.048,
            height: 0.085,
            src: "10.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 11,
            x: 0.807,
            y: 0.551,
            width: 0.12,
            height: 0.176,
            src: "11.png",
            ganj_closed: false,
            zIndex: 11
        },
        {
            id: 12,
            x: 0.785,
            y: 0.801,
            width: 0.084,
            height: 0.15,
            src: "12.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 13,
            x: 0.72,
            y: 0.72,
            width: 0.085,
            height: 0.138,
            src: "13.png",
            ganj_closed: true,
            zIndex: 11
        },
        {
            id: 14,
            x: 0.495,
            y: 0.737,
            width: 0.171,
            height: 0.15,
            src: "14.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 15,
            x: 0.616,
            y: 0.583,
            width: 0.078,
            height: 0.14,
            src: "15.png",
            ganj_closed: false,
            zIndex: 10
        },
        {
            id: 16,
            x: 0.658,
            y: 0.418,
            width: 0.096,
            height: 0.146,
            src: "16.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 17,
            x: 0.296,
            y: 0.015,
            width: 0.18,
            height: 0.115,
            src: "17.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 18,
            x: 0.41,
            y: 0.179,
            width: 0.108,
            height: 0.078,
            src: "18.png",
            ganj_closed: true,
            zIndex: 11
        },
        {
            id: 19,
            x: 0.429,
            y: 0.274,
            width: 0.08,
            height: 0.12,
            src: "19.png",
            ganj_closed: false,
            zIndex: 10
        },
        {
            id: 20,
            x: 0.379,
            y: 0.426,
            width: 0.132,
            height: 0.234,
            src: "20.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 21,
            x: 0.465,
            y: 0.66,
            width: 0.084,
            height: 0.1,
            src: "21.png",
            ganj_closed: true,
            zIndex: 11
        },
        {
            id: 22,
            x: 0.385,
            y: 0.69,
            width: 0.069,
            height: 0.145,
            src: "22.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 23,
            x: 0.336,
            y: 0.831,
            width: 0.228,
            height: 0.155,
            src: "23.png",
            ganj_closed: false,
            zIndex: 10
        },
        {
            id: 24,
            x: 0.195,
            y: 0.845,
            width: 0.132,
            height: 0.125,
            src: "24.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 25,
            x: 0.034,
            y: 0.736,
            width: 0.15,
            height: 0.145,
            src: "25.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 26,
            x: 0.183,
            y: 0.679,
            width: 0.063,
            height: 0.11,
            src: "26.png",
            ganj_closed: true,
            zIndex: 11
        },
        {
            id: 27,
            x: 0.1,
            y: 0.559,
            width: 0.111,
            height: 0.18,
            src: "27.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 28,
            x: 0.03,
            y: 0.41,
            width: 0.078,
            height: 0.19,
            src: "28.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 29,
            x: 0.333,
            y: 0.575,
            width: 0.048,
            height: 0.094,
            src: "29.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 30,
            x: 0.286,
            y: 0.395,
            width: 0.084,
            height: 0.195,
            src: "30.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 31,
            x: 0.257,
            y: 0.101,
            width: 0.102,
            height: 0.155,
            src: "31.png",
            ganj_closed: false,
            zIndex: 10
        },
        {
            id: 32,
            x: 0.018,
            y: 0.027,
            width: 0.078,
            height: 0.165,
            src: "32.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 33,
            x: 0.085,
            y: 0.192,
            width: 0.048,
            height: 0.2,
            src: "33.png",
            ganj_closed: false,
            zIndex: 10
        },
        {
            id: 34,
            x: 0.128,
            y: 0.055,
            width: 0.087,
            height: 0.18,
            src: "34.png",
            ganj_closed: true,
            zIndex: 10
        },
        {
            id: 35,
            x: 0.143,
            y: 0.235,
            width: 0.1,
            height: 0.135,
            src: "35.png",
            ganj_closed: true,
            zIndex: 10
        }
    ]
};

data.back.width = data.width * 1.3;
data.back.height = (data.back.width / 1500) * 900;
if (data.width / 1500 < data.height / 900) {
    data.back.height = data.height * 1.3;
    data.back.width = (data.back.height / 900) * 1500;
}
