let data = {
    width: window.innerWidth,
    height: window.innerHeight,
    back: {
        x: 0,
        y: 0,
        src: "BG.jpg"
    },
    jazireha: [
        {
            id: 1,
            x: 1402,
            y: 36,
            width: 186,
            height: 92,
            src: "1.png"
        },
        {
            id: 2,
            x: 1536,
            y: 130,
            width: 60,
            height: 115,
            src: "2.png"
        },
        {
            id: 3,
            x: 1075,
            y: 37,
            width: 155,
            height: 115,
            src: "3.png"
        },
        {
            id: 4,
            x: 1257,
            y: 102,
            width: 183,
            height: 181,
            src: "4.png"
        },
        {
            id: 5,
            x: 812,
            y: 30,
            width: 225,
            height: 208,
            src: "5.png"
        },
        {
            id: 6,
            x: 960,
            y: 198,
            width: 205,
            height: 190,
            src: "6.png"
        },
        {
            id: 7,
            x: 1311,
            y: 315,
            width: 140,
            height: 210,
            src: "7.png"
        },
        {
            id: 8,
            x: 1450,
            y: 239,
            width: 120,
            height: 170,
            src: "8.png"
        },
        {
            id: 9,
            x: 1470,
            y: 400,
            width: 165,
            height: 325,
            src: "9.png"
        },
        {
            id: 10,
            x: 1538,
            y: 753,
            width: 80,
            height: 85,
            src: "10.png"
        },
        {
            id: 11,
            x: 1343,
            y: 551,
            width: 200,
            height: 176,
            src: "11.png"
        },
        {
            id: 12,
            x: 1297,
            y: 800,
            width: 140,
            height: 150,
            src: "12.png"
        },
        {
            id: 13,
            x: 1205,
            y: 726,
            width: 143,
            height: 138,
            src: "13.png"
        },
        {
            id: 14,
            x: 825,
            y: 736,
            width: 285,
            height: 150,
            src: "14.png"
        },
        {
            id: 15,
            x: 1026,
            y: 583,
            width: 130,
            height: 140,
            src: "15.png"
        },
        {
            id: 16,
            x: 1096,
            y: 418,
            width: 160,
            height: 146,
            src: "16.png"
        },
        {
            id: 17,
            x: 493,
            y: 15,
            width: 300,
            height: 115,
            src: "17.png"
        },
        {
            id: 18,
            x: 683,
            y: 179,
            width: 180,
            height: 78,
            src: "18.png"
        },
        {
            id: 19,
            x: 715,
            y: 274,
            width: 134,
            height: 120,
            src: "19.png"
        },
        {
            id: 20,
            x: 632,
            y: 426,
            width: 220,
            height: 234,
            src: "20.png"
        },
        {
            id: 21,
            x: 756,
            y: 661,
            width: 140,
            height: 100,
            src: "21.png"
        },
        {
            id: 22,
            x: 640,
            y: 678,
            width: 115,
            height: 145,
            src: "22.png"
        },
        {
            id: 23,
            x: 560,
            y: 830,
            width: 380,
            height: 155,
            src: "23.png"
        },
        {
            id: 24,
            x: 326,
            y: 851,
            width: 220,
            height: 125,
            src: "24.png"
        },
        {
            id: 25,
            x: 57,
            y: 735,
            width: 250,
            height: 145,
            src: "25.png"
        },
        {
            id: 26,
            x: 305,
            y: 678,
            width: 105,
            height: 110,
            src: "26.png"
        },
        {
            id: 27,
            x: 168,
            y: 559,
            width: 185,
            height: 180,
            src: "27.png"
        },
        {
            id: 28,
            x: 38,
            y: 409,
            width: 130,
            height: 190,
            src: "28.png"
        },
        {
            id: 29,
            x: 560,
            y: 566,
            width: 80,
            height: 94,
            src: "29.png"
        },
        {
            id: 30,
            x: 477,
            y: 398,
            width: 140,
            height: 195,
            src: "30.png"
        },
        {
            id: 31,
            x: 429,
            y: 101,
            width: 170,
            height: 155,
            src: "31.png"
        },
        {
            id: 32,
            x: 31,
            y: 27,
            width: 130,
            height: 165,
            src: "32.png"
        },
        {
            id: 33,
            x: 143,
            y: 192,
            width: 80,
            height: 200,
            src: "33.png"
        },
        {
            id: 34,
            x: 214,
            y: 62,
            width: 145,
            height: 180,
            src: "34.png"
        },
        {
            id: 35,
            x: 239,
            y: 235,
            width: 168,
            height: 135,
            src: "35.png"
        }
    ]
};

data.back.width = data.width * 1.3;
data.back.height = (data.back.width / 1500) * 900;
if (data.width / 1500 < data.height / 900) {
    data.back.height = data.height * 1.3;
    data.back.width = (data.back.height / 900) * 1500;
}
