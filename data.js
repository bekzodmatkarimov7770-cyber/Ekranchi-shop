// ==========================================
// 1. REKLAMALAR VA YANGILIKLAR BANERI
// ==========================================
const bannersData = [
  {
    badge: "YANGILIK",
    title: "🔥 Yangi original partiya keldi!",
    desc: "Samsung, Redmi va Honor displeylari omborda.",
    bg: "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)"
  },
  {
    badge: "YETKAZISH",
    title: "🚚 Viloyatlarga tezkor BTS Pochta!",
    desc: "Toshkent bo'yicha taksi orqali bir necha soatda yetkaziladi.",
    bg: "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
  },
  {
    badge: "AKSIYA",
    title: "🎁 15+ xarid uchun ulgurji narx!",
    desc: "15 ta ekran to'plang va avtomatik optom chegirmaga ega bo'ling.",
    bg: "linear-gradient(135deg, #f12711 0%, #f5af19 100%)"
  }
];

// ==========================================
// 2. MAHSULOTLAR, NARXLAR VA OMBOR RO'YXATI
// ==========================================
const productsData = [
  { 
    id: 1, 
    brand: 'Samsung', 
    name: 'Samsung A14 5G', 
    type: 'Original', 
    wholesale: 180000, 
    retail: 220000, 
    stock: 35, 
    img: 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=200&auto=format&fit=crop&q=60' 
  },
  { 
    id: 2, 
    brand: 'Samsung', 
    name: 'Samsung A12', 
    type: 'BOE Zavod', 
    wholesale: 140000, 
    retail: 175000, 
    stock: 4, 
    img: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=200&auto=format&fit=crop&q=60' 
  },
  { 
    id: 3, 
    brand: 'Redmi', 
    name: 'Redmi Note 12', 
    type: 'FOG', 
    wholesale: 150000, 
    retail: 190000, 
    stock: 0, 
    img: 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=200&auto=format&fit=crop&q=60' 
  },
  { 
    id: 4, 
    brand: 'Honor', 
    name: 'Honor 90', 
    type: 'Original', 
    wholesale: 310000, 
    retail: 370000, 
    stock: 12, 
    img: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=200&auto=format&fit=crop&q=60' 
  },
  { 
    id: 5, 
    brand: 'Honor', 
    name: 'Honor 200', 
    type: 'OLED', 
    wholesale: 350000, 
    retail: 420000, 
    stock: 20, 
    img: 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=200&auto=format&fit=crop&q=60' 
  },
  { 
    id: 6, 
    brand: 'Huawei', 
    name: 'Huawei Nova 9', 
    type: 'OLED', 
    wholesale: 280000, 
    retail: 340000, 
    stock: 7, 
    img: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=200&auto=format&fit=crop&q=60' 
  },
  { 
    id: 7, 
    brand: 'iPhone', 
    name: 'iPhone 11', 
    type: 'Incell', 
    wholesale: 210000, 
    retail: 260000, 
    stock: 15, 
    img: 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=200&auto=format&fit=crop&q=60' 
  },
  { 
    id: 8, 
    brand: 'Vivo', 
    name: 'Vivo Y20', 
    type: 'Original', 
    wholesale: 130000, 
    retail: 165000, 
    stock: 10, 
    img: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=200&auto=format&fit=crop&q=60' 
  },
  { 
    id: 9, 
    brand: 'Oppo', 
    name: 'Oppo A54', 
    type: 'TFT', 
    wholesale: 135000, 
    retail: 170000, 
    stock: 0, 
    img: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=200&auto=format&fit=crop&q=60' 
  },
  { 
    id: 10, 
    brand: 'Tecno', 
    name: 'Tecno Spark 10C', 
    type: 'Oddiy', 
    wholesale: 125000, 
    retail: 160000, 
    stock: 18, 
    img: 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=200&auto=format&fit=crop&q=60' 
  },
  { 
    id: 11, 
    brand: 'Infinix', 
    name: 'Infinix Hot 30', 
    type: 'Oddiy', 
    wholesale: 130000, 
    retail: 165000, 
    stock: 9, 
    img: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=200&auto=format&fit=crop&q=60' 
  }
];
