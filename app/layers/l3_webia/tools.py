import re
from typing import Dict, Any, List, Optional
from app.services.handoff_service import HandoffService
from app.layers.l3_webia.brief_service import BusinessBriefService, BusinessBriefSchema


WEBIA_ADDONS = [
    {
        "id": "seo-optimization",
        "name": "SEO Optimization",
        "description": "Optimasi teknis dan konten meta tag terstruktur sesuai standar Google.",
    },
    {
        "id": "admin-dashboard",
        "name": "Admin Dashboard",
        "description": "Kelola konten produk, artikel, dan layanan melalui panel admin CMS mandiri.",
    },
    {
        "id": "custom-module",
        "name": "Custom Module",
        "description": "Tambahkan fungsi khusus seperti kalkulator tarif, filter kustom, atau alur unik bisnis.",
    },
    {
        "id": "integrasi-tambahan",
        "name": "Integrasi Tambahan",
        "description": "Integrasi layanan pihak ketiga, API eksternal, atau sistem CRM.",
    },
]

WEBIA_PACKAGES = [
    {
        "id": "pixel",
        "name": "Paket Pixel",
        "tagline": "01 / START SIMPLE",
        "price": 499000,
        "price_formatted": "Rp499.000",
        "original_price": "Rp589.500",
        "type": "TANPA CMS",
        "payment": "Sekali bayar",
        "description": "Tampil profesional di internet dengan landing page sederhana dan hemat.",
        "features": [
            "1 Halaman landing page responsif mobile-friendly",
            "WhatsApp order instan, form kontak, dan peta Google Maps",
            "AI Chatbot 500 pesan/bulan*",
            "Loading cepat dan mobile-first",
        ],
    },
    {
        "id": "pulse",
        "name": "Paket Pulse",
        "tagline": "02 / GET NOTICED",
        "price": 899000,
        "price_formatted": "Rp899.000",
        "original_price": "Rp1.199.000",
        "type": "TANPA CMS",
        "payment": "Sekali bayar",
        "description": "Landing page lebih lengkap untuk memperkuat kehadiran digital brand di Google.",
        "features": [
            "Landing page komprehensif satu halaman",
            "Galeri visual, testimoni klien, daftar layanan, dan FAQ interaktif",
            "AI Chatbot 1.500 pesan/bulan*",
            "Optimasi SEO dasar dan analitik pengunjung",
        ],
    },
    {
        "id": "nexus",
        "name": "Paket Nexus",
        "tagline": "03 / TAKE CONTROL",
        "price": 1499000,
        "price_formatted": "Rp1.499.000",
        "original_price": "Rp1.999.000",
        "type": "DENGAN CMS",
        "payment": "Sekali bayar",
        "description": "Kelola konten, layanan, produk, dan artikel secara mandiri kapan saja.",
        "features": [
            "Website multi-halaman (multi-page)",
            "Dashboard CMS Admin Mandiri tanpa koding",
            "Tracking data pelanggan dan formulir penawaran",
            "AI Chatbot 2.500 pesan/bulan*",
            "SEO lanjutan untuk kata kunci pencarian lokal",
        ],
    },
    {
        "id": "infinity",
        "name": "Paket Infinity",
        "tagline": "04 / BEYOND LIMITS",
        "price": 2499000,
        "price_formatted": "Rp2.499.000",
        "original_price": "Rp3.499.000",
        "type": "ADVANCED CMS",
        "payment": "Sekali bayar",
        "badge": "★ REKOMENDASI UTAMA",
        "description": "Website fleksibel dengan CMS lanjutan dan fitur kustom sesuai alur bisnis.",
        "features": [
            "Custom fitur sesuai alur bisnis spesifik",
            "CMS lanjutan dengan multi-admin dan tracking pelanggan",
            "AI Chatbot 5.000 pesan/bulan*",
            "Optimasi performa tinggi dan prioritas dukungan teknis",
        ],
    },
]

WEBIA_CATEGORIES = [
    {"number": "01", "slug": "fnb", "name": "F&B", "symbol": "☕", "desc": "Restaurant, cafe, catering, bakery, food product"},
    {"number": "02", "slug": "beauty", "name": "Beauty", "symbol": "✿", "desc": "Salon, barbershop, beauty clinic, skincare, MUA"},
    {"number": "03", "slug": "automotive", "name": "Automotive", "symbol": "✦", "desc": "Bengkel, car wash, dealer, body repair"},
    {"number": "04", "slug": "company", "name": "Company", "symbol": "▧", "desc": "Company profile, contractor, distributor, manufacturer, agency"},
    {"number": "05", "slug": "property", "name": "Property", "symbol": "⌂", "desc": "Developer, property agent, real estate, villa"},
    {"number": "06", "slug": "education", "name": "Education", "symbol": "✎", "desc": "School, course, tutor, training, online course"},
    {"number": "07", "slug": "professional-service", "name": "Professional Service", "symbol": "◇", "desc": "Consultant, lawyer, accountant, freelancer"},
    {"number": "08", "slug": "personal-brand", "name": "Personal Brand", "symbol": "✧", "desc": "Creator, influencer, portfolio"},
    {"number": "09", "slug": "retail", "name": "Retail", "symbol": "▣", "desc": "Store, distributor, supplier, fashion, gadget"},
    {"number": "10", "slug": "healthcare", "name": "Healthcare", "symbol": "✚", "desc": "Clinic, pharmacy, medical practice, dental"},
    {"number": "11", "slug": "pet-animal-service", "name": "Pet & Animal Services", "symbol": "🐾", "desc": "Pet shop, pet care, grooming salon, veterinary clinic"},
    {"number": "12", "slug": "technology-it", "name": "Technology & IT", "symbol": "⚡", "desc": "Software house, IT agency, web development, SaaS, tech startup"},
    {"number": "13", "slug": "travel-tourism", "name": "Travel & Tourism", "symbol": "✈", "desc": "Tour & travel agent, open trip, vacation packages, eco-tourism"},
    {"number": "14", "slug": "interior-architecture", "name": "Interior & Architecture", "symbol": "🛋", "desc": "Custom furniture, interior design, architecture, woodcraft"},
    {"number": "15", "slug": "home-services", "name": "Home Services & Laundry", "symbol": "🧺", "desc": "Laundry kiloan/satuan, dry clean, cuci sepatu, home cleaning, renovasi hunian"},
    {"number": "16", "slug": "agriculture-farming", "name": "Agriculture & Farming", "symbol": "🌱", "desc": "Peternakan sapi/kambing/unggas, agribisnis, smart farming IoT, hasil bumi"},
    {"number": "17", "slug": "transportation-logistics", "name": "Transportation & Logistics", "symbol": "🚛", "desc": "Ekspedisi kargo, logistik, freight forwarding, trucking, tracking armada"},
    {"number": "18", "slug": "nonprofit-community", "name": "Non-Profit & Community", "symbol": "🤝", "desc": "Yayasan, organisasi sosial, aksi kemanusiaan, komunitas relawan, lembaga filantropi, panti asuhan"},
    {"number": "19", "slug": "photography-creative-studio", "name": "Photography & Creative Studio", "symbol": "📷", "desc": "Studio foto produk, fotografer komersial, studio wisuda, wedding photoshoot, videografi"},
    {"number": "20", "slug": "sports-fitness", "name": "Sports & Fitness", "symbol": "🏋️", "desc": "Mega gym, fitness center, studio pilates, personal trainer, athletic performance"},
]

# PRD WEBIA §7.6: Category & Package Recommendation Matrix
RECOMMENDATION_MATRIX = {
    "fnb": {
        "category_name": "F&B (Food & Beverages)",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila Anda perlu admin CMS untuk rutin ganti menu & promo berkala, atau Infinity bila butuh sistem e-commerce/pos pemesanan kompleks.",
        "template_id": "Little Corner / Daily Crumb",
        "template_slug": "little-corner",
        "template_name": "Little Corner (Cafe) / Daily Crumb (Bakery) / F01 Cafe Earthtone",
        "recommended_modules": ["WhatsApp Direct Order", "Booking Meja / Reservasi", "Interactive FAQ Chips", "Google Maps Embed"],
    },
    "beauty": {
        "category_name": "Beauty & Wellness",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila perlu admin dashboard untuk jadwal appointment terapis atau manajemen katalog treatment klinik.",
        "template_id": "Maison Beauty / Blush Nail Studio",
        "template_slug": "maison-beauty",
        "template_name": "Maison Beauty / Blush Nail Studio / Salon Classic Warm Neutral / Salon Elegant Soft Pink / Salon Modern Sage",
        "recommended_modules": ["Appointment Booking", "Galeri Portofolio & Before-After", "Daftar Terapis/Treatment", "AI CS 24/7"],
    },
    "automotive": {
        "category_name": "Automotive",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila bengkel/dealer memerlukan admin service management untuk melacak riwayat servis berkala pelanggan.",
        "template_id": "Pitstop Garage",
        "template_slug": "pitstop-garage",
        "template_name": "Pitstop Garage (Bengkel) / Bengkel Otto (Artistic Workshop) / Samudra Detailing (Ceramic Coating) / AURUM Premium / Tidal Detail",
        "recommended_modules": ["Booking Servis Berkala", "Emergency Call WhatsApp", "Peta Bengkel", "Daftar Paket Servis"],
    },
    "company": {
        "category_name": "Company Profile & Contractor",
        "entry_package": "Nexus",
        "entry_price": "Rp1.499.000",
        "upgrade_package": "Infinity",
        "upgrade_trigger": "Bila membutuhkan portal rekanan khusus, multi-admin approval, atau integrasi CRM/ERP perusahaan.",
        "template_id": "Northstar Studio",
        "template_slug": "northstar-studio",
        "template_name": "Northstar Studio (Company Profile & Contractor)",
        "recommended_modules": ["Showcase Proyek/Portofolio", "Formulir RFQ (Permintaan Penawaran)", "Profil Direksi & Legalitas ISO", "Blog & Berita"],
    },
    "property": {
        "category_name": "Property & Real Estate",
        "entry_package": "Nexus",
        "entry_price": "Rp1.499.000",
        "upgrade_package": "Infinity",
        "upgrade_trigger": "Bila perlu portal listing unit dinamis, kalkulator KPR interaktif, dan integrasi CRM sales properti.",
        "template_id": "Casa Verde",
        "template_slug": "casa-verde",
        "template_name": "Casa Verde (Property & Real Estate)",
        "recommended_modules": ["Listing Unit Properti", "Jadwal Survey Lokasi", "Virtual Tour / Video Embed", "Brosur Download"],
    },
    "education": {
        "category_name": "Education & Course",
        "entry_package": "Nexus",
        "entry_price": "Rp1.499.000",
        "upgrade_package": "Infinity",
        "upgrade_trigger": "Bila butuh integrasi LMS, pembayaran SPP/kursus online otomatis, dan area member siswa.",
        "template_id": "SPARK Academy / BrightPath / Rumah Latte & Tunas Cendekia (Daycare)",
        "template_slug": "spark-academy-maximum-impact",
        "template_name": "Ruby Academy (School of Excellence) / SPARK Academy (Modern School) / EduPrime (Bootcamp) / Rumah Latte & Tunas Cendekia (Daycare & Preschool)",
        "recommended_modules": ["Formulir Pendaftaran Siswa / PPDB Online", "Jadwal Kelas, Biaya SPP & Daycare", "Profil Pengajar/Tutor", "Testimoni Alumni & Wali Murid"],
    },
    "professional_service": {
        "category_name": "Professional Service (Hukum, Pajak, Konsultan)",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila konsultan memerlukan CMS artikel edukasi reguler, lead capture terintegrasi, atau portal dokumen klien.",
        "template_id": "Nexa Consulting",
        "template_slug": "nexa-consulting",
        "template_name": "Nexa Consulting (Legal & Business Consultant)",
        "recommended_modules": ["Booking Konsultasi", "Artikel & Legal Insight", "Profil Partner/Konsultan", "WhatsApp Confidential"],
    },
    "personal_brand": {
        "category_name": "Personal Brand & Creator",
        "entry_package": "Pixel",
        "entry_price": "Rp499.000",
        "upgrade_package": "Pulse",
        "upgrade_trigger": "Upgrade ke Pulse bila butuh galeri portofolio lengkap & review klien, atau Nexus bila perlu blog tulisan mandiri.",
        "template_id": "The Creator Room",
        "template_slug": "the-creator-room",
        "template_name": "The Creator Room / Arya Sanjaya (Author Portfolio) / Lumiere Photography Studio",
        "recommended_modules": ["Social Media Hub", "Portofolio Showreel", "Media Kit Download", "Direct Endorsement Contact"],
    },
    "retail": {
        "category_name": "Retail & Online Store",
        "entry_package": "Nexus",
        "entry_price": "Rp1.499.000",
        "upgrade_package": "Infinity",
        "upgrade_trigger": "Bila membutuhkan payment gateway otomatis, manajemen stok multi-gudang, atau integrasi kurir pengiriman.",
        "template_id": "Urban Supply",
        "template_slug": "urban-supply",
        "template_name": "Urban Supply (Modern Store) / Aurora Petit & Petit Wonder (Baby & Kids Boutique)",
        "recommended_modules": ["Etalase Katalog Produk", "Admin CMS Produk", "WhatsApp Quick Checkout", "Kategori & Search Produk"],
    },
    "healthcare": {
        "category_name": "Healthcare & Clinic",
        "entry_package": "Nexus",
        "entry_price": "Rp1.499.000",
        "upgrade_package": "Infinity",
        "upgrade_trigger": "Bila butuh integrasi rekam medis, portal pasien, atau sistem antrean dokter spesifik.",
        "template_id": "Medika Care / Sunset Dental / Azure Smile / Mint Dental",
        "template_slug": "healthcare-dental-sunset",
        "template_name": "Sunset Dental Care / Azure Smile / Medika Care / Mitra Jiwa (Psikologi & Konseling)",
        "recommended_modules": ["Jadwal Dokter Praktek", "Pendaftaran Pasien Online", "Kalkulator Estimasi Biaya/Cicilan", "Lokasi & Call Center Darurat"],
    },
    "pet_animal_service": {
        "category_name": "Pet & Animal Services",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila pet shop memiliki ratusan stok pakan & aksesoris yang perlu dikelola mandiri via Dashboard CMS.",
        "template_id": "PawMart / Furry & Co.",
        "template_slug": "petshop-minimalist-glacierblue",
        "template_name": "PawMart (Pet Shop Minimalist) / Furry & Co. (Pet Boutique Luxury) / Pawtopia (Animal Care & Clinic)",
        "recommended_modules": ["Katalog Makanan & Perlengkapan Hewan", "Online Booking Grooming", "Direct WhatsApp Order", "AI Nutrisi & Perawatan Hewan"],
    },
    "technology_it": {
        "category_name": "Technology & IT",
        "entry_package": "Nexus",
        "entry_price": "Rp1.499.000",
        "upgrade_package": "Infinity",
        "upgrade_trigger": "Bila software house memerlukan portal klien mandiri, sistem tiket/proyek custom, atau integrasi API backend kompleks.",
        "template_id": "AzuraCraft Studio / RoseCode / Nexora Digital",
        "template_slug": "technology-softwarehouse-elegant-babyblue-putri",
        "template_name": "AzuraCraft Studio / Aetherion (Hardware) / Cyberwave (Networking) / Nexora Digital",
        "recommended_modules": ["Showcase Portofolio Proyek IT", "Estimator Biaya Pembuatan Software", "Tech Stack & Layanan", "Formulir RFP / Kontak WhatsApp"],
    },
    "travel_tourism": {
        "category_name": "Travel & Tourism",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila biro perjalanan memerlukan CMS untuk mengupdate jadwal keberangkatan open trip, itinerary baru, dan galeri tur berkala.",
        "template_id": "OceanJourney / GreenTrip / GrandJourney",
        "template_slug": "travel-agent-ocean-teal",
        "template_name": "OceanJourney (Modern Ocean Teal) / GreenTrip / Baitul Safar (Biro Umrah & Haji Khusus)",
        "recommended_modules": ["Katalog Paket Wisata", "Itinerary Harian Lengkap", "Jadwal Keberangkatan", "Formulir Booking / WhatsApp Consultant"],
    },
    "interior_architecture": {
        "category_name": "Interior, Furniture & Architecture",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila toko mebel atau biro interior membutuhkan upload katalog produk furnitur custom secara mandiri tanpa koding.",
        "template_id": "WoodenLane / RusticFurni / Griya Etnik Nantara",
        "template_slug": "furniture-mocha-cream",
        "template_name": "WoodenLane (Premium Minimal) / RusticFurni (Rustic Terracotta) / Griya Etnik Nantara",
        "recommended_modules": ["Katalog Furnitur & Ruang", "Visualizer / Galeri 3D", "Formulir Custom Furniture", "Konsultasi WhatsApp Desainer"],
    },
    "home_services": {
        "category_name": "Home Services & Laundry",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila bisnis laundry Anda membutuhkan sistem CMS untuk update promo berkala, pelacakan status pengerjaan cucian, atau form booking antar-jemput.",
        "template_id": "Mint Fresh / Baby Blue / Classic Trust",
        "template_slug": "laundry-mint-fresh",
        "template_name": "Mint Fresh Laundry (Minimalis) / Classic Trust (Professional) / Baby Blue (Modern) / Aurelia (Renovation) / Matcha Clean",
        "recommended_modules": ["Price List Kiloan & Satuan", "Interactive Coverage Area Map", "Live Status Buka/Tutup Toko", "Form Booking Pick-up & Delivery", "Kalkulator Estimasi Biaya Renovasi per m2", "Form Booking Survey Arsitek", "AI Chatbot CS"],
    },
    "agriculture_farming": {
        "category_name": "Agriculture & Farming",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila usaha peternakan atau agribisnis membutuhkan katalog stok hewan qurban/panen berkala, dashboard IoT kandang, atau pemesanan B2B suplai.",
        "template_id": "Agriternak Bold Livestock / Agriternak Futuristic IoT",
        "template_slug": "agriternak-bold-livestock",
        "template_name": "Agriternak Bold Livestock (Peternakan Tangguh) / Futuristic IoT (Smart Farming) / Organic Precision",
        "recommended_modules": ["Katalog Hewan Ternak & Bobot", "Sertifikasi Kesehatan & SKKH", "Monitoring Sensor IoT Kandang", "Form Pemesanan Qurban/B2B", "WhatsApp Farm Manager"],
    },
    "transportation_logistics": {
        "category_name": "Transportation & Logistics",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila perusahaan ekspedisi membutuhkan dashboard CMS untuk update tarif rute berkala, manajemen armada, atau integrasi API tracking resi.",
        "template_id": "Swiftly (Express Delivery) / Hearth & Haul (Moving Company) / Atelier Move (Luxury Relocation) / Logistics Company Classic Trust",
        "template_slug": "logistics-company-classic-trust",
        "template_name": "Swiftly (Express Delivery) / Hearth & Haul (Moving Company) / Atelier Move (Luxury Relocation) / Logistics Company Classic Trust",
        "recommended_modules": ["Cek Resi / Tracking Muatan", "Kalkulator Freight Cargo", "Peta Jangkauan Armada", "Formulir Permintaan Penawaran (RFQ)", "WhatsApp CS Ekspedisi"],
    },
    "nonprofit_community": {
        "category_name": "Non-Profit & Community (Yayasan, Donasi, Lembaga Sosial)",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila yayasan membutuhkan CMS untuk mempublikasikan laporan transparansi donasi, agenda bakti sosial berkala, dan artikel aksi lapangan.",
        "template_id": "REVOLT // IMPACT",
        "template_slug": "revolt-impact-social-organization",
        "template_name": "REVOLT // IMPACT (Bold Social Movement & Organization)",
        "recommended_modules": ["Live Impact & Donation Counter", "Formulir Pendaftaran Relawan Online", "Tiers Donasi Transparan", "Interactive Manifesto Visi-Misi", "Kalender Event Aksi Sosial", "WhatsApp Koordinator"],
    },
    "photography_creative_studio": {
        "category_name": "Photography & Creative Studio",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila studio memerlukan CMS upload portofolio client photoshoot berkala, update pricelist musiman, dan download invoice/proposal klien.",
        "template_id": "Peachy Studio / Lumière Studio / Noir Studio",
        "template_slug": "peachy-studio",
        "template_name": "Peachy Studio (Product Photography) / Lumière Studio (Luxury) / Noir Studio (Dramatic)",
        "recommended_modules": ["Showcase Portofolio Foto Kategori Interaktif", "Pricelist Paket Photoshoot", "Formulir Booking Sesi Foto", "Direct WhatsApp Studio Admin", "Testimoni Klien & Brand"],
    },
    "sports_fitness": {
        "category_name": "Sports, Gym & Fitness",
        "entry_package": "Pulse",
        "entry_price": "Rp899.000",
        "upgrade_package": "Nexus",
        "upgrade_trigger": "Bila tempat gym/fitness butuh CMS manajemen jadwal kelas harian, profil pelatih/instruktur, dan registrasi membership online.",
        "template_id": "IRONPULSE / Apex Pulse / Strawberry Fizz",
        "template_slug": "ironpulse-gym-fitness-center",
        "template_name": "IRONPULSE (Mega Gym & Strength) / Apex Pulse (Athletic Performance) / Strawberry Fizz (Pilates Studio) / Jelly Pop (Personal Trainer)",
        "recommended_modules": ["Jadwal Kelas & Sesi Latihan", "Booking 1-Day Free Trial Pass", "Katalog Paket Membership", "Profil Certified Coach", "WhatsApp Admin Gym"],
    },
}


def get_webia_pricing_table() -> List[Dict[str, Any]]:
    """Mengembalikan daftar 4 paket resmi WEBIA beserta harga dan fiturnya."""
    return WEBIA_PACKAGES


def recommend_webia_solution(
    category_slug: str,
    needs_cms: bool = False,
    needs_custom: bool = False,
    budget_range: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Logika rekomendasi solusi WEBIA berdasarkan Recommendation Matrix PRD §7.6:
    Menghasilkan rekomendasi Paket, Template Desain, dan Modul Unggulan.
    """
    cat_key = category_slug.lower().replace("-", "_")
    cat_meta = RECOMMENDATION_MATRIX.get(cat_key, RECOMMENDATION_MATRIX["fnb"])

    if needs_custom or budget_range == "high":
        pkg = WEBIA_PACKAGES[3]  # Infinity
        reason = f"Kebutuhan Anda mencakup alur bisnis kustom atau integrasi sistem tingkat lanjut untuk industri {cat_meta['category_name']}."
    elif needs_cms or cat_meta["entry_package"] == "Nexus":
        pkg = WEBIA_PACKAGES[2]  # Nexus
        reason = f"Paket Nexus memberikan Dashboard CMS mandiri sehingga Anda dapat memperbarui data {cat_meta['category_name']} kapan saja tanpa koding."
    elif budget_range == "low" or cat_meta["entry_package"] == "Pixel":
        pkg = WEBIA_PACKAGES[0]  # Pixel
        reason = f"Paket Pixel (Rp499.000) adalah opsi paling hemat untuk memulai kehadiran online bisnis {cat_meta['category_name']} Anda."
    else:
        pkg = WEBIA_PACKAGES[1]  # Pulse
        reason = f"Paket Pulse (Rp899.000) adalah pilihan ideal untuk landing page komprehensif, dilengkapi galeri, testimoni, FAQ, dan analitik SEO Google ready."

    return {
        "category": cat_meta["category_name"],
        "recommended_package": pkg["name"],
        "price": pkg["price_formatted"],
        "type": pkg["type"],
        "reason": reason,
        "recommended_template": cat_meta["template_name"],
        "recommended_modules": cat_meta["recommended_modules"],
        "upgrade_info": cat_meta["upgrade_trigger"],
        "action_url": "#paket-website",
        "cart_template_slug": cat_meta.get("template_slug", "little-corner"),
    }


def generate_business_brief(data: Dict[str, Any]) -> Dict[str, Any]:
    """Menyusun business brief terstruktur dari data yang dikumpulkan selama percakapan (Sprint L3-3)."""
    return BusinessBriefService.create_brief(data)


class L3IntentRouter:
    @classmethod
    def detect_and_route(cls, query: str) -> Dict[str, Any]:
        normalized = query.lower().strip()

        # 1. Cross-Service: Undangan Digital (D-Karsa)
        if any(w in normalized for w in ["nikah", "pernikahan", "undangan", "wedding", "manten", "resepsi"]) and not any(k in normalized for k in ["wedding organizer", "wedding planner", "wo", "organizer", "event organizer"]):
            return {
                "intent": "cross_service_dkarsa",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "index.html?site=dkarsa",
                "button_text": "Buka Layanan Undangan Digital D-Karsa (Mulai Rp50.000) 💌 →",
                "service_name": "Undangan Digital D-Karsa",
            }

        # 1b. Customer Account & Order Status Tracking (Webia Account System)
        if any(w in normalized for w in ["status pesanan", "cek pesanan", "order saya", "lacak pesanan", "dashboard saya", "progress web", "progres pembuatan"]):
            return {
                "intent": "customer_order_tracking",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "/dashboard",
                "button_text": "Buka Dashboard & Pesanan Saya →",
                "service_name": "Dashboard Pesanan Customer WEBIA",
            }

        # 1e. Tagihan & Perpanjangan Hosting (/hosting-invoices)
        if any(w in normalized for w in ["tagihan hosting", "invoice hosting", "bayar hosting", "perpanjang hosting", "perpanjangan hosting", "hosting suspend", "hosting disuspend", "hosting mati", "biaya hosting", "cek invoice hosting", "status hosting", "jatuh tempo hosting", "masa aktif hosting", "hosting expired", "hosting invoice"]):
            return {
                "intent": "hosting_invoice_inquiry",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "/hosting-invoices",
                "button_text": "Buka Tagihan & Faktur Hosting Saya →",
                "service_name": "Faktur & Tagihan Hosting WEBIA",
                "data": {
                    "portal_url": "/hosting-invoices",
                    "due_period": "7 hari kalender sejak faktur terbit",
                    "methods": ["QRIS (GoPay/ShopeePay)", "Virtual Account Bank (BCA, Mandiri, BRI, BNI)", "Kartu Kredit"],
                    "unsuspend_policy": "Otomatis pulih dan aktif kembali begitu invoice diselesaikan via Midtrans.",
                },
            }

        if any(w in normalized for w in ["login", "masuk akun", "daftar akun", "register", "bikin akun", "sign in", "sign up"]):
            return {
                "intent": "customer_auth",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "/login",
                "button_text": "Login Akun WEBIA (Order Baru via Guest Checkout) →",
                "service_name": "Akun Customer WEBIA (Guest Checkout Aktif)",
                "data": {
                    "login_url": "/login",
                    "guest_checkout_url": "/orders/create",
                    "note": "Pemesanan baru tidak perlu registrasi manual; akun dibuat otomatis dan dikirim via email setelah order.",
                },
            }

        # 1d. Add-on Services Resmi WEBIA
        if any(w in normalized for w in ["addon", "add-on", "fitur tambahan", "modul tambahan", "tambahan modul", "upgrade fitur"]):
            return {
                "intent": "addon_inquiry",
                "confidence": 0.95,
                "action": "inform",
                "target_url": "/orders/create",
                "button_text": "Pilih Add-on di Formulir Pemesanan →",
                "service_name": "4 Pilihan Add-on Resmi WEBIA",
                "data": {
                    "addons": WEBIA_ADDONS,
                },
            }

        # 1c. Checkout & Metode Pembayaran Midtrans
        if any(w in normalized for w in ["metode bayar", "metode pembayaran", "cara bayar", "bisa bayar pakai", "qris", "virtual account", "midtrans", "kartu kredit", "checkout pesanan"]):
            return {
                "intent": "payment_checkout_inquiry",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "/orders/create",
                "button_text": "Buka Formulir Checkout & Pembayaran Midtrans →",
                "service_name": "Pembayaran Otomatis WEBIA (Midtrans)",
                "data": {
                    "gateway": "Midtrans",
                    "methods": ["QRIS (GoPay, OVO, ShopeePay)", "Virtual Account Bank (BCA, Mandiri, BRI, BNI)", "Kartu Kredit", "Transfer Manual Bank"],
                    "verification": "Otomatis Real-Time (Status Langsung Paid)",
                    "next_step": "Isi data bisnis di Dashboard (/dashboard) setelah pembayaran berhasil",
                },
            }

        # 2. Business Brief Generator (Prioritas sebelum kategori umum)
        if any(w in normalized for w in ["brief", "business brief", "susun brief", "buatkan brief", "formulir kebutuhan", "briefing"]):
            return {
                "intent": "business_brief_request",
                "confidence": 0.95,
                "action": "brief",
                "target_url": HandoffService.get_whatsapp_url("Halo Tim Sales WEBIA, saya ingin konsultasi penyusunan Business Brief untuk website usaha saya."),
                "button_text": "Mulai Susun Business Brief ✍️",
                "service_name": "AI Business Brief Generator",
                "prompt_guide": "Beri tahu saya: 1) Nama bisnis, 2) Bidang usaha, 3) Fitur utama yang diinginkan, dan 4) Kontak WhatsApp Anda.",
                "plain_text_copy": (
                    "FORMAT PENGAJUAN BUSINESS BRIEF WEBIA:\n"
                    "- Nama Bisnis: \n"
                    "- Bidang/Kategori: \n"
                    "- Deskripsi Usaha: \n"
                    "- Target Pelanggan: \n"
                    "- Fitur yang Dibutuhkan: \n"
                    "- Lokasi/Kota: \n"
                    "- Nomor WhatsApp: "
                ),
            }

        # 3. Rekomendasi Spesifik Berdasarkan Kategori Industri (Recommendation Matrix PRD §7.6)
        if any(w in normalized for w in ["event organizer", "wedding organizer", "organizer acara", "organizer", "eventora", "wedding planner", "promotor konser", "gathering korporat"]) or re.search(r'\b(eo|wo)\b', normalized):
            return {
                "intent": "recommend_event_organizer_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Eventora (Wedding & Event Organizer) →",
                "service_name": "Solusi Website Event Organizer & Wedding Planner",
                "recommendation": {
                    "category": "Wedding & Event Organizer",
                    "category_symbol": "🎉",
                    "recommended_package": "Paket Pulse",
                    "recommended_template": "Eventora - Wedding & Event Organizer Bold Sunset Gradient",
                    "price": "Rp899.000",
                    "reason": "Paket Pulse memberikan landing page bold sunset gradient yang elegan untuk portofolio event, klien korporat, showcase konser, dan tombol WhatsApp booking.",
                    "cart_template_slug": "wedding-event-organizer-sunset-gradient",
                },
                "cart_template_slug": "wedding-event-organizer-sunset-gradient",
            }

        if any(w in normalized for w in ["alat pertanian", "mesin pertanian", "traktor", "peralatan tani", "alat semprot", "matchaagro", "frostyagro", "toko alat tani", "peralatan pertanian"]):
            return {
                "intent": "recommend_agro_machinery_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template MatchaAgro (Mesin & Alat Pertanian) →",
                "service_name": "Solusi Website Peralatan & Mesin Pertanian",
                "recommendation": {
                    "category": "Agriculture & Farming Equipment",
                    "category_symbol": "🌾",
                    "recommended_package": "Paket Nexus",
                    "recommended_template": "MatchaAgro Machinery - Creative Matcha Latte",
                    "price": "Rp1.499.000",
                    "reason": "Paket Nexus dilengkapi Dashboard CMS mandiri untuk katalog inventaris mesin tani, spesifikasi teknis traktor, dan pesanan suku cadang grosir.",
                    "cart_template_slug": "agriculture-peralatanpertanian-creative-matchalatte-putri",
                },
                "cart_template_slug": "agriculture-peralatanpertanian-creative-matchalatte-putri",
            }

        if any(w in normalized for w in ["ugc", "content creator studio", "ugc creator", "agensi kreator", "studio influencer", "ugc studio"]):
            return {
                "intent": "recommend_ugc_studio_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template UGC Content Creator Studio (Dark Mode) →",
                "service_name": "Solusi Website Studio UGC & Content Creator",
                "recommendation": {
                    "category": "Photography & Creative Studio",
                    "category_symbol": "📷",
                    "recommended_package": "Paket Pulse",
                    "recommended_template": "UGC Content Creator Studio - Futuristic Dark Mode",
                    "price": "Rp899.000",
                    "reason": "Paket Pulse dengan tampilan futuristik dark mode sangat cocok untuk agensi UGC, portofolio video reels/TikTok, rate card, dan booking kolaborasi brand.",
                    "cart_template_slug": "ugc-content-creator-studio-dark-mode",
                },
                "cart_template_slug": "ugc-content-creator-studio-dark-mode",
            }
        if (any(w in normalized for w in ["nonprofit", "non-profit", "yayasan", "komunitas", "relawan", "donasi", "charity", "filantropi", "panti asuhan", "organisasi sosial", "aksi sosial", "gerakan sosial", "baksos"]) or re.search(r'\bngo\b', normalized)) and not any(k in normalized for k in ["sekolah", "ppdb", "murid", "siswa", "preschool", "daycare"]):
            sol = recommend_webia_solution("nonprofit_community")
            return {
                "intent": "recommend_nonprofit_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template REVOLT // IMPACT (Non-Profit & Organisasi Sosial) →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "revolt-impact-social-organization"),
            }

        if any(w in normalized for w in ["foto produk", "peachy", "product photography", "katalog foto produk", "foto katalog"]):
            sol = recommend_webia_solution("photography_creative_studio")
            sol["recommended_template"] = "Peachy Studio — Product Photography"
            sol["cart_template_slug"] = "peachy-studio"
            return {
                "intent": "recommend_product_photography_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Peachy Studio (Product Photography) →",
                "service_name": "Solusi Website Foto Produk & Studio Kreatif",
                "recommendation": sol,
                "cart_template_slug": "peachy-studio",
            }


        if any(w in normalized for w in ["pindahan", "jasa pindahan", "moving", "moving company", "relokasi rumah", "pindahan kantor", "angkut barang pindahan", "hearth and haul", "hearth & haul", "atelier move"]):
            sol = recommend_webia_solution("transportation_logistics")
            sol["recommended_template"] = "Hearth & Haul / Atelier Move — Moving Company & Luxury Concierge"
            sol["cart_template_slug"] = "moving-company-navy-hearth"
            return {
                "intent": "recommend_moving_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Jasa Pindahan (Hearth & Haul) →",
                "service_name": "Solusi Website Jasa Pindahan & Relokasi",
                "recommendation": sol,
                "cart_template_slug": "moving-company-navy-hearth",
            }

        if any(w in normalized for w in ["kurir", "kurir kilat", "delivery service", "express delivery", "same day", "swiftly", "antar paket instan"]):
            sol = recommend_webia_solution("transportation_logistics")
            sol["recommended_template"] = "Swiftly — Delivery Service Modern Emerald Express"
            sol["cart_template_slug"] = "delivery-service-emerald-express"
            return {
                "intent": "recommend_express_delivery_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Swiftly (Express Delivery) →",
                "service_name": "Solusi Website Kurir & Delivery Service",
                "recommendation": sol,
                "cart_template_slug": "delivery-service-emerald-express",
            }

        if any(w in normalized for w in ["gym", "fitness", "angkat beban", "pilates", "personal trainer", "pt gym", "kebugaran", "pusat kebugaran", "workout", "senam", "ironpulse", "apex pulse", "strawberry fizz"]):
            sol = recommend_webia_solution("sports_fitness")
            return {
                "intent": "recommend_fitness_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template IRONPULSE (Gym & Fitness Center) →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "ironpulse-gym-fitness-center"),
            }

        if any(w in normalized for w in ["agribisnis", "agribusiness", "hasil bumi", "komoditas", "rempah", "ekspor kopi", "vanili", "green harvest", "bumi lestari"]):
            sol = recommend_webia_solution("agriculture_farming", needs_cms=True)
            sol["recommended_template"] = "Green Harvest — Corporate Agribisnis & Ekspor"
            sol["cart_template_slug"] = "agriculture-agribisnis-forest-moss"
            return {
                "intent": "recommend_b2b_agriculture_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Green Harvest (Agribisnis Ekspor) →",
                "service_name": "Solusi Website Agribisnis & Komoditas Ekspor",
                "recommendation": sol,
                "cart_template_slug": "agriculture-agribisnis-forest-moss",
            }

        if any(w in normalized for w in ["detailing", "auto detailing", "poles mobil", "ceramic coating", "graphene coating", "salon mobil", "paint protection", "bengkel otto", "samudra detailing", "aurum"]):
            sol = recommend_webia_solution("automotive")
            sol["recommended_template"] = "Bengkel Otto / Samudra Detailing / AURUM Auto Detailing"
            sol["cart_template_slug"] = "otto-artistic-workshop"
            return {
                "intent": "recommend_auto_detailing_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Bengkel Otto & Auto Detailing →",
                "service_name": "Solusi Website Auto Detailing & Bengkel Kustom",
                "recommendation": sol,
                "cart_template_slug": "otto-artistic-workshop",
            }

        if any(w in normalized for w in ["daycare", "preschool", "penitipan anak", "paud", "playgroup", "kelompok bermain", "anak usia dini"]):
            sol = recommend_webia_solution("education")
            sol["recommended_template"] = "Rumah Latte / Tunas Cendekia (Preschool & Daycare)"
            sol["cart_template_slug"] = "rumah-latte-preschool-daycare"
            return {
                "intent": "recommend_daycare_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Rumah Latte (Preschool & Daycare) →",
                "service_name": "Solusi Website Preschool & Daycare",
                "recommendation": sol,
                "cart_template_slug": "rumah-latte-preschool-daycare",
            }

        if any(w in normalized for w in ["sekolah", "akademi", "school", "academy", "yayasan sekolah", "ppdb", "sekolah swasta", "sd", "smp", "sma", "ruby academy"]):
            sol = recommend_webia_solution("education", needs_cms=True)
            sol["recommended_template"] = "Ruby Academy — School of Excellence"
            sol["cart_template_slug"] = "ruby-academy-classic-school"
            return {
                "intent": "recommend_school_website",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Ruby Academy (School of Excellence) →",
                "service_name": "Solusi Website Sekolah & Akademi",
                "recommendation": sol,
                "cart_template_slug": "ruby-academy-classic-school",
            }

        if any(w in normalized for w in ["logistik", "logistics", "ekspedisi", "cargo", "kargo", "pengiriman barang", "freight", "trucking", "truk", "kontainer", "armada kapal", "resi", "antar barang", "cek resi"]):
            sol = recommend_webia_solution("transportation_logistics")
            return {
                "intent": "recommend_logistics_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Transportation & Logistics (Classic Trust) →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "logistics-company-classic-trust"),
            }

        if any(w in normalized for w in ["fotografi", "fotografer", "studio foto", "photo studio", "pemotretan", "videografi", "dokumentasi foto"]):
            sol = recommend_webia_solution("personal_brand")
            sol["recommended_template"] = "Lumiere Photography Studio / Noir Studio Photography"
            sol["cart_template_slug"] = "lumiere-photography-studio"
            return {
                "intent": "recommend_photography_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Photography Studio (Lumiere / Noir) →",
                "service_name": "Solusi Website Fotografi & Studio Foto",
                "recommendation": sol,
                "cart_template_slug": "lumiere-photography-studio",
            }

        if any(w in normalized for w in ["psikolog", "konseling", "kesehatan mental", "terapi jiwa", "psikologi", "mental health", "konselor"]):
            sol = recommend_webia_solution("healthcare", needs_cms=True)
            sol["recommended_template"] = "Mitra Jiwa / Ruang Tenang Psikologi & Konseling"
            sol["cart_template_slug"] = "mitra-jiwa-psikologi-konseling"
            return {
                "intent": "recommend_psychology_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Psikologi & Konseling (Mitra Jiwa) →",
                "service_name": "Solusi Website Psikologi & Konseling",
                "recommendation": sol,
                "cart_template_slug": "mitra-jiwa-psikologi-konseling",
            }

        if any(w in normalized for w in ["travel", "tour", "wisata", "liburan", "open trip", "trip planner", "biro perjalanan", "paket tour", "jalan-jalan", "umrah", "haji", "ziarah"]):
            sol = recommend_webia_solution("travel_tourism")
            return {
                "intent": "recommend_travel_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Template Travel & Tourism (OceanJourney) →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "travel-agent-ocean-teal"),
            }

        if any(w in normalized for w in ["furniture", "furnitur", "mebel", "meubel", "kayu", "interior", "arsitektur", "joglo", "limasan"]):
            sol = recommend_webia_solution("interior_architecture")
            return {
                "intent": "recommend_furniture_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Template Furniture & Interior (WoodenLane) →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "furniture-mocha-cream"),
            }

        if any(w in normalized for w in ["software house", "software", "teknologi", "technology", "developer", "pembuatan aplikasi", "saas", "tech startup", "jasa koding", "hardware", "komputer", "networking", "jaringan"]):
            sol = recommend_webia_solution("technology_it", needs_cms=True)
            return {
                "intent": "recommend_technology_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Solusi Technology & Software House →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "technology-softwarehouse-elegant-babyblue-putri"),
            }

        if any(w in normalized for w in ["penulis", "author", "buku", "novelis", "sastra", "personal brand", "creator", "portofolio diri"]):
            sol = recommend_webia_solution("personal_brand")
            return {
                "intent": "recommend_personal_brand_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Personal Brand & Author (Arya Sanjaya / Creator) →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": "arya-sanjaya-ruby-editorial",
            }

        if any(w in normalized for w in ["fnb", "kuliner", "resto", "restoran", "cafe", "kafe", "kopi", "coffee", "catering", "katering", "bakery"]):
            sol = recommend_webia_solution("fnb")
            return {
                "intent": "recommend_fnb_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Template {sol['recommended_template'][:25]}... →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "little-corner"),
            }

        if any(w in normalized for w in ["beauty", "salon", "barber", "barbershop", "klinik kecantikan", "skincare", "mua", "spa", "nailart", "nail art"]):
            sol = recommend_webia_solution("beauty")
            return {
                "intent": "recommend_beauty_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Template Beauty & Salon →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "maison-beauty"),
            }

        if any(w in normalized for w in ["bengkel", "otomotif", "automotive", "car wash", "cuci mobil", "dealer", "motor", "detailing", "auto detailing", "coating", "cat mobil"]):
            sol = recommend_webia_solution("automotive")
            return {
                "intent": "recommend_automotive_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Template Bengkel & Otomotif →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "pitstop-garage"),
            }

        if any(w in normalized for w in ["company", "pt", "cv", "perusahaan", "kontraktor", "distributor", "pabrik", "manufaktur"]):
            sol = recommend_webia_solution("company", needs_cms=True)
            return {
                "intent": "recommend_company_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Solusi Company Profile (Nexus) →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
            }

        if any(w in normalized for w in ["petshop", "pet shop", "hewan", "kucing", "anjing", "grooming", "peliharaan"]):
            sol = recommend_webia_solution("pet_animal_service")
            return {
                "intent": "recommend_petshop_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Template Pet Shop & Animal Services →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "petshop-minimalist-glacierblue"),
            }

        if any(w in normalized for w in ["gigi", "dental", "dokter gigi", "orthodontic", "klinik gigi", "behel", "veneer"]):
            sol = recommend_webia_solution("healthcare", needs_cms=True)
            return {
                "intent": "recommend_dental_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Template Dental Clinic (Sunset / Azure) →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "healthcare-dental-sunset"),
            }

        if any(w in normalized for w in ["toko", "toko online", "retail", "jual baju", "olshop", "fashion", "baby shop", "baju anak", "perlengkapan bayi", "boutique"]):
            sol = recommend_webia_solution("retail", needs_cms=True)
            return {
                "intent": "recommend_retail_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Solusi Toko Retail & Etalase →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
            }

        if any(w in normalized for w in ["laundry", "cuci", "dry clean", "cuci baju", "kiloan", "sepatu", "setrika", "cleaning", "renovasi rumah", "home service"]):
            sol = recommend_webia_solution("home_services", needs_cms=False)
            return {
                "intent": "recommend_home_services_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Laundry & Home Services (Mint Fresh / Baby Blue) →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "laundry-mint-fresh"),
            }

        if any(w in normalized for w in ["peternakan", "ternak", "sapi", "kambing", "domba", "unggas", "ayam", "qurban", "agriternak", "agribisnis", "pertanian", "hidroponik", "iot kandang", "smart farm"]):
            sol = recommend_webia_solution("agriculture_farming", needs_cms=True)
            return {
                "intent": "recommend_agriculture_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": "Lihat Template Agriternak & Smart Farming →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "agriternak-bold-livestock"),
            }

        if any(w in normalized for w in ["edukasi", "education", "kursus", "bimbel", "sekolah", "les privat", "e-learning", "elearning", "bootcamp"]):
            sol = recommend_webia_solution("education", needs_cms=True)
            return {
                "intent": "recommend_education_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Solusi E-Learning & Bimbel →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "brightpath-academy"),
            }

        if any(w in normalized for w in ["properti", "property", "rumah", "real estate", "villa", "cluster"]):
            sol = recommend_webia_solution("property", needs_cms=True)
            return {
                "intent": "recommend_property_website",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#koleksi-template",
                "button_text": f"Lihat Solusi Properti & Real Estate →",
                "service_name": f"Solusi Website {sol['category']}",
                "recommendation": sol,
                "cart_template_slug": sol.get("cart_template_slug", "casa-verde"),
            }

        # 4. Paket & Harga Website Umum
        if any(w in normalized for w in ["paket", "harga", "biaya", "tarif", "berapa", "pixel", "pulse", "nexus", "infinity"]):
            return {
                "intent": "website_packages",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#paket-website",
                "button_text": "Lihat 4 Paket Website WEBIA (Mulai Rp499.000) →",
                "service_name": "Paket Website WEBIA",
            }

        # 5. Kategori Bisnis Umum & Galeri Template
        if any(w in normalized for w in ["kategori", "koleksi", "katalog", "template", "desain", "contoh", "portofolio", "galeri"]):
            return {
                "intent": "website_categories",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#kategori-website",
                "button_text": "Lihat Kategori Bisnis WEBIA →",
                "service_name": "Kategori Bisnis WEBIA",
            }

        # 6. Fitur Khusus (Chatbot AI, CMS, SEO)
        if any(w in normalized for w in ["chatbot", "ai", "seo", "google", "cms", "admin", "dashboard"]):
            return {
                "intent": "website_features",
                "confidence": 0.9,
                "action": "inform",
                "target_url": None,
                "button_text": None,
                "service_name": "Fitur Chatbot AI & CMS WEBIA",
            }

        # 7. WhatsApp Sales Consultation
        if any(w in normalized for w in ["whatsapp", "wa", "sales", "pesan", "order", "konsultasi", "admin", "cs"]):
            return {
                "intent": "sales_consultation",
                "confidence": 0.95,
                "action": "handoff",
                "target_url": HandoffService.get_whatsapp_url("Halo Tim Sales WEBIA, saya ingin konsultasi pembuatan website bisnis."),
                "button_text": "Konsultasi Sales via WhatsApp →",
                "service_name": "Tim Sales WEBIA",
            }

        return {
            "intent": "general_web_inquiry",
            "confidence": 0.7,
            "action": "clarify",
            "target_url": None,
            "button_text": None,
            "service_name": None,
            "clarification_question": "Apakah usaha Anda bergerak di bidang F&B, Beauty, Otomotif, Retail, Company Profile, atau bidang lainnya? Anda juga bisa ketik 'buat brief' untuk mulai merancang website.",
        }
