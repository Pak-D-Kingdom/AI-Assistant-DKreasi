from typing import Dict, Any, List, Optional
from app.services.handoff_service import HandoffService


WEBIA_PACKAGES = [
    {
        "id": "pixel",
        "name": "Paket Pixel",
        "tagline": "01 / START SIMPLE",
        "price": 99500,
        "price_formatted": "Rp99.500",
        "original_price": "Rp589.500",
        "type": "TANPA CMS",
        "payment": "Sekali bayar",
        "description": "Tampil profesional di internet dengan landing page sederhana.",
        "features": [
            "1 Halaman landing page responsif",
            "WhatsApp order instan, kontak, dan Google Maps",
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
        "description": "Landing page lebih lengkap untuk memperkuat kehadiran digital brand.",
        "features": [
            "Landing page komprehensif satu halaman",
            "Galeri, testimoni klien, layanan, dan FAQ",
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
        "description": "Kelola konten, layanan, produk, dan artikel secara mandiri.",
        "features": [
            "Website beberapa halaman (multi-page)",
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
        "description": "Website fleksibel dengan CMS lanjutan dan fitur kustom sesuai kebutuhan bisnis.",
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
]


def get_webia_pricing_table() -> List[Dict[str, Any]]:
    """Mengembalikan daftar 4 paket resmi WEBIA beserta harga dan fiturnya."""
    return WEBIA_PACKAGES


def recommend_webia_package(
    needs_cms: bool = False,
    needs_custom_features: bool = False,
    has_large_catalog: bool = False,
) -> Dict[str, Any]:
    """Merekomendasikan paket WEBIA terbaik berdasarkan kebutuhan klien."""
    if needs_custom_features:
        pkg = WEBIA_PACKAGES[3]  # Infinity
        reason = "Anda membutuhkan fitur kustom khusus, CMS lanjutan, dan kapasitas AI Chatbot tertinggi."
    elif needs_cms or has_large_catalog:
        pkg = WEBIA_PACKAGES[2]  # Nexus
        reason = "Anda membutuhkan Dashboard CMS untuk mengelola halaman, produk, atau artikel secara mandiri."
    elif has_large_catalog is False and needs_cms is False:
        pkg = WEBIA_PACKAGES[1]  # Pulse
        reason = "Paket Pulse memberikan landing page lengkap dengan galeri, testimoni, FAQ, dan analitik SEO."
    else:
        pkg = WEBIA_PACKAGES[0]  # Pixel
        reason = "Paket Pixel paling hemat (Rp99.500) untuk landing page simpel profesional yang langsung closing ke WhatsApp."

    return {
        "recommended_package": pkg["name"],
        "price": pkg["price_formatted"],
        "type": pkg["type"],
        "reason": reason,
        "features": pkg["features"],
        "action_url": "#paket-website",
    }


class L3IntentRouter:
    @classmethod
    def detect_and_route(cls, query: str) -> Dict[str, Any]:
        normalized = query.lower().strip()

        # 1. Paket & Harga Website
        if any(w in normalized for w in ["paket", "harga", "biaya", "tarif", "berapa", "pixel", "pulse", "nexus", "infinity"]):
            return {
                "intent": "website_packages",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#paket-website",
                "button_text": "Lihat 4 Paket Website WEBIA (Mulai Rp99.500) →",
                "service_name": "Paket Website WEBIA",
            }

        # 2. 10 Kategori Bisnis & Katalog Desain
        if any(w in normalized for w in [
            "kategori", "koleksi", "katalog", "template", "desain", "contoh", "portofolio",
            "fnb", "kuliner", "resto", "cafe", "beauty", "salon", "barber", "otomotif", "bengkel",
            "company", "properti", "property", "edukasi", "sekolah", "kursus", "legal", "lawyer",
            "pajak", "creator", "retail", "toko", "klinik", "medis"
        ]):
            return {
                "intent": "website_categories",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#kategori-website",
                "button_text": "Lihat 10 Kategori Bisnis WEBIA →",
                "service_name": "Kategori Bisnis WEBIA",
            }

        # 3. Fitur Khusus (Chatbot AI, CMS, SEO)
        if any(w in normalized for w in ["chatbot", "ai", "seo", "google", "cms", "admin", "dashboard"]):
            return {
                "intent": "website_features",
                "confidence": 0.9,
                "action": "inform",
                "target_url": None,
                "button_text": None,
                "service_name": "Fitur Chatbot AI & CMS WEBIA",
            }

        # 4. WhatsApp Sales Consultation
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
            "clarification_question": "Apakah usaha Anda bergerak di bidang F&B, Beauty, Otomotif, Retail, Company Profile, atau bidang lainnya?",
        }
