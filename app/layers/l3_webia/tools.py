from typing import Dict, Any, List, Optional
from app.services.handoff_service import HandoffService
from app.layers.l3_webia.brief_service import BusinessBriefService, BusinessBriefSchema


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
        "template_name": "Maison Beauty (Salon) / Blush Nail Studio (Nail Art) / Glow Society",
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
        "template_name": "Pitstop Garage (Bengkel & Auto Detailing)",
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
        "template_id": "BrightPath Academy / E-learna / EduPlus / NovaLearn",
        "template_slug": "brightpath-academy",
        "template_name": "BrightPath Academy (School) / E-learna (Bootcamp) / NovaLearn (Futuristic Dark)",
        "recommended_modules": ["Formulir Pendaftaran Siswa", "Jadwal Kelas & Biaya", "Profil Pengajar/Tutor", "Testimoni Alumni"],
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
        "template_name": "The Creator Room (Creator & Influencer Portfolio)",
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
        "template_name": "Urban Supply (Modern Store & Fashion)",
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
        "template_name": "Sunset Dental Care (Dental Clinic) / Azure Smile / Medika Care",
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
        "template_name": "PawMart (Pet Shop Minimalist) / Furry & Co. (Pet Boutique Luxury)",
        "recommended_modules": ["Katalog Makanan & Perlengkapan Hewan", "Online Booking Grooming", "Direct WhatsApp Order", "AI Nutrisi & Perawatan Hewan"],
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
        if any(w in normalized for w in ["nikah", "pernikahan", "undangan", "wedding", "manten", "resepsi"]):
            return {
                "intent": "cross_service_dkarsa",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "index.html?site=dkarsa",
                "button_text": "Buka Layanan Undangan Digital D-Karsa (Mulai Rp50.000) 💌 →",
                "service_name": "Undangan Digital D-Karsa",
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

        if any(w in normalized for w in ["bengkel", "otomotif", "automotive", "car wash", "cuci mobil", "dealer", "motor"]):
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

        if any(w in normalized for w in ["toko", "toko online", "retail", "jual baju", "olshop", "fashion"]):
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
                "button_text": "Lihat 10 Kategori Bisnis WEBIA →",
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
