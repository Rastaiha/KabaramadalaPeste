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
        x: 0.5,
        y: 0.5,
        src: "ship.png",
        width: 0.06,
        height: 0.065,
        jazire_id: 20
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
            zIndex: 10,
            neighborhoods: [3, 4],
            name: "مخوف"
        },
        {
            id: 2,
            x: 0.93,
            y: 0.13,
            width: 0.036,
            height: 0.115,
            src: "2.png",
            zIndex: 10,
            neighborhoods: [4, 8],
            name: "باحال"
        },
        {
            id: 3,
            x: 0.646,
            y: 0.037,
            width: 0.093,
            height: 0.115,
            src: "3.png",
            zIndex: 10,
            neighborhoods: [1, 4, 16],
            name: "سخت"
        },
        {
            id: 4,
            x: 0.755,
            y: 0.102,
            width: 0.109,
            height: 0.181,
            src: "4.png",
            zIndex: 10,
            neighborhoods: [1, 2, 3, 7],
            name: "سخت"
        },
        {
            id: 5,
            x: 0.487,
            y: 0.03,
            width: 0.135,
            height: 0.208,
            src: "5.png",
            zIndex: 10,
            neighborhoods: [6, 18, 19],
            name: "سخت"
        },
        {
            id: 6,
            x: 0.576,
            y: 0.198,
            width: 0.123,
            height: 0.19,
            src: "6.png",
            zIndex: 10,
            neighborhoods: [5, 16, 19],
            name: "سخت"
        },
        {
            id: 7,
            x: 0.787,
            y: 0.315,
            width: 0.084,
            height: 0.21,
            src: "7.png",
            zIndex: 10,
            neighborhoods: [4, 8, 9],
            name: "باحال"
        },
        {
            id: 8,
            x: 0.871,
            y: 0.239,
            width: 0.072,
            height: 0.17,
            src: "8.png",
            zIndex: 10,
            neighborhoods: [2, 7, 9],
            name: "سخت"
        },
        {
            id: 9,
            x: 0.883,
            y: 0.41,
            width: 0.099,
            height: 0.325,
            src: "9.png",
            zIndex: 10,
            neighborhoods: [7, 8, 10, 11, 12],
            name: "عجیب"
        },
        {
            id: 10,
            x: 0.93,
            y: 0.77,
            width: 0.048,
            height: 0.085,
            src: "10.png",
            zIndex: 10,
            neighborhoods: [9, 11, 12],
            name: "سخت"
        },
        {
            id: 11,
            x: 0.807,
            y: 0.551,
            width: 0.12,
            height: 0.176,
            src: "11.png",
            zIndex: 11,
            neighborhoods: [9, 10, 12, 13],
            name: "سخت"
        },
        {
            id: 12,
            x: 0.785,
            y: 0.801,
            width: 0.084,
            height: 0.15,
            src: "12.png",
            zIndex: 10,
            neighborhoods: [9, 10, 11, 13],
            name: "مخوف"
        },
        {
            id: 13,
            x: 0.72,
            y: 0.72,
            width: 0.085,
            height: 0.138,
            src: "13.png",
            zIndex: 11,
            neighborhoods: [11, 12, 15, 16],
            name: "سخت"
        },
        {
            id: 14,
            x: 0.495,
            y: 0.737,
            width: 0.171,
            height: 0.15,
            src: "14.png",
            zIndex: 10,
            neighborhoods: [15, 21, 22, 23],
            name: "مخوف"
        },
        {
            id: 15,
            x: 0.616,
            y: 0.583,
            width: 0.078,
            height: 0.14,
            src: "15.png",
            zIndex: 10,
            neighborhoods: [13, 14, 16],
            name: "باحال"
        },
        {
            id: 16,
            x: 0.658,
            y: 0.418,
            width: 0.096,
            height: 0.146,
            src: "16.png",
            zIndex: 10,
            neighborhoods: [3, 6, 13, 15, 19],
            name: "عجیب"
        },
        {
            id: 17,
            x: 0.296,
            y: 0.015,
            width: 0.18,
            height: 0.115,
            src: "17.png",
            zIndex: 10,
            neighborhoods: [18, 31],
            name: "مخوف"
        },
        {
            id: 18,
            x: 0.41,
            y: 0.179,
            width: 0.108,
            height: 0.078,
            src: "18.png",
            zIndex: 11,
            neighborhoods: [5, 17, 20, 30, 31],
            name: "سخت"
        },
        {
            id: 19,
            x: 0.429,
            y: 0.274,
            width: 0.08,
            height: 0.12,
            src: "19.png",
            zIndex: 10,
            neighborhoods: [5, 6, 16],
            name: "مخوف"
        },
        {
            id: 20,
            x: 0.379,
            y: 0.426,
            width: 0.132,
            height: 0.234,
            src: "20.png",
            zIndex: 10,
            neighborhoods: [18, 21, 29, 30, 31],
            name: "سخت"
        },
        {
            id: 21,
            x: 0.465,
            y: 0.66,
            width: 0.084,
            height: 0.1,
            src: "21.png",
            zIndex: 11,
            neighborhoods: [14, 20, 22, 23],
            name: "سخت"
        },
        {
            id: 22,
            x: 0.385,
            y: 0.69,
            width: 0.069,
            height: 0.145,
            src: "22.png",
            zIndex: 10,
            neighborhoods: [14, 21, 23, 29],
            name: "مخوف"
        },
        {
            id: 23,
            x: 0.336,
            y: 0.831,
            width: 0.228,
            height: 0.155,
            src: "23.png",
            zIndex: 10,
            neighborhoods: [14, 21, 22, 24],
            name: "باحال"
        },
        {
            id: 24,
            x: 0.195,
            y: 0.845,
            width: 0.132,
            height: 0.125,
            src: "24.png",
            zIndex: 10,
            neighborhoods: [23, 25, 26],
            name: "سخت"
        },
        {
            id: 25,
            x: 0.034,
            y: 0.736,
            width: 0.15,
            height: 0.145,
            src: "25.png",
            zIndex: 10,
            neighborhoods: [24, 26],
            name: "سخت"
        },
        {
            id: 26,
            x: 0.183,
            y: 0.679,
            width: 0.063,
            height: 0.11,
            src: "26.png",
            zIndex: 11,
            neighborhoods: [24, 25, 27, 30],
            name: "عجیب"
        },
        {
            id: 27,
            x: 0.1,
            y: 0.559,
            width: 0.111,
            height: 0.18,
            src: "27.png",
            zIndex: 10,
            neighborhoods: [26, 28, 30],
            name: "مخوف"
        },
        {
            id: 28,
            x: 0.03,
            y: 0.41,
            width: 0.078,
            height: 0.19,
            src: "28.png",
            zIndex: 10,
            neighborhoods: [27, 35],
            name: "باحال"
        },
        {
            id: 29,
            x: 0.333,
            y: 0.575,
            width: 0.048,
            height: 0.094,
            src: "29.png",
            zIndex: 10,
            neighborhoods: [20, 22, 30],
            name: "باحال"
        },
        {
            id: 30,
            x: 0.286,
            y: 0.395,
            width: 0.084,
            height: 0.195,
            src: "30.png",
            zIndex: 10,
            neighborhoods: [18, 20, 26, 27, 29, 31],
            name: "سخت"
        },
        {
            id: 31,
            x: 0.257,
            y: 0.101,
            width: 0.102,
            height: 0.155,
            src: "31.png",
            zIndex: 10,
            neighborhoods: [17, 18, 30, 34],
            name: "عجیب"
        },
        {
            id: 32,
            x: 0.018,
            y: 0.027,
            width: 0.078,
            height: 0.165,
            src: "32.png",
            zIndex: 10,
            neighborhoods: [33, 34, 35],
            name: "سخت"
        },
        {
            id: 33,
            x: 0.085,
            y: 0.192,
            width: 0.048,
            height: 0.2,
            src: "33.png",
            zIndex: 10,
            neighborhoods: [32, 35],
            name: "عجیب"
        },
        {
            id: 34,
            x: 0.128,
            y: 0.055,
            width: 0.087,
            height: 0.18,
            src: "34.png",
            zIndex: 10,
            neighborhoods: [31, 32, 35],
            name: "مخوف"
        },
        {
            id: 35,
            x: 0.143,
            y: 0.235,
            width: 0.1,
            height: 0.135,
            src: "35.png",
            zIndex: 10,
            neighborhoods: [28, 32, 33, 34],
            name: "عجیب"
        }
    ]
};

data.back.width = data.width * 1.3;
data.back.height = (data.back.width / 1500) * 900;
if (data.width / 1500 < data.height / 900) {
    data.back.height = data.height * 1.3;
    data.back.width = (data.back.height / 900) * 1500;
}
