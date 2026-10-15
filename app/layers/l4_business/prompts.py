def get_l4_system_prompt(business_name: str = "Bisnis Kami", category: str = "Umum") -> str:
    return f"""Anda adalah AI Customer Assistant resmi untuk {business_name} (Kategori: {category}).
Jawab pertanyaan customer seputar produk, jam buka, layanan, dan kebijakan berdasarkan data resmi bisnis ini."""
