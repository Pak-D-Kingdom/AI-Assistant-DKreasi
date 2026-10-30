from typing import Dict, Any, List, Optional
from app.services.handoff_service import HandoffService


DKARSA_PACKAGES = [
    {
        "id": "basic",
        "name": "Paket Basic",
        "price": 50000,
        "price_formatted": "Rp50.000",
        "original_price": "Rp110.000",
        "tier": "basic",
        "badge": "Desain Standar",
        "description": "Desain bersih, minimalis & esensial, paling hemat & ringan.",
        "max_guests": "Fleksibel (1 link)",
        "features": [
            "Bebas semua 6 bab kategori acara",
            "RSVP konfirmasi kehadiran & simpan kalender HP",
            "Integrasi navigasi Google Maps",
            "Hitung mundur acara (Countdown Timer)",
            "Galeri 2 foto & musik latar autoplay",
            "Aktif selamanya tanpa biaya bulanan",
        ],
    },
    {
        "id": "premium",
        "name": "Paket Premium",
        "price": 110000,
        "price_formatted": "Rp110.000",
        "original_price": "Rp250.000",
        "tier": "premium",
        "badge": "Desain Modern",
        "description": "Desain modern & elegan dengan transisi halus dan fitur amplop digital.",
        "max_guests": "Hingga 100 nama tamu personal",
        "features": [
            "Semua fitur Paket Basic",
            "Personalisasi nama tamu pada cover (hingga 100 tamu)",
            "Amplop digital (transfer bank langsung & scan QRIS)",
            "Buku tamu ucapan doa restu online real-time",
            "Galeri hingga 10 foto & cerita Love Story",
            "Bebas upload lagu MP3 pilihan sendiri",
            "Fitur kirim kado fisik via kurir",
            "Import daftar nama tamu dari Excel",
        ],
    },
    {
        "id": "eksklusif",
        "name": "Paket Eksklusif",
        "price": 180000,
        "price_formatted": "Rp180.000",
        "original_price": "Rp400.000",
        "tier": "eksklusif",
        "badge": "★ Rekomendasi (Best Seller)",
        "description": "Desain mewah 3D royal adat nusantara, tamu tanpa batas, dan siaran langsung.",
        "max_guests": "Tanpa Batas (Unlimited)",
        "features": [
            "Semua fitur Paket Premium",
            "Desain mewah 3D (animasi gunungan wayang 3D) & royal adat",
            "Link nama tamu TANPA BATAS (Unlimited Guests)",
            "Undangan 2 bahasa (Indonesia & Inggris)",
            "Sematkan Live Streaming YouTube / Instagram",
            "Galeri 20 foto & video sinematik teaser prewedding",
            "Bebas pilih seluruh koleksi tema katalog",
            "Prioritas pengerjaan Terima Beres",
            "Gratis gambar InstaStory / status WA pengumuman",
        ],
    },
    {
        "id": "kustom",
        "name": "Paket Kustom",
        "price": 280000,
        "price_formatted": "Rp280.000",
        "original_price": "Rp800.000",
        "tier": "kustom",
        "badge": "Full Request",
        "description": "Bisa request desain baru dari nol sesuai keinginan customer (1-on-1 dengan desainer).",
        "max_guests": "Tanpa Batas (Unlimited)",
        "features": [
            "Semua fitur Paket Eksklusif (All-In)",
            "Dibuatkan tema khusus dari nol sesuai request",
            "Konsultasi 1-on-1 langsung dengan desainer D'Karsa",
            "Sampul video sinematik + efek animasi partikel unik",
            "Gratis Custom Domain sendiri (contoh: bima-laras.com)",
            "Revisi fleksibel sampai customer puas",
            "QR Code check-in tamu resepsi & denah meja VIP",
            "Kamera tamu interaktif (disposable camera online)",
        ],
    },
]

DKARSA_CATEGORIES = [
    {
        "name": "Pernikahan",
        "icon": "💍",
        "default_sub": "Pernikahan adat Jawa, Sunda, Minang, dan lainnya",
        "recommended_theme": "theme-javanese-royal",
        "recommended_package": "eksklusif",
    },
    {
        "name": "Ulang Tahun",
        "icon": "🎂",
        "default_sub": "Sweet seventeen",
        "recommended_theme": "theme-golden-birthday",
        "recommended_package": "eksklusif",
    },
    {
        "name": "Aqiqah",
        "icon": "👶",
        "default_sub": "Aqiqah anak",
        "recommended_theme": "theme-little-prince",
        "recommended_package": "premium",
    },
    {
        "name": "Keagamaan",
        "icon": "🕌",
        "default_sub": "Halal bihalal",
        "recommended_theme": "theme-green-mosque",
        "recommended_package": "premium",
    },
    {
        "name": "Wisuda",
        "icon": "🎓",
        "default_sub": "Wisuda kuliah",
        "recommended_theme": "theme-golden-birthday",
        "recommended_package": "premium",
    },
    {
        "name": "Acara Formal",
        "icon": "🏛️",
        "default_sub": "Grand opening bisnis",
        "recommended_theme": "theme-snow-white",
        "recommended_package": "eksklusif",
    },
]

DKARSA_THEMES = [
    {
        "id": "theme-floral-wreath",
        "demo_url": "/demo/floral-wreath",
        "name": "Simple Minimalist Floral",
        "tier": "basic",
        "package_val": "Paket Basic - Rp50.000",
        "category": "Pernikahan",
    },
    {
        "id": "theme-rose-romance",
        "demo_url": "/demo/rose-romance",
        "name": "Elegant Rose Romance (ChungDoi Wildflower)",
        "tier": "premium",
        "package_val": "Paket Premium - Rp110.000",
        "category": "Pernikahan",
    },
    {
        "id": "theme-javanese-royal",
        "demo_url": "/demo/javanese-royal",
        "name": "3D Javanese Royal Keraton",
        "tier": "eksklusif",
        "package_val": "Paket Eksklusif - Rp180.000",
        "category": "Pernikahan",
    },
    {
        "id": "theme-batak-heritage",
        "demo_url": "/demo/batak-heritage",
        "name": "Batak Istimewa Heritage",
        "tier": "eksklusif",
        "package_val": "Paket Eksklusif - Rp180.000",
        "category": "Pernikahan",
    },
    {
        "id": "theme-green-mosque",
        "demo_url": "/demo/green-mosque",
        "name": "Green Mosque Harmony",
        "tier": "premium",
        "package_val": "Paket Premium - Rp110.000",
        "category": "Keagamaan",
    },
    {
        "id": "theme-snow-white",
        "demo_url": "/demo/snow-white",
        "name": "SnowFall Minimalist White",
        "tier": "eksklusif",
        "package_val": "Paket Eksklusif - Rp180.000",
        "category": "Pernikahan",
    },
    {
        "id": "theme-golden-birthday",
        "demo_url": "/demo/golden-birthday",
        "name": "Golden Luxury Birthday / Wisuda",
        "tier": "eksklusif",
        "package_val": "Paket Eksklusif - Rp180.000",
        "category": "Ulang Tahun",
    },
    {
        "id": "theme-little-prince",
        "demo_url": "/demo/little-prince",
        "name": "Little Prince Safari Khitan",
        "tier": "basic",
        "package_val": "Paket Basic - Rp50.000",
        "category": "Aqiqah",
    },
]


def calculate_guest_tier(guest_count: int) -> Dict[str, Any]:
    """
    Kalkulator Tamu & Rekomendasi Tier Otomatis D-Karsa:
    - 1 link umum / tanpa nama personal: Paket Basic (Rp50.000)
    - s.d 100 tamu personal: Paket Premium (Rp110.000)
    - > 100 tamu personal / ribuan: Paket Eksklusif (Rp180.000 - Unlimited)
    """
    if guest_count > 100:
        pkg = DKARSA_PACKAGES[2]  # Eksklusif
        reason = f"Untuk perkiraan {guest_count} tamu undangan, Anda WAJIB memilih **Paket Eksklusif (Rp180.000)** karena Paket Premium dibatasi maksimal 100 nama tamu. Paket Eksklusif memberikan tautan personalisasi nama tamu **TANPA BATAS (Unlimited Guests)**, live streaming, dan video teaser prewedding sinematik."
    elif guest_count > 1:
        pkg = DKARSA_PACKAGES[1]  # Premium
        reason = f"Untuk perkiraan {guest_count} tamu undangan, **Paket Premium (Rp110.000)** sangat ideal karena mencakup hingga 100 nama tamu personal pada cover, amplop digital QRIS/Bank, dan buku ucapan online."
    else:
        pkg = DKARSA_PACKAGES[0]  # Basic
        reason = "Untuk undangan santai atau acara keluarga hemat dengan 1 tautan umum tanpa personalisasi nama tamu per orang, **Paket Basic (Rp50.000)** adalah pilihan paling ekonomis."

    return {
        "guest_count": guest_count,
        "recommended_package": pkg["name"],
        "price": pkg["price_formatted"],
        "tier": pkg["tier"],
        "reason": reason,
        "features": pkg["features"],
    }


def get_builder_checklist() -> Dict[str, Any]:
    """
    Panduan Pengisian Data & Checklist Builder D-Karsa:
    Daftar data dan berkas yang perlu disiapkan pemesan sebelum mengisi form atau kirim ke desainer.
    """
    return {
        "title": "Checklist Persiapan Pembuatan Undangan D'Karsa",
        "steps": [
            {
                "step": 1,
                "name": "Data Acara Utama",
                "items": [
                    "Kategori & Judul Acara (Walimatul 'Ursy, Khitan, Aqiqah, dll.)",
                    "Hari, Tanggal, dan Waktu Acara (Akad & Resepsi)",
                    "Nama Gedung / Tempat & Alamat Lengkap",
                    "Tautan Titik Google Maps Presisi",
                ],
            },
            {
                "step": 2,
                "name": "Biodata Mempelai / Tokoh Acara",
                "items": [
                    "Nama Lengkap & Nama Panggilan Mempelai / Yang Dikhitan / Wisudawan",
                    "Nama Ayah & Ibu (beserta gelar jika diinginkan)",
                    "Urutan Anak (contoh: Putra Pertama, Putri Kedua)",
                    "Akun Instagram (opsional)",
                ],
            },
            {
                "step": 3,
                "name": "Media Galeri & Musik",
                "items": [
                    "Foto Cover Utama (resolusi tinggi)",
                    "Foto Mempelai Pria & Wanita / Tokoh Acara",
                    "2 s.d 20 Foto Galeri Prewedding / Momen Bahagia (sesuai paket)",
                    "Judul Lagu atau File MP3 Pilihan",
                ],
            },
            {
                "step": 4,
                "name": "Amplop Digital & Kado Fisik (Paket Premium ke atas)",
                "items": [
                    "Nama Bank & Nomor Rekening",
                    "Nama Lengkap Pemilik Rekening",
                    "Gambar QRIS (opsional)",
                    "Alamat Pengiriman Kado Fisik via Kurir",
                ],
            },
        ],
        "reminder": "Jika memilih Layanan Terima Beres, seluruh checklist di atas cukup dikirimkan sekaligus ke WhatsApp CS D'Karsa agar langsung ditata oleh tim desainer.",
    }


def get_dkarsa_pricing_table() -> List[Dict[str, Any]]:
    """Mengembalikan daftar 4 paket resmi D'Karsa beserta harga dan fiturnya."""
    return DKARSA_PACKAGES


def recommend_dkarsa_package(
    event_type: str = "pernikahan",
    estimated_guests: Optional[int] = None,
    needs_custom_design: bool = False,
    needs_live_streaming: bool = False,
) -> Dict[str, Any]:
    """Merekomendasikan paket D'Karsa terbaik berdasarkan kebutuhan klien."""
    if needs_custom_design:
        pkg = DKARSA_PACKAGES[3]  # Kustom
        reason = "Anda menginginkan desain kustom dari nol dengan konsultasi 1-on-1 dan custom domain."
    elif needs_live_streaming or (estimated_guests and estimated_guests > 100):
        pkg = DKARSA_PACKAGES[2]  # Eksklusif
        reason = "Anda membutuhkan fitur link tamu tanpa batas, live streaming, atau desain mewah 3D."
    elif estimated_guests and estimated_guests > 1:
        pkg = DKARSA_PACKAGES[1]  # Premium
        reason = "Paket Premium sangat pas untuk personalisasi nama tamu (s.d 100 tamu) dan amplop digital."
    else:
        pkg = DKARSA_PACKAGES[0]  # Basic
        reason = "Paket Basic paling hemat (Rp50.000) dengan fitur esensial lengkap dan aktif selamanya."

    return {
        "recommended_package": pkg["name"],
        "price": pkg["price_formatted"],
        "reason": reason,
        "features": pkg["features"],
        "action_url": "#harga",
    }


class L2IntentRouter:
    @classmethod
    def detect_and_route(cls, query: str) -> Dict[str, Any]:
        normalized = query.lower().strip()

        # 0. Checklist Persiapan / Syarat Data
        if any(w in normalized for w in ["checklist", "syarat data", "siapkan data", "apa saja yang disiapkan", "persiapan data", "berkas undangan", "data apa saja"]):
            return {
                "intent": "builder_checklist",
                "confidence": 0.95,
                "action": "inform",
                "target_url": None,
                "button_text": None,
                "service_name": "Checklist Persiapan Undangan D'Karsa",
                "data": get_builder_checklist(),
            }

        # 0b. Kalkulator Tamu Otomatis (Ekstraksi Angka Tamu)
        import re
        guest_match = re.search(r"(\d+)\s*(tamu|orang|undangan|keluarga)", normalized)
        if guest_match and any(w in normalized for w in ["tamu", "orang", "undangan", "kapasitas", "rekomendasi paket", "paket apa"]):
            count = int(guest_match.group(1))
            rec = calculate_guest_tier(count)
            return {
                "intent": "guest_calculator",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#harga",
                "button_text": f"Lihat {rec['recommended_package']} ({rec['price']}) →",
                "service_name": f"Kalkulator Tamu ({count} Tamu)",
                "calculation": rec,
            }

        # 0d. Online Builder Mandiri (/buat-undangan)
        if any(w in normalized for w in ["buat sendiri", "bikin sendiri", "susun sendiri", "builder", "buat undangan online", "form online", "isi data sendiri"]):
            return {
                "intent": "online_builder",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "/buat-undangan",
                "button_text": "Buka Online Builder Undangan D'Karsa →",
                "service_name": "Online Builder Mandiri D'Karsa",
                "data": {
                    "url": "/buat-undangan",
                    "features": ["Isi data mempelai & acara", "Upload galeri foto", "Pilih musik latar MP3", "Live Preview instan"],
                },
            }

        # 0e. Fitur RSVP & Buku Tamu Online
        if any(w in normalized for w in ["rsvp", "buku tamu", "ucapan doa", "doa restu", "konfirmasi kehadiran"]):
            return {
                "intent": "rsvp_wish_feature",
                "confidence": 0.95,
                "action": "inform",
                "target_url": "#fitur",
                "button_text": "Lihat Fitur Interaktif D'Karsa →",
                "service_name": "Fitur RSVP & Buku Tamu Real-Time",
                "data": {
                    "rsvp": "Tamu bisa konfirmasi hadir/tidak hadir beserta jumlah tamu yang dibawa.",
                    "wish_wall": "Tamu bisa mengirimkan doa restu yang langsung tayang interaktif pada buku tamu online.",
                },
            }

        # 0c. Metode Pembayaran & Verifikasi Midtrans
        if any(w in normalized for w in ["metode bayar", "metode pembayaran", "cara bayar", "bisa bayar pakai", "qris", "transfer bank", "virtual account", "midtrans", "kartu kredit", "va bca"]):
            return {
                "intent": "payment_inquiry",
                "confidence": 0.98,
                "action": "navigate",
                "target_url": "#harga",
                "button_text": "Lihat Pilihan Paket & Metode Pembayaran Midtrans →",
                "service_name": "Metode Pembayaran Resmi D'Karsa (Midtrans)",
                "data": {
                    "gateway": "Midtrans",
                    "methods": ["QRIS (GoPay, ShopeePay, OVO)", "Virtual Account (BCA, Mandiri, BRI, BNI)", "Kartu Kredit / Debit"],
                    "verification": "Otomatis Real-Time (Aktif Instan)",
                },
            }

        # 1. Custom / Request Khusus -> Handoff WA
        if any(w in normalized for w in ["custom", "kustom", "request khusus", "desain sendiri", "dari nol", "pinterest"]):
            return {
                "intent": "custom_design_request",
                "confidence": 0.95,
                "action": "handoff",
                "target_url": HandoffService.get_whatsapp_url("Halo Admin D'Karsa, saya tertarik dengan Paket Kustom (Rp280.000). Saya ingin konsultasi desain undangan kustom dari nol."),
                "button_text": "Konsultasi Paket Kustom via WhatsApp →",
                "service_name": "Paket Kustom D'Karsa",
            }

        # 2. Tema Spesifik -> Handoff WhatsApp / Katalog
        if "jawa" in normalized or "gunungan" in normalized or "wayang" in normalized:
            return {
                "intent": "wedding_javanese_royal",
                "confidence": 0.95,
                "action": "handoff",
                "target_url": HandoffService.get_whatsapp_url("Halo CS D'Karsa, saya tertarik memesan undangan tema 3D Javanese Royal Keraton (Paket Eksklusif - Rp180.000)."),
                "button_text": "Pesan Tema 3D Javanese Royal via WhatsApp →",
                "service_name": "Tema 3D Javanese Royal (Eksklusif - Rp180.000)",
            }

        if "batak" in normalized or "ulos" in normalized or "gorga" in normalized:
            return {
                "intent": "wedding_batak_heritage",
                "confidence": 0.95,
                "action": "handoff",
                "target_url": HandoffService.get_whatsapp_url("Halo CS D'Karsa, saya tertarik memesan undangan tema Batak Istimewa Heritage (Paket Eksklusif - Rp180.000)."),
                "button_text": "Pesan Tema Batak Heritage via WhatsApp →",
                "service_name": "Tema Batak Istimewa Heritage (Eksklusif - Rp180.000)",
            }

        if "rose romance" in normalized or "wildflower" in normalized or "chungdoi" in normalized:
            return {
                "intent": "wedding_rose_romance",
                "confidence": 0.95,
                "action": "handoff",
                "target_url": HandoffService.get_whatsapp_url("Halo CS D'Karsa, saya tertarik memesan undangan tema Elegant Rose Romance (Paket Premium - Rp110.000)."),
                "button_text": "Pesan Tema Rose Romance via WhatsApp →",
                "service_name": "Tema Elegant Rose Romance (Premium - Rp110.000)",
            }

        if "snowfall" in normalized or "snow white" in normalized or "salju" in normalized:
            return {
                "intent": "wedding_snow_white",
                "confidence": 0.95,
                "action": "handoff",
                "target_url": HandoffService.get_whatsapp_url("Halo CS D'Karsa, saya tertarik memesan undangan tema SnowFall Minimalist White (Paket Eksklusif - Rp180.000)."),
                "button_text": "Pesan Tema SnowFall White via WhatsApp →",
                "service_name": "Tema SnowFall Minimalist White (Eksklusif - Rp180.000)",
            }

        # 3. Kategori Bab Acara -> Katalog Desain / Konsultasi
        if any(w in normalized for w in ["nikah", "pernikahan", "wedding", "akad", "resepsi"]):
            return {
                "intent": "wedding_invitation",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#desain",
                "button_text": "Lihat Katalog Undangan Pernikahan →",
                "service_name": "Undangan Pernikahan D'Karsa",
            }

        if any(w in normalized for w in ["ulang tahun", "ultah", "birthday", "sweet 17", "sweet seventeen", "milad"]):
            return {
                "intent": "birthday_invitation",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#desain",
                "button_text": "Lihat Tema Ulang Tahun & Sweet 17 →",
                "service_name": "Undangan Ulang Tahun D'Karsa",
            }

        if any(w in normalized for w in ["khitan", "khitanan", "sunat", "sunatan", "walimatul khitan"]):
            return {
                "intent": "khitanan_invitation",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#desain",
                "button_text": "Lihat Tema Walimatul Khitan →",
                "service_name": "Undangan Walimatul Khitan D'Karsa",
            }

        if any(w in normalized for w in ["aqiqah", "akikah", "kelahiran", "tasmiyah", "bayi"]):
            return {
                "intent": "aqiqah_invitation",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#desain",
                "button_text": "Lihat Tema Aqiqah & Tasmiyah →",
                "service_name": "Undangan Aqiqah D'Karsa",
            }

        if any(w in normalized for w in ["wisuda", "kelulusan", "sarjana"]):
            return {
                "intent": "wisuda_invitation",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#desain",
                "button_text": "Lihat Tema Wisuda & Kelulusan →",
                "service_name": "Undangan Wisuda D'Karsa",
            }

        if any(w in normalized for w in ["formal", "seminar", "workshop", "gathering", "grand opening"]):
            return {
                "intent": "formal_invitation",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#desain",
                "button_text": "Lihat Tema Acara Formal & Bisnis →",
                "service_name": "Undangan Acara Formal D'Karsa",
            }

        if any(w in normalized for w in ["halal bihalal", "halalbihalal", "lebaran", "idul fitri", "silaturahmi", "tahlilan", "tahlil", "haul", "syukuran"]):
            return {
                "intent": "keagamaan_invitation",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#desain",
                "button_text": "Lihat Tema Keagamaan & Silaturahmi →",
                "service_name": "Undangan Keagamaan D'Karsa",
            }

        # 4. Harga / Biaya / Paket
        if any(w in normalized for w in ["harga", "biaya", "tarif", "paket", "berapa", "promo", "murah"]):
            return {
                "intent": "guest_calculator",
                "confidence": 0.95,
                "action": "navigate",
                "target_url": "#harga",
                "button_text": "Hitung Estimasi Paket & Tamu Live ⚡ →",
                "service_name": "Kalkulator Paket & Tamu D'Karsa",
                "calculation": calculate_guest_tier(150),
            }

        # 5. WhatsApp CS / Pemesanan Langsung
        if any(w in normalized for w in ["whatsapp", "wa", "cs", "admin", "kontak", "hubungi", "telepon", "pesan", "order", "bikin", "buat"]):
            return {
                "intent": "order_consultation",
                "confidence": 0.95,
                "action": "handoff",
                "target_url": HandoffService.get_whatsapp_url("Halo CS D'Karsa, saya ingin memesan / konsultasi undangan digital."),
                "button_text": "Hubungi CS Pemesanan via WhatsApp →",
                "service_name": "Customer Service D'Karsa",
            }

        return {
            "intent": "general_inquiry",
            "confidence": 0.7,
            "action": "clarify",
            "target_url": None,
            "button_text": None,
            "service_name": None,
            "clarification_question": "Apakah Anda sedang mempersiapkan undangan Pernikahan, Ulang Tahun, Aqiqah, Keagamaan, Wisuda, atau Acara Formal?",
        }
