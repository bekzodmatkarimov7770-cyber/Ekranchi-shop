// ==========================================
// 1. REKLAMALAR VA YANGILIKLAR BANERI
// ==========================================
const bannersData = [
  {
    badge: "YANGI PARTIYA",
    title: "🔥 Barcha turdagi Displeylar Omborda!",
    desc: "Samsung, iPhone, Redmi, Tecno, Infinix, Oppo, Vivo, Honor, Huawei va Xiaomi ekranlari.",
    bg: "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)"
  },
  {
    badge: "OPTOM NARX",
    title: "⚡️ 50+ ta displeyga maxsus ulgurji narx!",
    desc: "Savatga jami 50 ta ekran to'plang va eng arzon birinchi qo'l narxda xarid qiling.",
    bg: "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)"
  },
  {
    badge: "KAFOLAT",
    title: "🛡 Barcha displeylarga 2 OY kafolat!",
    desc: "Zavod braki bo'lsa video/rasm orqali darhol yangisiga almashtiramiz yoki pulni qaytaramiz.",
    bg: "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
  }
];

// ==========================================
// 2. TOZALANGAN VA GURUHLANGAN MODELLAR BAZASI (456 TA MODEL)
// ==========================================
const productsData = [
  {
    "brand": "Samsung",
    "name": "A02S / A03S / A03 / A035 / A025 / A04E / A042",
    "type": "IPS LCD",
    "wholesale": 57000,
    "retail": 77000,
    "stock": 3818,
    "id": 1
  },
  {
    "brand": "Samsung",
    "name": "A10 2019 / A105 / M10 / M105",
    "type": "IPS LCD",
    "wholesale": 57000,
    "retail": 77000,
    "stock": 1519,
    "id": 2
  },
  {
    "brand": "Redmi",
    "name": "POCO M3 / 9T",
    "type": "Incell HD+",
    "wholesale": 62000,
    "retail": 84000,
    "stock": 1461,
    "id": 3
  },
  {
    "brand": "Redmi",
    "name": "13C 4G / 13C 5G / POCO C65 / 13R / POCO M6 5G",
    "type": "Incell HD+",
    "wholesale": 63000,
    "retail": 86000,
    "stock": 1350,
    "id": 4
  },
  {
    "brand": "Redmi",
    "name": "NOTE8 PRO",
    "type": "Incell HD+",
    "wholesale": 64000,
    "retail": 87000,
    "stock": 1341,
    "id": 5
  },
  {
    "brand": "Samsung",
    "name": "A135F / A13 4G / A13 LITE / A135 / A137 / F13 / M13",
    "type": "IPS LCD",
    "wholesale": 59000,
    "retail": 80000,
    "stock": 1332,
    "id": 6
  },
  {
    "brand": "Samsung",
    "name": "A10S 2020 / A107",
    "type": "IPS LCD",
    "wholesale": 57000,
    "retail": 77000,
    "stock": 1205,
    "id": 7
  },
  {
    "brand": "Vivo",
    "name": "Y21T / Y16 / y21 / Y15A / Y15S / Y21A / Y21e / Y21G / Y21S / Y33E / Y31S / Y32 / Y01 / Y02S",
    "type": "Incell HD+",
    "wholesale": 57000,
    "retail": 77000,
    "stock": 1194,
    "id": 8
  },
  {
    "brand": "Redmi",
    "name": "11A / POCO C55 / A11 / 12C",
    "type": "Incell HD+",
    "wholesale": 62000,
    "retail": 84000,
    "stock": 1102,
    "id": 9
  },
  {
    "brand": "Redmi",
    "name": "9 PRIME / POCO M2",
    "type": "Incell HD+",
    "wholesale": 62000,
    "retail": 84000,
    "stock": 1075,
    "id": 10
  },
  {
    "brand": "Samsung",
    "name": "A20S 2020 / A207",
    "type": "IPS LCD",
    "wholesale": 59000,
    "retail": 80000,
    "stock": 933,
    "id": 11
  },
  {
    "brand": "Redmi",
    "name": "10X / NOTE 9",
    "type": "Incell HD+",
    "wholesale": 66000,
    "retail": 90000,
    "stock": 911,
    "id": 12
  },
  {
    "brand": "Samsung",
    "name": "J4+ / J6+ / J415 / J610 / J410",
    "type": "IPS LCD",
    "wholesale": 57000,
    "retail": 77000,
    "stock": 765,
    "id": 13
  },
  {
    "brand": "Redmi",
    "name": "A1 / A1+ / A2 / A2+",
    "type": "Incell HD+",
    "wholesale": 57000,
    "retail": 77000,
    "stock": 747,
    "id": 14
  },
  {
    "brand": "Samsung",
    "name": "A13 5G / A04S / A136U / A047 / A04CORE",
    "type": "IPS LCD",
    "wholesale": 58000,
    "retail": 79000,
    "stock": 701,
    "id": 15
  },
  {
    "brand": "Samsung",
    "name": "A01CORE / A013 / A3CORE",
    "type": "IPS LCD",
    "wholesale": 60000,
    "retail": 81000,
    "stock": 697,
    "id": 16
  },
  {
    "brand": "Redmi",
    "name": "10 4G / 10-2022 / 10 prime / 10prime 2022",
    "type": "Incell HD+",
    "wholesale": 68000,
    "retail": 92000,
    "stock": 683,
    "id": 17
  },
  {
    "brand": "Redmi",
    "name": "A5 4G / A5 5G / A5 New / Poco C71",
    "type": "Incell HD+",
    "wholesale": 66000,
    "retail": 90000,
    "stock": 628,
    "id": 18
  },
  {
    "brand": "Tecno & Infinix",
    "name": "BE8 / HOT12 / Hot20i / POP6 Pro / TECNO SPARK8C / SPARK 8C / SPARK9 / SPARK 9T / SMART 6HD / Hot 12i / HOT12 PRO",
    "type": "IPS LCD",
    "wholesale": 59000,
    "retail": 80000,
    "stock": 627,
    "id": 19
  },
  {
    "brand": "Redmi",
    "name": "15C 4G",
    "type": "Incell HD+",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 627,
    "id": 20
  },
  {
    "brand": "Samsung",
    "name": "A15 / M15 / M156",
    "type": "IPS LCD",
    "wholesale": 66000,
    "retail": 90000,
    "stock": 608,
    "id": 21
  },
  {
    "brand": "Redmi",
    "name": "A3 / A3X / POCO C61(yin du)",
    "type": "Incell HD+",
    "wholesale": 62000,
    "retail": 84000,
    "stock": 574,
    "id": 22
  },
  {
    "brand": "Tecno & Infinix",
    "name": "Hot11 / Spark8P / Spark8t / S18pro / S662L / vision5plus / S662LC / SPARK9PRO",
    "type": "IPS LCD",
    "wholesale": 63000,
    "retail": 86000,
    "stock": 551,
    "id": 23
  },
  {
    "brand": "Samsung",
    "name": "A04 / A045",
    "type": "IPS LCD",
    "wholesale": 60000,
    "retail": 81000,
    "stock": 535,
    "id": 24
  },
  {
    "brand": "Redmi",
    "name": "NOTE10 5G / Note11SE / Note10T 5G / POCO M3 PRO",
    "type": "Incell HD+",
    "wholesale": 68000,
    "retail": 92000,
    "stock": 519,
    "id": 25
  },
  {
    "brand": "Samsung",
    "name": "A06 4G / A065",
    "type": "IPS LCD",
    "wholesale": 63000,
    "retail": 86000,
    "stock": 513,
    "id": 26
  },
  {
    "brand": "Tecno & Infinix",
    "name": "BD4 / SMART6 / BD4A / BD4I / BD4J / BD4H / SPARK GO2022 / POP5LTE / POP5PRO / BD4T",
    "type": "IPS LCD",
    "wholesale": 58000,
    "retail": 79000,
    "stock": 487,
    "id": 27
  },
  {
    "brand": "Samsung",
    "name": "A07 4G",
    "type": "IPS LCD",
    "wholesale": 66000,
    "retail": 90000,
    "stock": 482,
    "id": 28
  },
  {
    "brand": "Redmi",
    "name": "POCO C40 / 10 POWER / 10INDIA / 10C",
    "type": "Incell HD+",
    "wholesale": 62000,
    "retail": 84000,
    "stock": 481,
    "id": 29
  },
  {
    "brand": "Tecno & Infinix",
    "name": "HOT12 / HOT12PLAY / HOT12PLAYNFC / NOTE12I / LG7N / POVA4 / HOT20PLAY / HOT20 / LG6 / LG6N / POVANEO2 / LH6N / POVANEO3 / HOT30PLAY / 6835",
    "type": "IPS LCD",
    "wholesale": 66000,
    "retail": 90000,
    "stock": 478,
    "id": 30
  },
  {
    "brand": "Tecno & Infinix",
    "name": "S16 / Smart5 / SparkGo 2020 / Hot10lite / Vision1pro / Vision1plus",
    "type": "IPS LCD",
    "wholesale": 57000,
    "retail": 77000,
    "stock": 469,
    "id": 31
  },
  {
    "brand": "Xiaomi",
    "name": "MI 11T / MI11T PRO",
    "type": "Incell HD+",
    "wholesale": 92000,
    "retail": 125000,
    "stock": 429,
    "id": 32
  },
  {
    "brand": "Realme",
    "name": "A11X / A5 2020 / narzo 20A / A9 2020 / A31 2020 / realmeC3 / Realme5 / Realme5S / narzo10A / A8 2020 / Realme6 / Realme6i / Realme7",
    "type": "Incell HD+",
    "wholesale": 57000,
    "retail": 77000,
    "stock": 426,
    "id": 33
  },
  {
    "brand": "Redmi",
    "name": "12R / Note 13R / 12 / 13 5G / 13 / POCO M6 PRO 5G / 12 5G",
    "type": "Incell HD+",
    "wholesale": 66000,
    "retail": 90000,
    "stock": 423,
    "id": 34
  },
  {
    "brand": "Samsung",
    "name": "A01F 2020 / A015",
    "type": "IPS LCD",
    "wholesale": 59000,
    "retail": 80000,
    "stock": 413,
    "id": 35
  },
  {
    "brand": "Redmi",
    "name": "NOTE 8",
    "type": "Incell HD+",
    "wholesale": 65000,
    "retail": 88000,
    "stock": 409,
    "id": 36
  },
  {
    "brand": "Tecno & Infinix",
    "name": "HOT50 / SPARK30 / SPARK30 4G / HOT50 4G",
    "type": "IPS LCD",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 384,
    "id": 37
  },
  {
    "brand": "Xiaomi",
    "name": "MI 9T / MI9T PRO",
    "type": "Incell HD+",
    "wholesale": 74000,
    "retail": 100000,
    "stock": 373,
    "id": 38
  },
  {
    "brand": "Redmi",
    "name": "14C 4G / 14C 5G / Poco C75",
    "type": "Incell HD+",
    "wholesale": 63000,
    "retail": 86000,
    "stock": 366,
    "id": 39
  },
  {
    "brand": "Samsung",
    "name": "A2Core / A260",
    "type": "IPS LCD",
    "wholesale": 53000,
    "retail": 72000,
    "stock": 358,
    "id": 40
  },
  {
    "brand": "Tecno & Infinix",
    "name": "S17 / A58 / A58PRO 4G / A49 / A661 / A661L / S661W / SMART6+ / SPARK8",
    "type": "IPS LCD",
    "wholesale": 59000,
    "retail": 80000,
    "stock": 353,
    "id": 41
  },
  {
    "brand": "Samsung",
    "name": "A05 / A055F / M05",
    "type": "IPS LCD",
    "wholesale": 61000,
    "retail": 83000,
    "stock": 346,
    "id": 42
  },
  {
    "brand": "Samsung",
    "name": "A05S / A057",
    "type": "IPS LCD",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 345,
    "id": 43
  },
  {
    "brand": "Samsung",
    "name": "M23",
    "type": "IPS LCD",
    "wholesale": 65000,
    "retail": 88000,
    "stock": 331,
    "id": 44
  },
  {
    "brand": "Redmi",
    "name": "NOTE14 PRO 4GWF",
    "type": "Incell HD+",
    "wholesale": 125000,
    "retail": 169000,
    "stock": 322,
    "id": 45
  },
  {
    "brand": "Redmi",
    "name": "8A",
    "type": "Incell HD+",
    "wholesale": 59000,
    "retail": 80000,
    "stock": 321,
    "id": 46
  },
  {
    "brand": "Xiaomi",
    "name": "POCO X3 / X3 PRO / NOTE9 PRO 5G / MI10T LITE 5G",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 320,
    "id": 47
  },
  {
    "brand": "Redmi",
    "name": "NOTE11 5G / NOTE 11T 5G / NOTE 11S 5G / POCO M4 PRO 5G",
    "type": "Incell HD+",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 284,
    "id": 48
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SMART5",
    "type": "IPS LCD",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 272,
    "id": 49
  },
  {
    "brand": "Redmi",
    "name": "15 4G / 5G",
    "type": "Incell HD+",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 263,
    "id": 50
  },
  {
    "brand": "Oppo",
    "name": "NARZO 50I",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 257,
    "id": 51
  },
  {
    "brand": "Redmi",
    "name": "NOTE13PRO 4GWF",
    "type": "Incell HD+",
    "wholesale": 143000,
    "retail": 194000,
    "stock": 256,
    "id": 52
  },
  {
    "brand": "Tecno & Infinix",
    "name": "HOT40PRO / HOT40",
    "type": "IPS LCD",
    "wholesale": 80000,
    "retail": 108000,
    "stock": 253,
    "id": 53
  },
  {
    "brand": "Samsung",
    "name": "A11 2020 / A115",
    "type": "IPS LCD",
    "wholesale": 76000,
    "retail": 103000,
    "stock": 246,
    "id": 54
  },
  {
    "brand": "Samsung",
    "name": "S10+WF",
    "type": "TFT",
    "wholesale": 170000,
    "retail": 230000,
    "stock": 246,
    "id": 55
  },
  {
    "brand": "Redmi",
    "name": "6A",
    "type": "Incell HD+",
    "wholesale": 69000,
    "retail": 94000,
    "stock": 243,
    "id": 56
  },
  {
    "brand": "Tecno & Infinix",
    "name": "NOTE30I / SPARK20SPRO",
    "type": "IPS LCD",
    "wholesale": 82000,
    "retail": 111000,
    "stock": 230,
    "id": 57
  },
  {
    "brand": "Vivo",
    "name": "Y3 / Y13 / Y3S / Y11 / Y12 / Y15 / Y17 / U3X / U10 / 8A",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 222,
    "id": 58
  },
  {
    "brand": "Oppo",
    "name": "A16 / A16S / A16K / A15 / A15S / A35 / A54S / A56 4G / 5G / A55 5G",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 221,
    "id": 59
  },
  {
    "brand": "Tecno & Infinix",
    "name": "HOT11S / CH6 / CG7 / Camon17PRO / CH7 / Camon18PRO / CI8 / KI7 / LI6 / SPARK8PRO / KJ6 / KJ8",
    "type": "IPS LCD",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 219,
    "id": 60
  },
  {
    "brand": "Tecno & Infinix",
    "name": "BD3 / KF6 / KF6H / KF6i / KF6J / Spark7 / PR651 / PR651H / POP5P / Smart5Pro / PR652B / Vision2S / HOT10i",
    "type": "IPS LCD",
    "wholesale": 69000,
    "retail": 94000,
    "stock": 211,
    "id": 61
  },
  {
    "brand": "Tecno & Infinix",
    "name": "KI7 / SPARK10PRO / HOT30 / POVA5 / LH7 / NOTE30 / LH7N",
    "type": "IPS LCD",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 203,
    "id": 62
  },
  {
    "brand": "Vivo",
    "name": "IQ00 Z7x(m) / VIVO Y100i / VIVO Y78m / IQ00 Z7 / VIVO Y78 / IQ00 Z7X / IQ00 Z8 / IQ00 Z8x / VIVO Y77T-5G / VIVO Y78T / VIVO Y78（t1） / VIVO Y100T / VIVO Y36-4G / VIVO Y36 5G",
    "type": "Incell HD+",
    "wholesale": 68000,
    "retail": 92000,
    "stock": 202,
    "id": 63
  },
  {
    "brand": "Redmi",
    "name": "NOTE11PRO 4GWF",
    "type": "Incell HD+",
    "wholesale": 108000,
    "retail": 146000,
    "stock": 200,
    "id": 64
  },
  {
    "brand": "Redmi",
    "name": "NOTE13 PRO 4G",
    "type": "Incell HD+",
    "wholesale": 87000,
    "retail": 118000,
    "stock": 198,
    "id": 65
  },
  {
    "brand": "Redmi",
    "name": "Y3",
    "type": "Incell HD+",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 195,
    "id": 66
  },
  {
    "brand": "Redmi",
    "name": "NOTE 9S / NOTE9 PRO 4G / NOTE9 PROMAX / NOTE10 LITE / XM POCO M2 PRO",
    "type": "Incell HD+",
    "wholesale": 70000,
    "retail": 95000,
    "stock": 193,
    "id": 67
  },
  {
    "brand": "Tecno & Infinix",
    "name": "CD7 / CD7H / CD6 / CD6J.S / HOT9 / HOT9PRO / SPARK5 / SPARK5PRO / Camon5 / Camon 5air / Note 7lite",
    "type": "IPS LCD",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 193,
    "id": 68
  },
  {
    "brand": "Vivo",
    "name": "Y20 / Y20I / Y20S / Y15A / Y15S / Y11S / Y12S / Y12A / (NEIDAN)Y30 / Y30G / Y31S / IQOOU1X / Y10-(T1 / T2) / Y02",
    "type": "Incell HD+",
    "wholesale": 66000,
    "retail": 90000,
    "stock": 188,
    "id": 69
  },
  {
    "brand": "Xiaomi",
    "name": "F3 / F4 / Mi 11i / Mi11x / Mi11x Pro / Shark 4 / 4Pro",
    "type": "Incell HD+",
    "wholesale": 85000,
    "retail": 115000,
    "stock": 188,
    "id": 70
  },
  {
    "brand": "Tecno & Infinix",
    "name": "HOT10 / CE7 / CE7J / LD7 / LD7J / SPARK6 / Pova / Note8i / Camon16 / Camon16SE",
    "type": "IPS LCD",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 186,
    "id": 71
  },
  {
    "brand": "Redmi",
    "name": "7A",
    "type": "Incell HD+",
    "wholesale": 68000,
    "retail": 92000,
    "stock": 181,
    "id": 72
  },
  {
    "brand": "Samsung",
    "name": "A6 2018 / A600",
    "type": "IPS LCD",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 174,
    "id": 73
  },
  {
    "brand": "Tecno & Infinix",
    "name": "NOTE11 / NOTE12",
    "type": "IPS LCD",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 174,
    "id": 74
  },
  {
    "brand": "Samsung",
    "name": "A325N / A325M / A325F / M325FV / M325F",
    "type": "IPS LCD",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 174,
    "id": 75
  },
  {
    "brand": "Samsung",
    "name": "A31 2020 / A315-WF",
    "type": "IPS LCD",
    "wholesale": 94000,
    "retail": 127000,
    "stock": 168,
    "id": 76
  },
  {
    "brand": "Oppo",
    "name": "A15 / A15S / A35 / V3 / A16K / Q2i / Narzo20 / Narzo30a / Rearlme 7i",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 156,
    "id": 77
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK6GO",
    "type": "IPS LCD",
    "wholesale": 69000,
    "retail": 94000,
    "stock": 152,
    "id": 78
  },
  {
    "brand": "Xiaomi",
    "name": "MI 8 LITE",
    "type": "Incell HD+",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 150,
    "id": 79
  },
  {
    "brand": "Honor",
    "name": "X9C WF",
    "type": "Servis",
    "wholesale": 372000,
    "retail": 503000,
    "stock": 148,
    "id": 80
  },
  {
    "brand": "Tecno & Infinix",
    "name": "KF7J / SPARK7P / HOT10T / HOT10S / SMART6PLUS / VISION3+ / KF7",
    "type": "IPS LCD",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 144,
    "id": 81
  },
  {
    "brand": "Samsung",
    "name": "A14 5G / A146B / A146F / A145F / A145M(BIG）",
    "type": "IPS LCD",
    "wholesale": 74000,
    "retail": 100000,
    "stock": 144,
    "id": 82
  },
  {
    "brand": "Tecno & Infinix",
    "name": "LE6 / HOT10PLAY / HOT11PLAY / POVANEO / LE6H / VOSON2+",
    "type": "IPS LCD",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 143,
    "id": 83
  },
  {
    "brand": "Samsung",
    "name": "A36 / A56",
    "type": "IPS LCD",
    "wholesale": 93000,
    "retail": 126000,
    "stock": 143,
    "id": 84
  },
  {
    "brand": "Redmi",
    "name": "NOTE14 4G WF",
    "type": "Incell HD+",
    "wholesale": 102000,
    "retail": 138000,
    "stock": 137,
    "id": 85
  },
  {
    "brand": "Redmi",
    "name": "POCO X3 GT / NOTE10PRO 5G",
    "type": "Incell HD+",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 134,
    "id": 86
  },
  {
    "brand": "Redmi",
    "name": "NOTE 6 / NOTE6 PRO",
    "type": "Incell HD+",
    "wholesale": 80000,
    "retail": 108000,
    "stock": 131,
    "id": 87
  },
  {
    "brand": "Xiaomi",
    "name": "MI 8",
    "type": "Incell HD+",
    "wholesale": 104000,
    "retail": 141000,
    "stock": 131,
    "id": 88
  },
  {
    "brand": "Redmi",
    "name": "POCO X4 GT",
    "type": "Incell HD+",
    "wholesale": 93000,
    "retail": 126000,
    "stock": 125,
    "id": 89
  },
  {
    "brand": "Honor",
    "name": "RY X8C",
    "type": "Servis",
    "wholesale": 180000,
    "retail": 244000,
    "stock": 122,
    "id": 90
  },
  {
    "brand": "Samsung",
    "name": "A325 / A32 4G / M32 / M325 / F325 / A32LITE",
    "type": "OLED",
    "wholesale": 244000,
    "retail": 330000,
    "stock": 120,
    "id": 91
  },
  {
    "brand": "Tecno & Infinix",
    "name": "KJ6 / SPARK20PRO",
    "type": "IPS LCD",
    "wholesale": 82000,
    "retail": 111000,
    "stock": 118,
    "id": 92
  },
  {
    "brand": "Tecno & Infinix",
    "name": "Note11 / Note12 5G(X671) / Note12pro 4G / 5G(X676B) / Note20 / Note12i",
    "type": "IPS LCD",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 116,
    "id": 93
  },
  {
    "brand": "Samsung",
    "name": "A16-WF",
    "type": "IPS LCD",
    "wholesale": 98000,
    "retail": 133000,
    "stock": 116,
    "id": 94
  },
  {
    "brand": "Vivo",
    "name": "Y93 / Y93A / Y93T / Y91 / Y95 / U1 / Y1S",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 114,
    "id": 95
  },
  {
    "brand": "Redmi",
    "name": "NOTE12 4G-WF",
    "type": "Incell HD+",
    "wholesale": 109000,
    "retail": 148000,
    "stock": 114,
    "id": 96
  },
  {
    "brand": "Xiaomi",
    "name": "MI 9",
    "type": "Incell HD+",
    "wholesale": 125000,
    "retail": 169000,
    "stock": 112,
    "id": 97
  },
  {
    "brand": "Samsung",
    "name": "A34 4G-WF",
    "type": "IPS LCD",
    "wholesale": 116000,
    "retail": 157000,
    "stock": 109,
    "id": 98
  },
  {
    "brand": "Honor",
    "name": "RY  X9",
    "type": "Incell HD+",
    "wholesale": 88000,
    "retail": 119000,
    "stock": 107,
    "id": 99
  },
  {
    "brand": "Honor",
    "name": "X6C WF",
    "type": "Incell HD+",
    "wholesale": 125000,
    "retail": 169000,
    "stock": 107,
    "id": 100
  },
  {
    "brand": "Samsung",
    "name": "A7 2018 / A750",
    "type": "IPS LCD",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 106,
    "id": 101
  },
  {
    "brand": "Huawei",
    "name": "Y7 2019 / Y7PRO 2019",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 105,
    "id": 102
  },
  {
    "brand": "Vivo",
    "name": "Y29 4G / Y300I",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 103,
    "id": 103
  },
  {
    "brand": "Samsung",
    "name": "A12 / A02 / A125 / A127 2021 / A022 / M12",
    "type": "IPS LCD",
    "wholesale": 69000,
    "retail": 94000,
    "stock": 102,
    "id": 104
  },
  {
    "brand": "Xiaomi",
    "name": "MI 14TPRO / MI14T",
    "type": "Incell HD+",
    "wholesale": 137000,
    "retail": 185000,
    "stock": 102,
    "id": 105
  },
  {
    "brand": "Tecno & Infinix",
    "name": "KC8 / KC8S / CC7 / CC7S / KC2 / KC2J / HOT8 / HOT8LITE / CAMON12 / SPARK4",
    "type": "IPS LCD",
    "wholesale": 68000,
    "retail": 92000,
    "stock": 101,
    "id": 106
  },
  {
    "brand": "Tecno & Infinix",
    "name": "BG6 / BG7 / POP8 / KJ5 / KJ5N / SPARKGO2024 / SPARK20C / SPARK20 / SMART8 / SMARTHD / HOTE40I / SMART8PLUS / SMART8PRO / 6525B / BG6H / S24 / BG6I / NOTE40PRO5G / NOTE30VIP / NOTE20PRO",
    "type": "IPS LCD",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 99,
    "id": 107
  },
  {
    "brand": "Samsung",
    "name": "A17WF",
    "type": "IPS LCD",
    "wholesale": 101000,
    "retail": 137000,
    "stock": 99,
    "id": 108
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK GO 2021",
    "type": "IPS LCD",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 97,
    "id": 109
  },
  {
    "brand": "Oppo",
    "name": "RENO5LITE WF",
    "type": "Incell HD+",
    "wholesale": 108000,
    "retail": 146000,
    "stock": 97,
    "id": 110
  },
  {
    "brand": "Vivo",
    "name": "Y19 / Y5S / Z5I / U3 / U20",
    "type": "Incell HD+",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 96,
    "id": 111
  },
  {
    "brand": "Vivo",
    "name": "s6-V1962A / y73s-V2031A / G1-V1962BA / S7 E-V2031A / S10E-V2130A / T1 4G-V2153 / y55 4G-V2154 / Y70外-V2023 / T1 4G-V2168",
    "type": "Incell HD+",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 96,
    "id": 112
  },
  {
    "brand": "Tecno & Infinix",
    "name": "POVA4PRO / LG8 / LG8N",
    "type": "IPS LCD",
    "wholesale": 93000,
    "retail": 126000,
    "stock": 95,
    "id": 113
  },
  {
    "brand": "Honor",
    "name": "X8CWF",
    "type": "Servis",
    "wholesale": 282000,
    "retail": 381000,
    "stock": 95,
    "id": 114
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK8C / S18 / Smart6 / SPARK9T / VISON3 / S661L / S663L / Vision5",
    "type": "IPS LCD",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 93,
    "id": 115
  },
  {
    "brand": "Redmi",
    "name": "NOTE14PRO 4G",
    "type": "Incell HD+",
    "wholesale": 116000,
    "retail": 157000,
    "stock": 93,
    "id": 116
  },
  {
    "brand": "Tecno & Infinix",
    "name": "NOTE30PRO",
    "type": "IPS LCD",
    "wholesale": 82000,
    "retail": 111000,
    "stock": 91,
    "id": 117
  },
  {
    "brand": "Xiaomi",
    "name": "MI 12T PRO / MI12T",
    "type": "Incell HD+",
    "wholesale": 107000,
    "retail": 145000,
    "stock": 91,
    "id": 118
  },
  {
    "brand": "Vivo",
    "name": "Y28 4G / Y38 5G / Y37PRO / Y19S / Y29 5G / Y200+",
    "type": "Incell HD+",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 90,
    "id": 119
  },
  {
    "brand": "Tecno & Infinix",
    "name": "KF8 / Spark7Pro / CG6 / CG6J / Camon17 / Camon18i",
    "type": "IPS LCD",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 89,
    "id": 120
  },
  {
    "brand": "Honor",
    "name": "X6AWF",
    "type": "Incell HD+",
    "wholesale": 99000,
    "retail": 134000,
    "stock": 89,
    "id": 121
  },
  {
    "brand": "Samsung",
    "name": "A30 / A50 / A50S-WF",
    "type": "IPS LCD",
    "wholesale": 92000,
    "retail": 125000,
    "stock": 88,
    "id": 122
  },
  {
    "brand": "Samsung",
    "name": "A8 2018 / A530",
    "type": "IPS LCD",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 87,
    "id": 123
  },
  {
    "brand": "Samsung",
    "name": "J3 2016 / J320 / J300",
    "type": "IPS LCD",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 86,
    "id": 124
  },
  {
    "brand": "Honor",
    "name": "RY X8 WF",
    "type": "Incell HD+",
    "wholesale": 133000,
    "retail": 180000,
    "stock": 84,
    "id": 125
  },
  {
    "brand": "Samsung",
    "name": "A15WF",
    "type": "IPS LCD",
    "wholesale": 94000,
    "retail": 127000,
    "stock": 82,
    "id": 126
  },
  {
    "brand": "Tecno & Infinix",
    "name": "GT20PRO",
    "type": "IPS LCD",
    "wholesale": 89000,
    "retail": 121000,
    "stock": 82,
    "id": 127
  },
  {
    "brand": "Redmi",
    "name": "NOTE13PRO PLUS WF",
    "type": "Incell HD+",
    "wholesale": 143000,
    "retail": 194000,
    "stock": 81,
    "id": 128
  },
  {
    "brand": "Tecno & Infinix",
    "name": "POP5LITE",
    "type": "IPS LCD",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 80,
    "id": 129
  },
  {
    "brand": "Vivo",
    "name": "Y35+ / Y35M+ / Y27 4G / Y36 / Y27 5G",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 79,
    "id": 130
  },
  {
    "brand": "Samsung",
    "name": "A6+ 2018 / A605",
    "type": "IPS LCD",
    "wholesale": 82000,
    "retail": 111000,
    "stock": 79,
    "id": 131
  },
  {
    "brand": "Tecno & Infinix",
    "name": "NOTE40S",
    "type": "IPS LCD",
    "wholesale": 89000,
    "retail": 121000,
    "stock": 77,
    "id": 132
  },
  {
    "brand": "Huawei",
    "name": "Y6P / RY 9A",
    "type": "Incell HD+",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 76,
    "id": 133
  },
  {
    "brand": "Honor",
    "name": "X9C SMART",
    "type": "Incell HD+",
    "wholesale": 97000,
    "retail": 131000,
    "stock": 74,
    "id": 134
  },
  {
    "brand": "Realme",
    "name": "Realme8i / Realme9i / A96 4G / Narzo50",
    "type": "Incell HD+",
    "wholesale": 76000,
    "retail": 103000,
    "stock": 74,
    "id": 135
  },
  {
    "brand": "Honor",
    "name": "RY X8B",
    "type": "Incell HD+",
    "wholesale": 187000,
    "retail": 253000,
    "stock": 74,
    "id": 136
  },
  {
    "brand": "Tecno & Infinix",
    "name": "CK7 / CK7N / CAMON20PRO",
    "type": "IPS LCD",
    "wholesale": 80000,
    "retail": 108000,
    "stock": 73,
    "id": 137
  },
  {
    "brand": "Honor",
    "name": "RY X8B WF",
    "type": "Incell HD+",
    "wholesale": 221000,
    "retail": 299000,
    "stock": 73,
    "id": 138
  },
  {
    "brand": "Samsung",
    "name": "A315 / A31-WF",
    "type": "OLED",
    "wholesale": 226000,
    "retail": 306000,
    "stock": 73,
    "id": 139
  },
  {
    "brand": "Honor",
    "name": "X8BWF",
    "type": "Servis",
    "wholesale": 272000,
    "retail": 368000,
    "stock": 73,
    "id": 140
  },
  {
    "brand": "Samsung",
    "name": "A16 4GWF",
    "type": "OLED",
    "wholesale": 327000,
    "retail": 442000,
    "stock": 72,
    "id": 141
  },
  {
    "brand": "Vivo",
    "name": "Y27S",
    "type": "Incell HD+",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 70,
    "id": 142
  },
  {
    "brand": "Oppo",
    "name": "V40LITE",
    "type": "Incell HD+",
    "wholesale": 99000,
    "retail": 134000,
    "stock": 70,
    "id": 143
  },
  {
    "brand": "Redmi",
    "name": "NOTE12 PRO-WF",
    "type": "Incell HD+",
    "wholesale": 104000,
    "retail": 141000,
    "stock": 69,
    "id": 144
  },
  {
    "brand": "Tecno & Infinix",
    "name": "POP8PRO",
    "type": "IPS LCD",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 68,
    "id": 145
  },
  {
    "brand": "Samsung",
    "name": "A336 / A33-WF",
    "type": "IPS LCD",
    "wholesale": 116000,
    "retail": 157000,
    "stock": 68,
    "id": 146
  },
  {
    "brand": "Redmi",
    "name": "NOTE11 4G / NOTE11S / M4PRO 4G / NOTE12S",
    "type": "Incell HD+",
    "wholesale": 83000,
    "retail": 113000,
    "stock": 67,
    "id": 147
  },
  {
    "brand": "Redmi",
    "name": "NOTE8T",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 65,
    "id": 148
  },
  {
    "brand": "Redmi",
    "name": "NOTE7 / NOTE7PRO / NOTE7PLUS / NOTE 7S",
    "type": "Incell HD+",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 64,
    "id": 149
  },
  {
    "brand": "Honor",
    "name": "RY X8",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 64,
    "id": 150
  },
  {
    "brand": "Redmi",
    "name": "NOTE8 Overseas version",
    "type": "Incell HD+",
    "wholesale": 66000,
    "retail": 90000,
    "stock": 63,
    "id": 151
  },
  {
    "brand": "Tecno & Infinix",
    "name": "Camon30 / CL7 / CL6K / CL6",
    "type": "IPS LCD",
    "wholesale": 88000,
    "retail": 119000,
    "stock": 63,
    "id": 152
  },
  {
    "brand": "Oppo",
    "name": "V40",
    "type": "Incell HD+",
    "wholesale": 143000,
    "retail": 194000,
    "stock": 62,
    "id": 153
  },
  {
    "brand": "Oppo",
    "name": "A36 / A76 / A76New",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 61,
    "id": 154
  },
  {
    "brand": "Redmi",
    "name": "NOTE12PRO-WF",
    "type": "Incell HD+",
    "wholesale": 101000,
    "retail": 137000,
    "stock": 61,
    "id": 155
  },
  {
    "brand": "Samsung",
    "name": "A53 / A536",
    "type": "IPS LCD",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 61,
    "id": 156
  },
  {
    "brand": "Honor",
    "name": "X7C WF",
    "type": "Incell HD+",
    "wholesale": 117000,
    "retail": 158000,
    "stock": 61,
    "id": 157
  },
  {
    "brand": "Xiaomi",
    "name": "MI10T / MI10T PRO",
    "type": "Incell HD+",
    "wholesale": 91000,
    "retail": 123000,
    "stock": 61,
    "id": 158
  },
  {
    "brand": "Honor",
    "name": "X9AWF",
    "type": "Incell HD+",
    "wholesale": 320000,
    "retail": 432000,
    "stock": 61,
    "id": 159
  },
  {
    "brand": "Samsung",
    "name": "J1 2016 / J120",
    "type": "TFT",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 60,
    "id": 160
  },
  {
    "brand": "Huawei",
    "name": "PLAY6TPRO / PLAY7TPRO",
    "type": "Incell HD+",
    "wholesale": 111000,
    "retail": 150000,
    "stock": 60,
    "id": 161
  },
  {
    "brand": "Samsung",
    "name": "A15 / A155 / A156-WF",
    "type": "OLED",
    "wholesale": 298000,
    "retail": 403000,
    "stock": 60,
    "id": 162
  },
  {
    "brand": "Honor",
    "name": "X9D WF",
    "type": "Servis",
    "wholesale": 334000,
    "retail": 451000,
    "stock": 60,
    "id": 163
  },
  {
    "brand": "Honor",
    "name": "X9B WF",
    "type": "Servis",
    "wholesale": 369000,
    "retail": 499000,
    "stock": 60,
    "id": 164
  },
  {
    "brand": "Tecno & Infinix",
    "name": "CAMON15 / 15AIR",
    "type": "IPS LCD",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 59,
    "id": 165
  },
  {
    "brand": "Tecno & Infinix",
    "name": "ZERO40",
    "type": "IPS LCD",
    "wholesale": 104000,
    "retail": 141000,
    "stock": 59,
    "id": 166
  },
  {
    "brand": "Vivo",
    "name": "Y02 / Y02T / Y02A / Y11-2023",
    "type": "Incell HD+",
    "wholesale": 69000,
    "retail": 94000,
    "stock": 58,
    "id": 167
  },
  {
    "brand": "Samsung",
    "name": "A20 / A205",
    "type": "IPS LCD",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 58,
    "id": 168
  },
  {
    "brand": "Realme",
    "name": "realme C31",
    "type": "Incell HD+",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 58,
    "id": 169
  },
  {
    "brand": "Samsung",
    "name": "A515 / A51-WF",
    "type": "OLED",
    "wholesale": 261000,
    "retail": 353000,
    "stock": 58,
    "id": 170
  },
  {
    "brand": "Tecno & Infinix",
    "name": "CC6 / KC3 / CAMON12AIR / S5 / S5LITE",
    "type": "IPS LCD",
    "wholesale": 72000,
    "retail": 98000,
    "stock": 57,
    "id": 171
  },
  {
    "brand": "Redmi",
    "name": "NOTE11 4G-WF",
    "type": "Incell HD+",
    "wholesale": 101000,
    "retail": 137000,
    "stock": 57,
    "id": 172
  },
  {
    "brand": "Samsung",
    "name": "J3Prime / J327",
    "type": "IPS LCD",
    "wholesale": 80000,
    "retail": 108000,
    "stock": 56,
    "id": 173
  },
  {
    "brand": "Realme",
    "name": "REALME5PRO / REALME Q",
    "type": "Incell HD+",
    "wholesale": 80000,
    "retail": 108000,
    "stock": 56,
    "id": 174
  },
  {
    "brand": "Tecno & Infinix",
    "name": "NOTE40PRO 4G",
    "type": "IPS LCD",
    "wholesale": 104000,
    "retail": 141000,
    "stock": 56,
    "id": 175
  },
  {
    "brand": "Samsung",
    "name": "S20 4GWF",
    "type": "TFT",
    "wholesale": 182000,
    "retail": 246000,
    "stock": 56,
    "id": 176
  },
  {
    "brand": "Honor",
    "name": "RY 10LITE(2018)",
    "type": "Incell HD+",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 55,
    "id": 177
  },
  {
    "brand": "Samsung",
    "name": "A26WF",
    "type": "IPS LCD",
    "wholesale": 130000,
    "retail": 176000,
    "stock": 55,
    "id": 178
  },
  {
    "brand": "Samsung",
    "name": "A36WF",
    "type": "IPS LCD",
    "wholesale": 136000,
    "retail": 184000,
    "stock": 55,
    "id": 179
  },
  {
    "brand": "Samsung",
    "name": "A20 2019 / A205-WF",
    "type": "IPS LCD",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 55,
    "id": 180
  },
  {
    "brand": "Oppo",
    "name": "NARZO50IPRIME",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 52,
    "id": 181
  },
  {
    "brand": "Oppo",
    "name": "V20E",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 52,
    "id": 182
  },
  {
    "brand": "Redmi",
    "name": "HM5",
    "type": "Incell HD+",
    "wholesale": 74000,
    "retail": 100000,
    "stock": 50,
    "id": 183
  },
  {
    "brand": "Samsung",
    "name": "A30S 2020 / A307",
    "type": "IPS LCD",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 50,
    "id": 184
  },
  {
    "brand": "Honor",
    "name": "RY X7A",
    "type": "Servis",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 50,
    "id": 185
  },
  {
    "brand": "Tecno & Infinix",
    "name": "POVA NEO6",
    "type": "IPS LCD",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 50,
    "id": 186
  },
  {
    "brand": "Realme",
    "name": "A60 4G / Realme C65 4G / Realme C65 5G / Realme Narzo N65 / Realme 12X 5G / Realme 14X 5G / Realme C75x / OPPO A3 Pro / Realme V60 / Realme V60s / OPPO K12x 5G / OPPO A3X 4G / OPPO A3X 5G / OPPO A35G",
    "type": "Incell HD+",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 50,
    "id": 187
  },
  {
    "brand": "Huawei",
    "name": "NOVA10 SE / NOVA11SE / NOVA12SE",
    "type": "Incell HD+",
    "wholesale": 148000,
    "retail": 200000,
    "stock": 50,
    "id": 188
  },
  {
    "brand": "Honor",
    "name": "X9A WF",
    "type": "Servis",
    "wholesale": 327000,
    "retail": 442000,
    "stock": 50,
    "id": 189
  },
  {
    "brand": "Realme",
    "name": "N61 / N63 / Realme note60",
    "type": "Incell HD+",
    "wholesale": 76000,
    "retail": 103000,
    "stock": 49,
    "id": 190
  },
  {
    "brand": "Realme",
    "name": "REALME12X 5G / REALME12 5G / NARZO70X 5G",
    "type": "Incell HD+",
    "wholesale": 80000,
    "retail": 108000,
    "stock": 49,
    "id": 191
  },
  {
    "brand": "Samsung",
    "name": "M53",
    "type": "IPS LCD",
    "wholesale": 100000,
    "retail": 135000,
    "stock": 49,
    "id": 192
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK GO 2",
    "type": "IPS LCD",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 47,
    "id": 193
  },
  {
    "brand": "Tecno & Infinix",
    "name": "ZEROX NEO",
    "type": "IPS LCD",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 47,
    "id": 194
  },
  {
    "brand": "Oppo",
    "name": "A57 WF",
    "type": "Incell HD+",
    "wholesale": 97000,
    "retail": 131000,
    "stock": 47,
    "id": 195
  },
  {
    "brand": "Oppo",
    "name": "F19PROWF",
    "type": "Incell HD+",
    "wholesale": 99000,
    "retail": 134000,
    "stock": 47,
    "id": 196
  },
  {
    "brand": "iPhone",
    "name": "XR-FHD",
    "type": "Incell HD+",
    "wholesale": 149000,
    "retail": 202000,
    "stock": 47,
    "id": 197
  },
  {
    "brand": "Samsung",
    "name": "A52WF",
    "type": "IPS LCD",
    "wholesale": 117000,
    "retail": 158000,
    "stock": 47,
    "id": 198
  },
  {
    "brand": "iPhone",
    "name": "XS-F(Q-X)",
    "type": "Servis",
    "wholesale": 372000,
    "retail": 503000,
    "stock": 47,
    "id": 199
  },
  {
    "brand": "Samsung",
    "name": "J2Core / J260",
    "type": "IPS LCD",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 45,
    "id": 200
  },
  {
    "brand": "iPhone",
    "name": "XR",
    "type": "Incell HD+",
    "wholesale": 87000,
    "retail": 118000,
    "stock": 45,
    "id": 201
  },
  {
    "brand": "iPhone",
    "name": "XS",
    "type": "Incell HD+",
    "wholesale": 92000,
    "retail": 125000,
    "stock": 45,
    "id": 202
  },
  {
    "brand": "iPhone",
    "name": "X",
    "type": "Incell HD+",
    "wholesale": 92000,
    "retail": 125000,
    "stock": 45,
    "id": 203
  },
  {
    "brand": "Redmi",
    "name": "NOTE14 4G",
    "type": "Incell HD+",
    "wholesale": 85000,
    "retail": 115000,
    "stock": 45,
    "id": 204
  },
  {
    "brand": "Samsung",
    "name": "A35WF",
    "type": "IPS LCD",
    "wholesale": 127000,
    "retail": 172000,
    "stock": 45,
    "id": 205
  },
  {
    "brand": "Samsung",
    "name": "A24-4G / Galaxy A25 5G / Galaxy M34 5G / A26-Galaxy F34 5G",
    "type": "IPS LCD",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 45,
    "id": 206
  },
  {
    "brand": "Honor",
    "name": "X8A / X8 2023",
    "type": "Incell HD+",
    "wholesale": 83000,
    "retail": 113000,
    "stock": 45,
    "id": 207
  },
  {
    "brand": "Samsung",
    "name": "NOTE8WF",
    "type": "TFT",
    "wholesale": 211000,
    "retail": 285000,
    "stock": 45,
    "id": 208
  },
  {
    "brand": "Tecno & Infinix",
    "name": "KM5 / SPARK GO1 / A80(A671L)",
    "type": "IPS LCD",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 44,
    "id": 209
  },
  {
    "brand": "Realme",
    "name": "A7 / A5S / A7n / AX5S / A12 / Realme3 / Realme3i",
    "type": "Incell HD+",
    "wholesale": 69000,
    "retail": 94000,
    "stock": 44,
    "id": 210
  },
  {
    "brand": "Realme",
    "name": "REALME12X 5G / REALME12 5G / NARZO70X 5G",
    "type": "Incell HD+",
    "wholesale": 87000,
    "retail": 118000,
    "stock": 44,
    "id": 211
  },
  {
    "brand": "Realme",
    "name": "A5 / A3S / Realme2 / A5低 / A12e / AX5 / RealmeC1",
    "type": "Incell HD+",
    "wholesale": 74000,
    "retail": 100000,
    "stock": 43,
    "id": 212
  },
  {
    "brand": "iPhone",
    "name": "15PRO",
    "type": "Incell HD+",
    "wholesale": 140000,
    "retail": 189000,
    "stock": 43,
    "id": 213
  },
  {
    "brand": "Oppo",
    "name": "A77 / A78WF",
    "type": "Incell HD+",
    "wholesale": 102000,
    "retail": 138000,
    "stock": 42,
    "id": 214
  },
  {
    "brand": "Samsung",
    "name": "A14 4G / A145P / A145B",
    "type": "IPS LCD",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 41,
    "id": 215
  },
  {
    "brand": "iPhone",
    "name": "13PROMAX",
    "type": "Incell HD+",
    "wholesale": 148000,
    "retail": 200000,
    "stock": 41,
    "id": 216
  },
  {
    "brand": "Samsung",
    "name": "NOTE9WF",
    "type": "TFT",
    "wholesale": 211000,
    "retail": 285000,
    "stock": 41,
    "id": 217
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK30PRO / HOT50PRO / S25 / S685LN",
    "type": "IPS LCD",
    "wholesale": 86000,
    "retail": 117000,
    "stock": 40,
    "id": 218
  },
  {
    "brand": "Realme",
    "name": "realme9 pro plus / realme9 4g / reno7 / oneplus nord ce 2 5G / reno 8t / REALME10 4G",
    "type": "Incell HD+",
    "wholesale": 83000,
    "retail": 113000,
    "stock": 40,
    "id": 219
  },
  {
    "brand": "iPhone",
    "name": "11PROMAX",
    "type": "Incell HD+",
    "wholesale": 108000,
    "retail": 146000,
    "stock": 40,
    "id": 220
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK5AIR / LC7 / LC7S / LC8 / SPARK6AIR / POUVOIR4 / POUVOIR4PRO / SPARKPOWER2",
    "type": "IPS LCD",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 40,
    "id": 221
  },
  {
    "brand": "Samsung",
    "name": "S10WF",
    "type": "TFT",
    "wholesale": 170000,
    "retail": 230000,
    "stock": 40,
    "id": 222
  },
  {
    "brand": "iPhone",
    "name": "X-F(Q)",
    "type": "Servis",
    "wholesale": 362000,
    "retail": 489000,
    "stock": 40,
    "id": 223
  },
  {
    "brand": "Samsung",
    "name": "NOTE10+WF",
    "type": "TFT",
    "wholesale": 232000,
    "retail": 314000,
    "stock": 40,
    "id": 224
  },
  {
    "brand": "Samsung",
    "name": "S23U(USA version)WF",
    "type": "TFT",
    "wholesale": 236000,
    "retail": 319000,
    "stock": 40,
    "id": 225
  },
  {
    "brand": "Samsung",
    "name": "NOTE10-WF",
    "type": "TFT",
    "wholesale": 242000,
    "retail": 327000,
    "stock": 40,
    "id": 226
  },
  {
    "brand": "Realme",
    "name": "A60 4G / Realme C65 4G / Realme C65 5G / Realme Narzo N65 / Realme 12X 5G / Realme 14X 5G / Realme C75x / OPPO A3 Pro / Realme V60 / Realme V60s / OPPO K12x 5G / OPPO A3X 4G / OPPO A3X 5G / OPPO A3 5G",
    "type": "Incell HD+",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 39,
    "id": 227
  },
  {
    "brand": "Samsung",
    "name": "A35 / A55 4G WF",
    "type": "IPS LCD",
    "wholesale": 144000,
    "retail": 195000,
    "stock": 39,
    "id": 228
  },
  {
    "brand": "Samsung",
    "name": "S21UWF",
    "type": "TFT",
    "wholesale": 195000,
    "retail": 264000,
    "stock": 39,
    "id": 229
  },
  {
    "brand": "Samsung",
    "name": "A52 / A525 A52 4G-WF",
    "type": "IPS LCD",
    "wholesale": 117000,
    "retail": 158000,
    "stock": 39,
    "id": 230
  },
  {
    "brand": "Tecno & Infinix",
    "name": "Smart 6 HD / Hot 12i / Smart 6HD 2022 / hot20i",
    "type": "IPS LCD",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 38,
    "id": 231
  },
  {
    "brand": "Vivo",
    "name": "Y04 / Y19E / Y29E / Y29S",
    "type": "Incell HD+",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 38,
    "id": 232
  },
  {
    "brand": "Huawei",
    "name": "RY X10 LITE / Y7A / PSMART 2021",
    "type": "Incell HD+",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 38,
    "id": 233
  },
  {
    "brand": "Realme",
    "name": "Realme8i-5G／A96／K10／narzo50／Realme9i / OPPO A36 / A76 / Realme9pro／K9S / reaimeQ3S／realmeQ3T／Realme v25／realmeQ5／1＋CE2lite / 1+ACE",
    "type": "Incell HD+",
    "wholesale": 88000,
    "retail": 119000,
    "stock": 38,
    "id": 234
  },
  {
    "brand": "Samsung",
    "name": "M52 / M53 / M54",
    "type": "IPS LCD",
    "wholesale": 89000,
    "retail": 121000,
    "stock": 38,
    "id": 235
  },
  {
    "brand": "Samsung",
    "name": "A22 5G(2021) / A226",
    "type": "IPS LCD",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 37,
    "id": 236
  },
  {
    "brand": "Tecno & Infinix",
    "name": "POVA6NEO",
    "type": "IPS LCD",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 37,
    "id": 237
  },
  {
    "brand": "Huawei",
    "name": "PSMART 2021 / Y7A / RY X10 LITE",
    "type": "Incell HD+",
    "wholesale": 76000,
    "retail": 103000,
    "stock": 37,
    "id": 238
  },
  {
    "brand": "iPhone",
    "name": "11",
    "type": "Incell HD+",
    "wholesale": 89000,
    "retail": 121000,
    "stock": 37,
    "id": 239
  },
  {
    "brand": "Samsung",
    "name": "A73-WF",
    "type": "IPS LCD",
    "wholesale": 126000,
    "retail": 171000,
    "stock": 37,
    "id": 240
  },
  {
    "brand": "Samsung",
    "name": "S8+WF",
    "type": "TFT",
    "wholesale": 165000,
    "retail": 223000,
    "stock": 37,
    "id": 241
  },
  {
    "brand": "Tecno & Infinix",
    "name": "CI6 / CI7N / CI8N / CAMON19 / CI8 / CI7 / CAMON19PRO",
    "type": "IPS LCD",
    "wholesale": 80000,
    "retail": 108000,
    "stock": 36,
    "id": 242
  },
  {
    "brand": "Samsung",
    "name": "A54 5G / A546 WF",
    "type": "IPS LCD",
    "wholesale": 127000,
    "retail": 172000,
    "stock": 36,
    "id": 243
  },
  {
    "brand": "Samsung",
    "name": "A315G / A315N / A315F",
    "type": "IPS LCD",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 35,
    "id": 244
  },
  {
    "brand": "Samsung",
    "name": "A40 2020 / A405-WF",
    "type": "IPS LCD",
    "wholesale": 116000,
    "retail": 157000,
    "stock": 35,
    "id": 245
  },
  {
    "brand": "Redmi",
    "name": "NOTE10 4G-WF",
    "type": "Incell HD+",
    "wholesale": 98000,
    "retail": 133000,
    "stock": 35,
    "id": 246
  },
  {
    "brand": "Samsung",
    "name": "A30 / A50 / A50S-WF",
    "type": "OLED",
    "wholesale": 228000,
    "retail": 308000,
    "stock": 35,
    "id": 247
  },
  {
    "brand": "Oppo",
    "name": "A3 / F7",
    "type": "Incell HD+",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 34,
    "id": 248
  },
  {
    "brand": "iPhone",
    "name": "13PRO",
    "type": "Incell HD+",
    "wholesale": 128000,
    "retail": 173000,
    "stock": 34,
    "id": 249
  },
  {
    "brand": "Honor",
    "name": "RY Y72 / Y72S",
    "type": "Incell HD+",
    "wholesale": 74000,
    "retail": 100000,
    "stock": 33,
    "id": 250
  },
  {
    "brand": "Huawei",
    "name": "NOVA Y90",
    "type": "Incell HD+",
    "wholesale": 83000,
    "retail": 113000,
    "stock": 33,
    "id": 251
  },
  {
    "brand": "Tecno & Infinix",
    "name": "ZERO304G / 5G",
    "type": "IPS LCD",
    "wholesale": 104000,
    "retail": 141000,
    "stock": 33,
    "id": 252
  },
  {
    "brand": "iPhone",
    "name": "11-F(Q)",
    "type": "Servis",
    "wholesale": 166000,
    "retail": 225000,
    "stock": 33,
    "id": 253
  },
  {
    "brand": "Realme",
    "name": "Reno8 5G / Reno7 Se 5G / Find X5 Lite / realme 10 / F21 PRO / F21s PRO / Realme Narzo 60 5G / realme 9 4G / Reno8 T / Realme Narzo 50 Pro 5G / Reno8 / 11 / OPPO A78 / Reno7 A / Reno7 4",
    "type": "Incell HD+",
    "wholesale": 72000,
    "retail": 98000,
    "stock": 32,
    "id": 254
  },
  {
    "brand": "Redmi",
    "name": "HM 5",
    "type": "Incell HD+",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 32,
    "id": 255
  },
  {
    "brand": "Xiaomi",
    "name": "MI 11 LITE 4G / 5G",
    "type": "Incell HD+",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 32,
    "id": 256
  },
  {
    "brand": "Redmi",
    "name": "A2 LITE / 6PRO",
    "type": "Incell HD+",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 31,
    "id": 257
  },
  {
    "brand": "Samsung",
    "name": "S22U（EU version）WF",
    "type": "TFT",
    "wholesale": 255000,
    "retail": 345000,
    "stock": 31,
    "id": 258
  },
  {
    "brand": "Realme",
    "name": "A1K / RealmeC2",
    "type": "Incell HD+",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 30,
    "id": 259
  },
  {
    "brand": "Honor",
    "name": "RY X5B",
    "type": "Incell HD+",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 30,
    "id": 260
  },
  {
    "brand": "Tecno & Infinix",
    "name": "HOT40 / SPARK20PRO / KJ6 / KJ7",
    "type": "IPS LCD",
    "wholesale": 85000,
    "retail": 115000,
    "stock": 30,
    "id": 261
  },
  {
    "brand": "Samsung",
    "name": "A11 2020 / A115",
    "type": "IPS LCD",
    "wholesale": 74000,
    "retail": 100000,
    "stock": 30,
    "id": 262
  },
  {
    "brand": "Honor",
    "name": "X5+",
    "type": "Incell HD+",
    "wholesale": 76000,
    "retail": 103000,
    "stock": 29,
    "id": 263
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK20PRO5G / NOTE40X5G",
    "type": "IPS LCD",
    "wholesale": 83000,
    "retail": 113000,
    "stock": 29,
    "id": 264
  },
  {
    "brand": "Samsung",
    "name": "S9WF",
    "type": "TFT",
    "wholesale": 169000,
    "retail": 229000,
    "stock": 29,
    "id": 265
  },
  {
    "brand": "Samsung",
    "name": "A53WF",
    "type": "IPS LCD",
    "wholesale": 113000,
    "retail": 153000,
    "stock": 29,
    "id": 266
  },
  {
    "brand": "Huawei",
    "name": "PSMART Z",
    "type": "Incell HD+",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 28,
    "id": 267
  },
  {
    "brand": "Vivo",
    "name": "Y03 / Y18 / Y37 / Y18E / Y18I / Y18S / Y28E 5G / Y03T / Y28S 5G / T3 LITE 5G",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 28,
    "id": 268
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK8PRO",
    "type": "IPS LCD",
    "wholesale": 86000,
    "retail": 117000,
    "stock": 28,
    "id": 269
  },
  {
    "brand": "Redmi",
    "name": "NOTE10PRO 4G-WF",
    "type": "Incell HD+",
    "wholesale": 105000,
    "retail": 142000,
    "stock": 28,
    "id": 270
  },
  {
    "brand": "Vivo",
    "name": "Y58",
    "type": "Incell HD+",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 28,
    "id": 271
  },
  {
    "brand": "Honor",
    "name": "RY X9A / MAGIC 5LITE",
    "type": "Incell HD+",
    "wholesale": 152000,
    "retail": 206000,
    "stock": 28,
    "id": 272
  },
  {
    "brand": "Samsung",
    "name": "S8WF",
    "type": "TFT",
    "wholesale": 162000,
    "retail": 219000,
    "stock": 28,
    "id": 273
  },
  {
    "brand": "Honor",
    "name": "RY 90WF",
    "type": "OLED",
    "wholesale": 348000,
    "retail": 470000,
    "stock": 28,
    "id": 274
  },
  {
    "brand": "Redmi",
    "name": "NOTE5 PLUS",
    "type": "Incell HD+",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 27,
    "id": 275
  },
  {
    "brand": "Tecno & Infinix",
    "name": "Spark7T",
    "type": "IPS LCD",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 27,
    "id": 276
  },
  {
    "brand": "Vivo",
    "name": "Y35 5G",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 27,
    "id": 277
  },
  {
    "brand": "iPhone",
    "name": "16PRO",
    "type": "Incell HD+",
    "wholesale": 194000,
    "retail": 262000,
    "stock": 27,
    "id": 278
  },
  {
    "brand": "Redmi",
    "name": "NOTE12Pro 4G-WF",
    "type": "OLED",
    "wholesale": 276000,
    "retail": 373000,
    "stock": 27,
    "id": 279
  },
  {
    "brand": "iPhone",
    "name": "14PROMAX-F(Q)",
    "type": "Servis",
    "wholesale": 828000,
    "retail": 1118000,
    "stock": 27,
    "id": 280
  },
  {
    "brand": "Huawei",
    "name": "NOVA10PRO",
    "type": "Servis",
    "wholesale": 468000,
    "retail": 632000,
    "stock": 27,
    "id": 281
  },
  {
    "brand": "Samsung",
    "name": "A04S / A047 / A136B",
    "type": "IPS LCD",
    "wholesale": 72000,
    "retail": 98000,
    "stock": 26,
    "id": 282
  },
  {
    "brand": "Redmi",
    "name": "NOTE5 PLUS",
    "type": "Incell HD+",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 26,
    "id": 283
  },
  {
    "brand": "Tecno & Infinix",
    "name": "POVA NEO 6",
    "type": "IPS LCD",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 26,
    "id": 284
  },
  {
    "brand": "Honor",
    "name": "X7D 5G",
    "type": "Incell HD+",
    "wholesale": 82000,
    "retail": 111000,
    "stock": 26,
    "id": 285
  },
  {
    "brand": "Samsung",
    "name": "A35 / A55",
    "type": "IPS LCD",
    "wholesale": 91000,
    "retail": 123000,
    "stock": 26,
    "id": 286
  },
  {
    "brand": "Redmi",
    "name": "NOTE13PRO 4G WF",
    "type": "OLED",
    "wholesale": 317000,
    "retail": 428000,
    "stock": 26,
    "id": 287
  },
  {
    "brand": "Xiaomi",
    "name": "Mi Note10Pro / Note10Lite",
    "type": "Servis",
    "wholesale": 409000,
    "retail": 553000,
    "stock": 26,
    "id": 288
  },
  {
    "brand": "Redmi",
    "name": "9A / 9AT / 9C / 9i / 10A / POCO-C3",
    "type": "Incell HD+",
    "wholesale": 66000,
    "retail": 90000,
    "stock": 25,
    "id": 289
  },
  {
    "brand": "Redmi",
    "name": "Note 10 / Note 10s / POCO M5S",
    "type": "Incell HD+",
    "wholesale": 82000,
    "retail": 111000,
    "stock": 25,
    "id": 290
  },
  {
    "brand": "Oppo",
    "name": "RENO 5LITE WF",
    "type": "Incell HD+",
    "wholesale": 100000,
    "retail": 135000,
    "stock": 25,
    "id": 291
  },
  {
    "brand": "Samsung",
    "name": "A53 / A535-WF",
    "type": "IPS LCD",
    "wholesale": 115000,
    "retail": 156000,
    "stock": 25,
    "id": 292
  },
  {
    "brand": "Honor",
    "name": "RY X6 / X6X / X8 5G / RY 70LITE / X8A 5G",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 25,
    "id": 293
  },
  {
    "brand": "Oppo",
    "name": "V27 5G",
    "type": "Incell HD+",
    "wholesale": 163000,
    "retail": 221000,
    "stock": 25,
    "id": 294
  },
  {
    "brand": "Samsung",
    "name": "S9+WF",
    "type": "TFT",
    "wholesale": 169000,
    "retail": 229000,
    "stock": 25,
    "id": 295
  },
  {
    "brand": "iPhone",
    "name": "12PROMAX-F-(Q)",
    "type": "Servis",
    "wholesale": 504000,
    "retail": 681000,
    "stock": 25,
    "id": 296
  },
  {
    "brand": "Samsung",
    "name": "A01M 2020 / A015",
    "type": "IPS LCD",
    "wholesale": 68000,
    "retail": 92000,
    "stock": 24,
    "id": 297
  },
  {
    "brand": "Redmi",
    "name": "NOTE5 / NOTE 5 PRO",
    "type": "Incell HD+",
    "wholesale": 73000,
    "retail": 99000,
    "stock": 24,
    "id": 298
  },
  {
    "brand": "iPhone",
    "name": "XSMAX",
    "type": "Incell HD+",
    "wholesale": 101000,
    "retail": 137000,
    "stock": 24,
    "id": 299
  },
  {
    "brand": "Samsung",
    "name": "S24UWF",
    "type": "IPS LCD",
    "wholesale": 242000,
    "retail": 327000,
    "stock": 24,
    "id": 300
  },
  {
    "brand": "iPhone",
    "name": "XSMAX-F(Q)",
    "type": "Servis",
    "wholesale": 433000,
    "retail": 585000,
    "stock": 24,
    "id": 301
  },
  {
    "brand": "Redmi",
    "name": "NOTE11 4G WF",
    "type": "OLED",
    "wholesale": 290000,
    "retail": 392000,
    "stock": 23,
    "id": 302
  },
  {
    "brand": "Vivo",
    "name": "S6 / G1 / S7E / Y70 / Y73S",
    "type": "Incell HD+",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 22,
    "id": 303
  },
  {
    "brand": "Xiaomi",
    "name": "MI NOTE10 LITE / CC9PRO",
    "type": "Incell HD+",
    "wholesale": 120000,
    "retail": 162000,
    "stock": 22,
    "id": 304
  },
  {
    "brand": "Redmi",
    "name": "Note14pro 5G / Note13proplus / PocoX7 / Note14pro plus",
    "type": "Incell HD+",
    "wholesale": 153000,
    "retail": 207000,
    "stock": 22,
    "id": 305
  },
  {
    "brand": "Realme",
    "name": "realme C31",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 21,
    "id": 306
  },
  {
    "brand": "iPhone",
    "name": "12 / 12PRO",
    "type": "Incell HD+",
    "wholesale": 106000,
    "retail": 144000,
    "stock": 21,
    "id": 307
  },
  {
    "brand": "Samsung",
    "name": "A24-4G / Galaxy A25 5G / Galaxy M34 5G / A26-Galaxy F34 5G",
    "type": "IPS LCD",
    "wholesale": 82000,
    "retail": 111000,
    "stock": 21,
    "id": 308
  },
  {
    "brand": "Huawei",
    "name": "NOVA10SE",
    "type": "Servis",
    "wholesale": 323000,
    "retail": 437000,
    "stock": 21,
    "id": 309
  },
  {
    "brand": "iPhone",
    "name": "13PROMAX-F(Q)",
    "type": "Servis",
    "wholesale": 639000,
    "retail": 863000,
    "stock": 21,
    "id": 310
  },
  {
    "brand": "Honor",
    "name": "RY 9XLITE(2020) / RY 8X",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 20,
    "id": 311
  },
  {
    "brand": "Samsung",
    "name": "S20+WF",
    "type": "TFT",
    "wholesale": 185000,
    "retail": 250000,
    "stock": 20,
    "id": 312
  },
  {
    "brand": "Samsung",
    "name": "A20-WF",
    "type": "OLED",
    "wholesale": 228000,
    "retail": 308000,
    "stock": 20,
    "id": 313
  },
  {
    "brand": "Oppo",
    "name": "A5PRO",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 19,
    "id": 314
  },
  {
    "brand": "Samsung",
    "name": "S20UWF",
    "type": "TFT",
    "wholesale": 202000,
    "retail": 273000,
    "stock": 19,
    "id": 315
  },
  {
    "brand": "Samsung",
    "name": "A30S-WF",
    "type": "OLED",
    "wholesale": 228000,
    "retail": 308000,
    "stock": 19,
    "id": 316
  },
  {
    "brand": "Samsung",
    "name": "NOTE11 PRO 4G / NOTE12 PRO 4G WF",
    "type": "OLED",
    "wholesale": 276000,
    "retail": 373000,
    "stock": 18,
    "id": 317
  },
  {
    "brand": "iPhone",
    "name": "16PROMAX",
    "type": "Incell HD+",
    "wholesale": 224000,
    "retail": 303000,
    "stock": 17,
    "id": 318
  },
  {
    "brand": "Redmi",
    "name": "NOTE12 4G-WF",
    "type": "OLED",
    "wholesale": 264000,
    "retail": 357000,
    "stock": 17,
    "id": 319
  },
  {
    "brand": "Samsung",
    "name": "A12 / A02 / A125 / A127 2021 / A022 / A32 5G / M12 / M127 / M02",
    "type": "IPS LCD",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 16,
    "id": 320
  },
  {
    "brand": "Redmi",
    "name": "NOTE11R / 10 5G / 11Prime 5G / POCO M4 5G / M5(INDIA) / NOTE11E",
    "type": "Incell HD+",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 16,
    "id": 321
  },
  {
    "brand": "Honor",
    "name": "X8A / X8 2023",
    "type": "Servis",
    "wholesale": 96000,
    "retail": 130000,
    "stock": 16,
    "id": 322
  },
  {
    "brand": "Honor",
    "name": "RY90",
    "type": "Incell HD+",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 16,
    "id": 323
  },
  {
    "brand": "Samsung",
    "name": "A23 4G / A235 / M336",
    "type": "IPS LCD",
    "wholesale": 72000,
    "retail": 98000,
    "stock": 15,
    "id": 324
  },
  {
    "brand": "iPhone",
    "name": "11PRO",
    "type": "Incell HD+",
    "wholesale": 105000,
    "retail": 142000,
    "stock": 15,
    "id": 325
  },
  {
    "brand": "iPhone",
    "name": "7GW-F(Q)",
    "type": "Servis",
    "wholesale": 125000,
    "retail": 169000,
    "stock": 15,
    "id": 326
  },
  {
    "brand": "iPhone",
    "name": "7PW-F(Q)",
    "type": "Servis",
    "wholesale": 162000,
    "retail": 219000,
    "stock": 15,
    "id": 327
  },
  {
    "brand": "Redmi",
    "name": "NOTE13 4G-WF",
    "type": "OLED",
    "wholesale": 272000,
    "retail": 368000,
    "stock": 15,
    "id": 328
  },
  {
    "brand": "Oppo",
    "name": "NARZO 50A",
    "type": "Incell HD+",
    "wholesale": 70000,
    "retail": 95000,
    "stock": 14,
    "id": 329
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK30PRO / HOT50PRO / S25 / S685LN",
    "type": "IPS LCD",
    "wholesale": 89000,
    "retail": 121000,
    "stock": 14,
    "id": 330
  },
  {
    "brand": "Samsung",
    "name": "A325 / A32 4G / A32LITE-WF",
    "type": "OLED",
    "wholesale": 248000,
    "retail": 335000,
    "stock": 14,
    "id": 331
  },
  {
    "brand": "Samsung",
    "name": "S23U(EU version)WF",
    "type": "TFT",
    "wholesale": 259000,
    "retail": 350000,
    "stock": 14,
    "id": 332
  },
  {
    "brand": "iPhone",
    "name": "12PRO-F(Q）",
    "type": "Servis",
    "wholesale": 473000,
    "retail": 639000,
    "stock": 14,
    "id": 333
  },
  {
    "brand": "Samsung",
    "name": "S10+-WF",
    "type": "OLED",
    "wholesale": 1128000,
    "retail": 1523000,
    "stock": 14,
    "id": 334
  },
  {
    "brand": "Samsung",
    "name": "J5 2017 / J5Pro / J530",
    "type": "IPS LCD",
    "wholesale": 72000,
    "retail": 98000,
    "stock": 13,
    "id": 335
  },
  {
    "brand": "Tecno & Infinix",
    "name": "HOT40(X6836) / SPARK20PRO(KJ6) / Spark10pro(KI7)",
    "type": "IPS LCD",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 13,
    "id": 336
  },
  {
    "brand": "iPhone",
    "name": "13MINI-FHD",
    "type": "Incell HD+",
    "wholesale": 187000,
    "retail": 253000,
    "stock": 13,
    "id": 337
  },
  {
    "brand": "Realme",
    "name": "realme9Pro plus / Realme9 4g / Reno7 / Reno 8t / REALME10 4G",
    "type": "Incell HD+",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 13,
    "id": 338
  },
  {
    "brand": "iPhone",
    "name": "11PROMAX-F(Q)",
    "type": "Servis",
    "wholesale": 514000,
    "retail": 694000,
    "stock": 13,
    "id": 339
  },
  {
    "brand": "Realme",
    "name": "REALME C35 / Narzo 50A prime",
    "type": "Incell HD+",
    "wholesale": 70000,
    "retail": 95000,
    "stock": 12,
    "id": 340
  },
  {
    "brand": "Vivo",
    "name": "A57 5G / A58 5G / A77 5G / A78 5G / NORD N20 SE / NORD N300 5G / A17 / A38 / A18 / A56S 5G / A58X / A57 4G / A17K / A77 4G / A17s / ONE PlusN20se / A1 5G(Vitality Edition Phone) / A17K(A01) / A17K(A40) / A1X 5G / A2M / A2X",
    "type": "Incell HD+",
    "wholesale": 74000,
    "retail": 100000,
    "stock": 12,
    "id": 341
  },
  {
    "brand": "Tecno & Infinix",
    "name": "BG6 / BG7 / BG7N / SMART8HD / SMART8 PRO / SMART8 PLUS / HOT40I / SPARK GO 2024 / POP8 / BG6H / BG6I / SPARK20 / KJ5 / KJ5N / SPARK20C / A666L / A666LN / A70S / RS4 / S24",
    "type": "IPS LCD",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 12,
    "id": 342
  },
  {
    "brand": "Oppo",
    "name": "S6 5G",
    "type": "Incell HD+",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 12,
    "id": 343
  },
  {
    "brand": "iPhone",
    "name": "15PROMAX-F(Q-X)",
    "type": "Servis",
    "wholesale": 908000,
    "retail": 1226000,
    "stock": 12,
    "id": 344
  },
  {
    "brand": "Vivo",
    "name": "Y58",
    "type": "Incell HD+",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 11,
    "id": 345
  },
  {
    "brand": "Redmi",
    "name": "NOTE11S-WF",
    "type": "Incell HD+",
    "wholesale": 99000,
    "retail": 134000,
    "stock": 11,
    "id": 346
  },
  {
    "brand": "iPhone",
    "name": "7PB-F(Q)",
    "type": "Servis",
    "wholesale": 162000,
    "retail": 219000,
    "stock": 11,
    "id": 347
  },
  {
    "brand": "Vivo",
    "name": "s18e / 30lite 5G / 30lite 4G / T3 5G / Y100 4G / Y100 5 G / Y200E 5G / iqooz9 5G / Y300 5G / Y400 5G / iqoo Z10 lite 4G / Y200 5G",
    "type": "Incell HD+",
    "wholesale": 224000,
    "retail": 303000,
    "stock": 11,
    "id": 348
  },
  {
    "brand": "Samsung",
    "name": "A15 / A155 / A156 / M15 / M156 5G",
    "type": "OLED",
    "wholesale": 305000,
    "retail": 412000,
    "stock": 11,
    "id": 349
  },
  {
    "brand": "Honor",
    "name": "RY Y72 / Y72S",
    "type": "Incell HD+",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 10,
    "id": 350
  },
  {
    "brand": "Redmi",
    "name": "NOTE11 4G-WF",
    "type": "Incell HD+",
    "wholesale": 95000,
    "retail": 129000,
    "stock": 10,
    "id": 351
  },
  {
    "brand": "Honor",
    "name": "X7D 5G WF",
    "type": "Incell HD+",
    "wholesale": 137000,
    "retail": 185000,
    "stock": 10,
    "id": 352
  },
  {
    "brand": "Samsung",
    "name": "S21WF",
    "type": "TFT",
    "wholesale": 184000,
    "retail": 249000,
    "stock": 10,
    "id": 353
  },
  {
    "brand": "Samsung",
    "name": "A165 4G / A166 5G / M16 5G / F16 5G / A266 / A26 5G / A175 4G / A176 5G / M176 / F176",
    "type": "OLED",
    "wholesale": 309000,
    "retail": 418000,
    "stock": 10,
    "id": 354
  },
  {
    "brand": "Samsung",
    "name": "A175 4G / A176 5G / M176 / F176 WF",
    "type": "OLED",
    "wholesale": 334000,
    "retail": 451000,
    "stock": 10,
    "id": 355
  },
  {
    "brand": "iPhone",
    "name": "16PRO-F(Q)",
    "type": "Servis",
    "wholesale": 744000,
    "retail": 1005000,
    "stock": 10,
    "id": 356
  },
  {
    "brand": "iPhone",
    "name": "15PRO-F(Q)",
    "type": "Servis",
    "wholesale": 1141000,
    "retail": 1541000,
    "stock": 10,
    "id": 357
  },
  {
    "brand": "Huawei",
    "name": "Y7P / Y7P 2020",
    "type": "Incell HD+",
    "wholesale": 76000,
    "retail": 103000,
    "stock": 9,
    "id": 358
  },
  {
    "brand": "Vivo",
    "name": "Y35 5G",
    "type": "Incell HD+",
    "wholesale": 76000,
    "retail": 103000,
    "stock": 9,
    "id": 359
  },
  {
    "brand": "Oppo",
    "name": "A40 / A60 / A80 / A3PRO",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 9,
    "id": 360
  },
  {
    "brand": "Oppo",
    "name": "A3PRO",
    "type": "Incell HD+",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 9,
    "id": 361
  },
  {
    "brand": "Honor",
    "name": "RY X5B",
    "type": "Servis",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 9,
    "id": 362
  },
  {
    "brand": "Redmi",
    "name": "NOTE10PRO 4G / NOTE10MAX / NOTE11PRO 4G / 5G / NOTE13 4G / POCO X4PRO / NOTE10PRO+ / NOTE11PRO+ / NOTE11E PRO / NOTE14 4G / M7PRO / NOTE12PRO 4G",
    "type": "Incell HD+",
    "wholesale": 80000,
    "retail": 108000,
    "stock": 9,
    "id": 363
  },
  {
    "brand": "iPhone",
    "name": "XSMAX-FHD",
    "type": "Incell HD+",
    "wholesale": 173000,
    "retail": 234000,
    "stock": 9,
    "id": 364
  },
  {
    "brand": "Samsung",
    "name": "A356 / A556 / A55 5G / M35 WF",
    "type": "IPS LCD",
    "wholesale": 144000,
    "retail": 195000,
    "stock": 9,
    "id": 365
  },
  {
    "brand": "Xiaomi",
    "name": "MI 12PRO / MI12S PRO",
    "type": "Incell HD+",
    "wholesale": 162000,
    "retail": 219000,
    "stock": 9,
    "id": 366
  },
  {
    "brand": "Honor",
    "name": "X9CWF",
    "type": "Incell HD+",
    "wholesale": 221000,
    "retail": 299000,
    "stock": 9,
    "id": 367
  },
  {
    "brand": "Samsung",
    "name": "J2Core / J260",
    "type": "IPS LCD",
    "wholesale": 64000,
    "retail": 87000,
    "stock": 8,
    "id": 368
  },
  {
    "brand": "Samsung",
    "name": "A32 4G / A325 / A32 LITE WF",
    "type": "IPS LCD",
    "wholesale": 94000,
    "retail": 127000,
    "stock": 8,
    "id": 369
  },
  {
    "brand": "Xiaomi",
    "name": "F3 / F4 / MI11I",
    "type": "OLED",
    "wholesale": 279000,
    "retail": 377000,
    "stock": 8,
    "id": 370
  },
  {
    "brand": "Oppo",
    "name": "RENO 8T 5G",
    "type": "OLED",
    "wholesale": 290000,
    "retail": 392000,
    "stock": 8,
    "id": 371
  },
  {
    "brand": "Samsung",
    "name": "S23ultra / S918-WF",
    "type": "OLED",
    "wholesale": 654000,
    "retail": 883000,
    "stock": 8,
    "id": 372
  },
  {
    "brand": "Samsung",
    "name": "A21S 2020 / A217",
    "type": "IPS LCD",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 7,
    "id": 373
  },
  {
    "brand": "Samsung",
    "name": "A03CORE / A032",
    "type": "IPS LCD",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 7,
    "id": 374
  },
  {
    "brand": "Tecno & Infinix",
    "name": "HOT60I",
    "type": "IPS LCD",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 7,
    "id": 375
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK20PRO5G / NOTE40X5G",
    "type": "IPS LCD",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 7,
    "id": 376
  },
  {
    "brand": "Vivo",
    "name": "S9e-V2048A / S15e-V2190A / VIVO T1 5G -V2150 / VIVO T1 Pro 5G-V2151",
    "type": "Incell HD+",
    "wholesale": 85000,
    "retail": 115000,
    "stock": 7,
    "id": 377
  },
  {
    "brand": "iPhone",
    "name": "8PB-F(Q)",
    "type": "Servis",
    "wholesale": 166000,
    "retail": 225000,
    "stock": 7,
    "id": 378
  },
  {
    "brand": "Honor",
    "name": "X8 WF",
    "type": "Incell HD+",
    "wholesale": 133000,
    "retail": 180000,
    "stock": 7,
    "id": 379
  },
  {
    "brand": "iPhone",
    "name": "12 / 12PRO-FHD",
    "type": "Incell HD+",
    "wholesale": 173000,
    "retail": 234000,
    "stock": 7,
    "id": 380
  },
  {
    "brand": "Vivo",
    "name": "Y300",
    "type": "Incell HD+",
    "wholesale": 204000,
    "retail": 276000,
    "stock": 7,
    "id": 381
  },
  {
    "brand": "Samsung",
    "name": "S22+WF",
    "type": "TFT",
    "wholesale": 211000,
    "retail": 285000,
    "stock": 7,
    "id": 382
  },
  {
    "brand": "iPhone",
    "name": "11PRO-F(Q)",
    "type": "Servis",
    "wholesale": 473000,
    "retail": 639000,
    "stock": 7,
    "id": 383
  },
  {
    "brand": "Redmi",
    "name": "POCO F3 WF",
    "type": "OLED",
    "wholesale": 323000,
    "retail": 437000,
    "stock": 7,
    "id": 384
  },
  {
    "brand": "Vivo",
    "name": "C21Y/C25Y",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 6,
    "id": 385
  },
  {
    "brand": "Redmi",
    "name": "NOTE 5 / NOTE 5 PRO",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 6,
    "id": 386
  },
  {
    "brand": "Vivo",
    "name": "Y100 / Y100-5G / Y200 / S18E / Y300 5G / Y200 5G / 5G",
    "type": "Incell HD+",
    "wholesale": 87000,
    "retail": 118000,
    "stock": 6,
    "id": 387
  },
  {
    "brand": "iPhone",
    "name": "8GW-F(Q)",
    "type": "Servis",
    "wholesale": 130000,
    "retail": 176000,
    "stock": 6,
    "id": 388
  },
  {
    "brand": "Realme",
    "name": "N61 / N63 / Realme note60",
    "type": "Incell HD+",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 6,
    "id": 389
  },
  {
    "brand": "Honor",
    "name": "X8A / X8 2023",
    "type": "Incell HD+",
    "wholesale": 77000,
    "retail": 104000,
    "stock": 6,
    "id": 390
  },
  {
    "brand": "Samsung",
    "name": "A56WF",
    "type": "IPS LCD",
    "wholesale": 154000,
    "retail": 208000,
    "stock": 6,
    "id": 391
  },
  {
    "brand": "Honor",
    "name": "RY 50",
    "type": "Incell HD+",
    "wholesale": 162000,
    "retail": 219000,
    "stock": 6,
    "id": 392
  },
  {
    "brand": "Samsung",
    "name": "S23WF",
    "type": "TFT",
    "wholesale": 215000,
    "retail": 291000,
    "stock": 6,
    "id": 393
  },
  {
    "brand": "iPhone",
    "name": "13PROMAX-FHD",
    "type": "Incell HD+",
    "wholesale": 228000,
    "retail": 308000,
    "stock": 6,
    "id": 394
  },
  {
    "brand": "Samsung",
    "name": "S23+WF",
    "type": "TFT",
    "wholesale": 289000,
    "retail": 391000,
    "stock": 6,
    "id": 395
  },
  {
    "brand": "Redmi",
    "name": "NOTE10PRO 4G WF",
    "type": "Incell HD+",
    "wholesale": 104000,
    "retail": 141000,
    "stock": 6,
    "id": 396
  },
  {
    "brand": "Oppo",
    "name": "A59 / F1S",
    "type": "Incell HD+",
    "wholesale": 67000,
    "retail": 91000,
    "stock": 5,
    "id": 397
  },
  {
    "brand": "Samsung",
    "name": "A16 4G / A17 / A17 5G / A16 5G / M16 / F16",
    "type": "IPS LCD",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 5,
    "id": 398
  },
  {
    "brand": "Samsung",
    "name": "A515 / A516 / M31S-WF",
    "type": "IPS LCD",
    "wholesale": 93000,
    "retail": 126000,
    "stock": 5,
    "id": 399
  },
  {
    "brand": "iPhone",
    "name": "8GB-F(Q)",
    "type": "Servis",
    "wholesale": 130000,
    "retail": 176000,
    "stock": 5,
    "id": 400
  },
  {
    "brand": "Realme",
    "name": "REALMEC53 / NOTE50",
    "type": "Incell HD+",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 5,
    "id": 401
  },
  {
    "brand": "iPhone",
    "name": "8PW-F-(Q)",
    "type": "Servis",
    "wholesale": 166000,
    "retail": 225000,
    "stock": 5,
    "id": 402
  },
  {
    "brand": "Honor",
    "name": "X7D 4G WF",
    "type": "Incell HD+",
    "wholesale": 137000,
    "retail": 185000,
    "stock": 5,
    "id": 403
  },
  {
    "brand": "Samsung",
    "name": "A245 / A246 / A255 / A256 / M346",
    "type": "IPS LCD",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 4,
    "id": 404
  },
  {
    "brand": "Honor",
    "name": "X6B",
    "type": "Servis",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 4,
    "id": 405
  },
  {
    "brand": "Honor",
    "name": "Magic7 Lite / X9C",
    "type": "Incell HD+",
    "wholesale": 187000,
    "retail": 253000,
    "stock": 4,
    "id": 406
  },
  {
    "brand": "Vivo",
    "name": "Y100 4G",
    "type": "OLED",
    "wholesale": 242000,
    "retail": 327000,
    "stock": 4,
    "id": 407
  },
  {
    "brand": "Samsung",
    "name": "S24WF",
    "type": "IPS LCD",
    "wholesale": 361000,
    "retail": 488000,
    "stock": 4,
    "id": 408
  },
  {
    "brand": "Honor",
    "name": "X9BWF",
    "type": "Incell HD+",
    "wholesale": 376000,
    "retail": 508000,
    "stock": 4,
    "id": 409
  },
  {
    "brand": "Honor",
    "name": "RY X6 / X6S / X8 5G / 70LITE / X8A 5G",
    "type": "Incell HD+",
    "wholesale": 70000,
    "retail": 95000,
    "stock": 3,
    "id": 410
  },
  {
    "brand": "Vivo",
    "name": "Y56 5G / Y35 4G / Y33S 4GOverseas version",
    "type": "Incell HD+",
    "wholesale": 70000,
    "retail": 95000,
    "stock": 3,
    "id": 411
  },
  {
    "brand": "Huawei",
    "name": "PSMART Z",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 3,
    "id": 412
  },
  {
    "brand": "Huawei",
    "name": "CW40 / RY X6A / CW40C / X5 Plus / X5B / X5B Plus",
    "type": "Incell HD+",
    "wholesale": 72000,
    "retail": 98000,
    "stock": 3,
    "id": 413
  },
  {
    "brand": "Samsung",
    "name": "A24 4G-WF",
    "type": "IPS LCD",
    "wholesale": 96000,
    "retail": 130000,
    "stock": 3,
    "id": 414
  },
  {
    "brand": "Xiaomi",
    "name": "MI 13T / MI13TPRO",
    "type": "Incell HD+",
    "wholesale": 125000,
    "retail": 169000,
    "stock": 3,
    "id": 415
  },
  {
    "brand": "Redmi",
    "name": "Note 14 5G / Note 14 / Note 13 / POCO M7 PRO 5G",
    "type": "Incell HD+",
    "wholesale": 80000,
    "retail": 108000,
    "stock": 3,
    "id": 416
  },
  {
    "brand": "Samsung",
    "name": "A725-WF",
    "type": "IPS LCD",
    "wholesale": 126000,
    "retail": 171000,
    "stock": 3,
    "id": 417
  },
  {
    "brand": "iPhone",
    "name": "12MINI-FHD",
    "type": "Incell HD+",
    "wholesale": 187000,
    "retail": 253000,
    "stock": 3,
    "id": 418
  },
  {
    "brand": "Tecno & Infinix",
    "name": "BF7 / BF6 / A60 / A60S / POP7 / KI5K / SPARKGO2023 / SMART10HD / KI5Q / SPARK10(KI5) / SPARK10C / KI8 / KI5N / VISION3 / SMART7 / S23 / POP7PRO / SMARK7HD / A662L / NOTE20 / NOTE12VIP / HOT30I",
    "type": "IPS LCD",
    "wholesale": 70000,
    "retail": 95000,
    "stock": 2,
    "id": 419
  },
  {
    "brand": "Vivo",
    "name": "S6 / G1 / S7E / Y70 / Y73S",
    "type": "Incell HD+",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 2,
    "id": 420
  },
  {
    "brand": "Tecno & Infinix",
    "name": "SPARK5AIR / LC7 / LC7S / LC8 / SPARK6AIR / POUVOIR4 / POUVOIR4PRO / SPARKPOWER2",
    "type": "IPS LCD",
    "wholesale": 76000,
    "retail": 103000,
    "stock": 2,
    "id": 421
  },
  {
    "brand": "Honor",
    "name": "RY X5B",
    "type": "Servis",
    "wholesale": 78000,
    "retail": 106000,
    "stock": 2,
    "id": 422
  },
  {
    "brand": "Samsung",
    "name": "A325N / A325M / A325F / M325FV / M325F",
    "type": "IPS LCD",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 2,
    "id": 423
  },
  {
    "brand": "Huawei",
    "name": "NOVA12I",
    "type": "Incell HD+",
    "wholesale": 84000,
    "retail": 114000,
    "stock": 2,
    "id": 424
  },
  {
    "brand": "iPhone",
    "name": "13",
    "type": "Incell HD+",
    "wholesale": 108000,
    "retail": 146000,
    "stock": 2,
    "id": 425
  },
  {
    "brand": "iPhone",
    "name": "11-FHD",
    "type": "Incell HD+",
    "wholesale": 149000,
    "retail": 202000,
    "stock": 2,
    "id": 426
  },
  {
    "brand": "Huawei",
    "name": "NOVA 5I / NOVA 7I",
    "type": "Servis",
    "wholesale": 115000,
    "retail": 156000,
    "stock": 2,
    "id": 427
  },
  {
    "brand": "Honor",
    "name": "X7B WF",
    "type": "Incell HD+",
    "wholesale": 117000,
    "retail": 158000,
    "stock": 2,
    "id": 428
  },
  {
    "brand": "Honor",
    "name": "RY 70",
    "type": "Incell HD+",
    "wholesale": 158000,
    "retail": 214000,
    "stock": 2,
    "id": 429
  },
  {
    "brand": "Huawei",
    "name": "NOVA12 SE",
    "type": "Servis",
    "wholesale": 160000,
    "retail": 216000,
    "stock": 2,
    "id": 430
  },
  {
    "brand": "Samsung",
    "name": "S21+WF",
    "type": "TFT",
    "wholesale": 184000,
    "retail": 249000,
    "stock": 2,
    "id": 431
  },
  {
    "brand": "Samsung",
    "name": "S22WF",
    "type": "TFT",
    "wholesale": 236000,
    "retail": 319000,
    "stock": 2,
    "id": 432
  },
  {
    "brand": "Vivo",
    "name": "V29E",
    "type": "OLED",
    "wholesale": 242000,
    "retail": 327000,
    "stock": 2,
    "id": 433
  },
  {
    "brand": "Huawei",
    "name": "NOVA12 SE",
    "type": "OLED",
    "wholesale": 335000,
    "retail": 453000,
    "stock": 2,
    "id": 434
  },
  {
    "brand": "Huawei",
    "name": "NOVA10PRO",
    "type": "Servis",
    "wholesale": 475000,
    "retail": 642000,
    "stock": 2,
    "id": 435
  },
  {
    "brand": "Samsung",
    "name": "S24U-WF",
    "type": "OLED",
    "wholesale": 736000,
    "retail": 994000,
    "stock": 2,
    "id": 436
  },
  {
    "brand": "Samsung",
    "name": "J6 2018 / J600",
    "type": "IPS LCD",
    "wholesale": 69000,
    "retail": 94000,
    "stock": 1,
    "id": 437
  },
  {
    "brand": "Oppo",
    "name": "A77S",
    "type": "Incell HD+",
    "wholesale": 70000,
    "retail": 95000,
    "stock": 1,
    "id": 438
  },
  {
    "brand": "Honor",
    "name": "RY X5",
    "type": "Incell HD+",
    "wholesale": 75000,
    "retail": 102000,
    "stock": 1,
    "id": 439
  },
  {
    "brand": "Tecno & Infinix",
    "name": "NOTE10(X693) / NOTE 11I / NOTE 11S(X698) / NOTE 11Pro(X697) / POVA 2(LE7 / LE7n) / POVA3(LF7) / POVA 5G(LE8)",
    "type": "IPS LCD",
    "wholesale": 91000,
    "retail": 123000,
    "stock": 1,
    "id": 440
  },
  {
    "brand": "iPhone",
    "name": "15",
    "type": "Incell HD+",
    "wholesale": 131000,
    "retail": 177000,
    "stock": 1,
    "id": 441
  },
  {
    "brand": "Samsung",
    "name": "A33WF",
    "type": "IPS LCD",
    "wholesale": 113000,
    "retail": 153000,
    "stock": 1,
    "id": 442
  },
  {
    "brand": "Redmi",
    "name": "NOTE12 4G / NOTE 12 5G / POCO X5 4G / POCO X5 5G",
    "type": "Incell HD+",
    "wholesale": 80000,
    "retail": 108000,
    "stock": 1,
    "id": 443
  },
  {
    "brand": "Oppo",
    "name": "RENO 8T 5G",
    "type": "Incell HD+",
    "wholesale": 135000,
    "retail": 183000,
    "stock": 1,
    "id": 444
  },
  {
    "brand": "Samsung",
    "name": "A30S-WF",
    "type": "IPS LCD",
    "wholesale": 86000,
    "retail": 117000,
    "stock": 1,
    "id": 445
  },
  {
    "brand": "Honor",
    "name": "Magic6 Lite 5G / X9B",
    "type": "Incell HD+",
    "wholesale": 189000,
    "retail": 256000,
    "stock": 1,
    "id": 446
  },
  {
    "brand": "iPhone",
    "name": "12PROMAX-FHD",
    "type": "Incell HD+",
    "wholesale": 248000,
    "retail": 335000,
    "stock": 1,
    "id": 447
  },
  {
    "brand": "Samsung",
    "name": "A35 / M35WF",
    "type": "OLED",
    "wholesale": 273000,
    "retail": 369000,
    "stock": 1,
    "id": 448
  },
  {
    "brand": "Samsung",
    "name": "A525 / A526 / A528 / A52S-WF",
    "type": "OLED",
    "wholesale": 283000,
    "retail": 383000,
    "stock": 1,
    "id": 449
  },
  {
    "brand": "Oppo",
    "name": "GT MASTER",
    "type": "OLED",
    "wholesale": 358000,
    "retail": 484000,
    "stock": 1,
    "id": 450
  },
  {
    "brand": "Samsung",
    "name": "S22ultra / S908-WF",
    "type": "OLED",
    "wholesale": 654000,
    "retail": 883000,
    "stock": 1,
    "id": 451
  },
  {
    "brand": "Realme",
    "name": "A32 4G / A33 / A53 4G / A53S / A54 4G / A55 4G / REALME7I / REALMEC17 / 1+N100",
    "type": "Incell HD+",
    "wholesale": 71000,
    "retail": 96000,
    "stock": 0,
    "id": 452
  },
  {
    "brand": "Redmi",
    "name": "NOTE13 4G-WF",
    "type": "Incell HD+",
    "wholesale": 129000,
    "retail": 175000,
    "stock": 0,
    "id": 453
  },
  {
    "brand": "Samsung",
    "name": "A70 2019 / A705-WF",
    "type": "IPS LCD",
    "wholesale": 94000,
    "retail": 127000,
    "stock": 0,
    "id": 454
  },
  {
    "brand": "Redmi",
    "name": "NOTE14 4G",
    "type": "Incell HD+",
    "wholesale": 79000,
    "retail": 107000,
    "stock": 0,
    "id": 455
  },
  {
    "brand": "Honor",
    "name": "RY X7C",
    "type": "Incell HD+",
    "wholesale": 81000,
    "retail": 110000,
    "stock": 0,
    "id": 456
  }
];
