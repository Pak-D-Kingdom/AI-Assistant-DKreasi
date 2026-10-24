/**
 * Universal PakDe AI Widget (Multi-Tier: D-KREASI, WEBIA, D-KARSA, L4 Tenant)
 * Automatically adapts title, persona, theme styling, and suggestion chips
 * based on data-site-key or data-layer.
 *
 * v2 - Perbaikan multi-tenant:
 *  - Sesi & riwayat chat terikat ke tenant (ganti tenant = chat mulai ulang)
 *  - Request yang masih berjalan dibatalkan saat tenant diganti
 *  - Nomor WhatsApp dinamis per tenant (tidak lagi hardcoded untuk L4)
 *  - Proteksi XSS pada URL/teks dari server
 *  - Riwayat dibatasi & dibersihkan saat error
 *
 * API publik:
 *   window.PakdeAI.setTenant('tenant_id', { name: 'Nama Bisnis', whatsapp: '0812...' })
 *   window.PakdeAI.reset()
 *   window.__PAKDE_TENANT_ID = 'tenant_id'   // otomatis memicu reset bila nilainya berubah
 */
(() => {
    'use strict';

    // ------------------------------------------------------------------
    // Konstanta & util
    // ------------------------------------------------------------------
    const MAX_HISTORY = 10; // jumlah pesan terakhir yang dikirim ke backend
    const DEFAULT_WA_URL = 'https://wa.me/6281234567890';

    const esc = (s) => String(s ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');

    const safeUrl = (url) => (/^https?:\/\//i.test(String(url || '').trim()) ? String(url).trim() : '');

    const toWaUrl = (number) => {
        if (!number) return '';
        const raw = String(number).trim();
        if (/^https?:\/\//i.test(raw)) return safeUrl(raw);
        let digits = raw.replace(/\D/g, '');
        if (!digits) return '';
        if (digits.startsWith('0')) digits = '62' + digits.slice(1);
        return `https://wa.me/${digits}`;
    };

    // ------------------------------------------------------------------
    // Locate script tag & endpoint
    // ------------------------------------------------------------------
    const currentScript = document.currentScript || Array.from(document.querySelectorAll('script')).find(s => s.src.includes('widget.js'));
    const siteKey = currentScript?.dataset?.siteKey || 'site_dkreasi_public';
    const layerParam = currentScript?.dataset?.layer;
    const baseUrl = (currentScript?.dataset?.apiUrl || window.location.origin || 'http://localhost:8001').replace(/\/$/, '');
    const chatEndpoint = `${baseUrl}/api/v1/chat`;

    // ------------------------------------------------------------------
    // Multi-Tier Configuration Catalog
    // ------------------------------------------------------------------
    const CLIENT_ICON_LAUNCHER = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;
    const CLIENT_ICON_AVATAR = `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;

    const CONFIGS = {
        'site_dkreasi_public': {
            theme: 'dkreasi',
            layer: 'l1',
            title: 'D-KREASI Assistant',
            subtitle: 'Online · Front-Desk PakDe Group',
            eyebrow: '✦ PAKDE GROUP AI CONCIERGE',
            launcherLabel: 'Tanya D-KREASI AI',
            launcherIcon: '✦',
            avatarIcon: '✦',
            welcomeTitle: 'Halo! Butuh solusi kreasi digital? ✨',
            welcomeDesc: 'Saya siap memandu Anda menemukan layanan terbaik dari PakDe Group: mulai dari Website Bisnis (WEBIA) hingga Undangan Digital.',
            initialMsg: 'Halo! Ada yang bisa saya bantu hari ini? Anda sedang mencari solusi Website Bisnis, Undangan Digital, atau ingin berkonsultasi seputar layanan kami?',
            chips: [
                { label: '💻 Buat Website Bisnis', prompt: 'Saya butuh website untuk mengembangkan usaha bisnis saya.' },
                { label: '💌 Undangan Digital', prompt: 'Bisa bantu buat undangan pernikahan digital?' },
                { label: '✦ Layanan D-KREASI', prompt: 'Apa saja layanan yang tersedia di D-KREASI?' },
                { label: '💬 Hubungi CS WhatsApp', prompt: 'Saya ingin berbicara dengan customer service WhatsApp.' }
            ],
            footer: 'D-KREASI AI Assistant · Solusi Digital Kreatif by PakDe Group'
        },
        'site_webia_public': {
            theme: 'webia',
            layer: 'l3',
            title: 'WEBIA Assistant',
            subtitle: 'Online · Asisten Digital WEBIA',
            eyebrow: 'WELCOME TO WEBIA',
            launcherLabel: 'AI Assistant',
            launcherIcon: '✦',
            avatarIcon: '✦',
            welcomeTitle: 'Hai! Mau bikin website impianmu? ✨',
            welcomeDesc: 'Aku siap membantumu menjelajahi layanan WEBIA. Pilih topik di bawah atau tulis pertanyaanmu.',
            initialMsg: 'Halo! Kamu sedang mencari website untuk bisnis, ingin melihat paket layanan, atau butuh bantuan menentukan jenis website yang cocok?',
            chips: [
                { label: '💻 4 Paket Website', prompt: 'Berapa daftar 4 paket dan harga resmi website di WEBIA?' },
                { label: '📝 Buat Business Brief', prompt: 'Bantu saya susun business brief untuk website usaha saya.' },
                { label: '✨ 10 Kategori Bisnis', prompt: 'Kategori bisnis apa saja yang didukung oleh WEBIA?' },
                { label: '💬 Chat Sales WhatsApp', prompt: 'Bisa hubungkan saya dengan tim sales WEBIA via WhatsApp?' }
            ],
            footer: 'WEBIA Assistant · Sales AI by PakDe Group'
        },
        'site_dkarsa_public': {
            theme: 'dkarsa',
            layer: 'l2',
            title: "Tanya D'Karsa",
            subtitle: 'Online · Konsultan Undangan Digital',
            eyebrow: "D'KARSA WEDDING & INVITATION",
            launcherLabel: "Tanya D'Karsa",
            launcherIcon: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path><path d="M12 7l.8 1.8 1.8.8-1.8.8-.8 1.8-.8-1.8-1.8-.8 1.8-.8.8-1.8z" fill="currentColor" stroke="none"></path></svg>`,
            avatarIcon: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path><path d="M12 7l.8 1.8 1.8.8-1.8.8-.8 1.8-.8-1.8-1.8-.8 1.8-.8.8-1.8z" fill="currentColor" stroke="none"></path></svg>`,
            welcomeTitle: 'Mulai rancang hari bahagia kalian ✨',
            welcomeDesc: 'Pilih desain favorit, konsultasikan kebutuhan acara spesial secara gratis, dan dapatkan rekomendasi terbaik.',
            initialMsg: "Halo! Selamat datang di Tanya D'Karsa. Sedang merencanakan undangan Pernikahan, Halal Bihalal, Khitanan, Aqiqah, Ulang Tahun, atau Syukuran? Aku siap bantu info paket & rekomendasinya!",
            chips: [
                { label: '💍 Paket & Harga (Mulai 50rb)', prompt: 'Berapa daftar paket dan harga resmi undangan digital di D-Karsa?' },
                { label: '🌸 Katalog Tema Desain', prompt: 'Bisa rekomendasikan pilihan tema desain undangan yang tersedia?' },
                { label: '🕌 Khitan, Aqiqah & Syukuran', prompt: 'Apa saja pilihan undangan untuk Halal Bihalal, Khitanan, Aqiqah, atau Syukuran?' },
                { label: '✨ Request Desain Kustom', prompt: 'Bagaimana cara request desain kustom dari nol di Paket Kustom (Rp280.000)?' }
            ],
            footer: "Tanya D'Karsa · Konsultan Undangan Digital by PakDe Group"
        },
        'site_webia_tenant_public': {
            theme: 'client',
            layer: 'l4',
            title: 'Asisten Bisnis Tenant',
            subtitle: 'Online · AI Customer Support Resmi',
            eyebrow: 'AI BUSINESS CHATBOT · TIER L4',
            launcherLabel: 'Tanya CS Bisnis',
            launcherIcon: CLIENT_ICON_LAUNCHER,
            avatarIcon: CLIENT_ICON_AVATAR,
            welcomeTitle: 'Selamat Datang di Bisnis Kami! ✨',
            welcomeDesc: 'Saya adalah asisten AI resmi yang siap menjawab pertanyaan seputar produk, jam buka, layanan, dan promo kami.',
            initialMsg: 'Halo! Ada yang bisa saya bantu terkait produk, reservasi, atau layanan kami hari ini?',
            chips: [
                { label: '⏰ Jam Buka & Lokasi', prompt: 'Buka jam berapa dan di mana alamat lokasi bisnis ini?' },
                { label: '📋 Layanan & Harga', prompt: 'Apa saja layanan atau produk yang tersedia beserta harganya?' },
                { label: '🏷️ Promo & Diskon Aktif', prompt: 'Apakah sedang ada promo atau diskon yang berlaku saat ini?' },
                { label: '💬 Hubungi WhatsApp CS', prompt: 'Bisa hubungkan saya dengan WhatsApp atau customer service resmi?' }
            ],
            footer: 'AI Business Chatbot · Powered by WEBIA Ekosistem PakDe Group'
        }
    };
    // Alias (sebelumnya duplikat penuh)
    CONFIGS['site_client_webia_public'] = CONFIGS['site_webia_tenant_public'];

    // Determine active profile
    let activeConfig = CONFIGS[siteKey] || CONFIGS['site_dkreasi_public'];
    if (layerParam === 'l2' || siteKey.includes('dkarsa')) activeConfig = CONFIGS['site_dkarsa_public'];
    if (layerParam === 'l3' || siteKey === 'site_webia_public') activeConfig = CONFIGS['site_webia_public'];
    if (layerParam === 'l4' || siteKey.includes('tenant') || siteKey.includes('client')) activeConfig = CONFIGS['site_webia_tenant_public'];

    const isTenantLayer = activeConfig.layer === 'l4';

    // Inject CSS
    if (!document.querySelector('link[href*="widget.css"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = `${baseUrl}/widget/widget.css`;
        document.head.appendChild(link);
    }

    // ------------------------------------------------------------------
    // State: tenant, sesi, riwayat
    // ------------------------------------------------------------------
    let tenantId = window.__PAKDE_TENANT_ID ? String(window.__PAKDE_TENANT_ID) : '';
    let tenantMeta = {};              // { name, whatsapp }
    let history = [];                 // riwayat percakapan (dikosongkan saat ganti tenant)
    let requestCounter = 0;           // penanda request aktif
    let abortController = null;       // untuk membatalkan request yang sedang jalan

    const sessionKeyFor = (tid) => `pakde_ai_session_${activeConfig.layer}_${tid || 'default'}`;
    const newSessionId = () => `sess_${activeConfig.layer}_` + (
        (window.crypto && crypto.randomUUID)
            ? crypto.randomUUID().replace(/-/g, '').slice(0, 12)
            : Math.random().toString(36).substring(2, 14)
    );

    const loadOrCreateSession = (tid) => {
        let id = null;
        try { id = sessionStorage.getItem(sessionKeyFor(tid)); } catch (e) {}
        if (!id) {
            id = newSessionId();
            try { sessionStorage.setItem(sessionKeyFor(tid), id); } catch (e) {}
        }
        return id;
    };

    let sessionId = loadOrCreateSession(tenantId);

    // ------------------------------------------------------------------
    // Render widget
    // ------------------------------------------------------------------
    const chipsHtml = activeConfig.chips.map(c =>
        `<button type="button" class="pakde-ai-chip" data-prompt="${esc(c.prompt)}">${esc(c.label)}</button>`
    ).join('');

    // Tombol CS: untuk layer tenant (L4) nomor harus berasal dari tenant, bukan hardcoded.
    const initialWaHref = isTenantLayer ? '' : DEFAULT_WA_URL;

    const container = document.createElement('div');
    container.className = `pakde-ai-widget pakde-ai-theme--${activeConfig.theme}`;
    container.id = 'pakde-ai-root';
    container.innerHTML = `
        <button class="pakde-ai-launcher pakde-ai-launcher--${activeConfig.theme}" id="pakde-ai-launcher" aria-label="Buka AI Assistant">
            <span class="pakde-ai-icon">${activeConfig.launcherIcon}</span>
            <span class="pakde-ai-label">${activeConfig.launcherLabel}</span>
            <span class="pakde-ai-pulse"></span>
        </button>

        <section class="pakde-ai-panel pakde-ai-panel--${activeConfig.theme}" id="pakde-ai-panel" role="dialog" aria-hidden="true" inert>
            <header class="pakde-ai-header">
                <div class="pakde-ai-identity">
                    <div class="pakde-ai-avatar">${activeConfig.avatarIcon}</div>
                    <div>
                        <h2 id="pakde-ai-title">${activeConfig.title}</h2>
                        <p><span class="pakde-ai-dot"></span> ${activeConfig.subtitle}</p>
                    </div>
                </div>
                <div class="pakde-ai-header-actions">
                    <a href="${initialWaHref || '#'}" target="_blank" rel="noopener noreferrer" class="pakde-ai-wa-btn" id="pakde-ai-header-wa" ${initialWaHref ? '' : 'style="display:none"'}>
                        💬 CS
                    </a>
                    <button class="pakde-ai-close" id="pakde-ai-close" aria-label="Tutup">×</button>
                </div>
            </header>

            <div class="pakde-ai-messages" id="pakde-ai-messages">
                <div class="pakde-ai-welcome">
                    <span class="pakde-ai-eyebrow">${activeConfig.eyebrow}</span>
                    <h3 id="pakde-ai-welcome-title">${activeConfig.welcomeTitle}</h3>
                    <p>${activeConfig.welcomeDesc}</p>
                </div>

                <div class="pakde-ai-msg-group pakde-ai-msg-group--assistant" id="pakde-ai-initial">
                    <div class="pakde-ai-bubble">${activeConfig.initialMsg}</div>
                </div>

                <div class="pakde-ai-chips" id="pakde-ai-chips">
                    ${chipsHtml}
                </div>

                <div class="pakde-ai-typing" id="pakde-ai-typing" style="display: none;">
                    <div class="pakde-ai-typing-bubble">
                        <span class="pakde-ai-typing-dot"></span>
                        <span class="pakde-ai-typing-dot"></span>
                        <span class="pakde-ai-typing-dot"></span>
                    </div>
                </div>
            </div>

            <form class="pakde-ai-form" id="pakde-ai-form">
                <textarea id="pakde-ai-input" rows="1" placeholder="Tulis pesan Anda di sini..." autocomplete="off"></textarea>
                <button type="submit" id="pakde-ai-send" disabled aria-label="Kirim">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5">
                        <line x1="12" y1="19" x2="12" y2="5"></line>
                        <polyline points="5 12 12 5 19 12"></polyline>
                    </svg>
                </button>
            </form>

            <footer class="pakde-ai-footer">
                ${activeConfig.footer}
            </footer>
        </section>
    `;
    document.body.appendChild(container);

    const launcher = container.querySelector('#pakde-ai-launcher');
    const panel = container.querySelector('#pakde-ai-panel');
    const closeBtn = container.querySelector('#pakde-ai-close');
    const messages = container.querySelector('#pakde-ai-messages');
    const form = container.querySelector('#pakde-ai-form');
    const input = container.querySelector('#pakde-ai-input');
    const sendBtn = container.querySelector('#pakde-ai-send');
    const typing = container.querySelector('#pakde-ai-typing');
    const chipsContainer = container.querySelector('#pakde-ai-chips');
    const waBtn = container.querySelector('#pakde-ai-header-wa');
    const welcomeTitleEl = container.querySelector('#pakde-ai-welcome-title');

    // ------------------------------------------------------------------
    // UI tenant: WhatsApp & sambutan
    // ------------------------------------------------------------------
    const setWhatsApp = (value) => {
        const url = toWaUrl(value);
        if (!url) return false;
        waBtn.href = url;
        waBtn.style.display = '';
        tenantMeta.whatsappUrl = url;
        return true;
    };

    const applyTenantUi = () => {
        if (!isTenantLayer) return;

        // Sambutan personal bila nama tenant diketahui
        welcomeTitleEl.textContent = tenantMeta.name
            ? `Selamat Datang di ${tenantMeta.name}! ✨`
            : activeConfig.welcomeTitle;

        // WhatsApp: pakai milik tenant, sembunyikan bila belum diketahui
        if (tenantMeta.whatsappUrl) {
            waBtn.href = tenantMeta.whatsappUrl;
            waBtn.style.display = '';
        } else {
            waBtn.href = '#';
            waBtn.style.display = 'none';
        }
    };

    // ------------------------------------------------------------------
    // Reset chat penuh (dipanggil saat ganti tenant)
    // ------------------------------------------------------------------
    const resetChat = () => {
        // 1. Batalkan request yang masih berjalan agar jawaban lama tidak masuk ke chat baru
        requestCounter++;
        if (abortController) {
            try { abortController.abort(); } catch (e) {}
            abortController = null;
        }

        // 2. Sesi baru untuk tenant ini + kosongkan riwayat
        sessionId = newSessionId();
        try { sessionStorage.setItem(sessionKeyFor(tenantId), sessionId); } catch (e) {}
        history = [];

        // 3. Bersihkan UI: hapus semua bubble & kartu kecuali pesan pembuka
        messages.querySelectorAll('.pakde-ai-msg-group, .pakde-ai-action-card').forEach(el => {
            if (el.id !== 'pakde-ai-initial') el.remove();
        });

        // 4. Tampilkan chips lagi, reset input & typing
        if (chipsContainer) chipsContainer.style.display = '';
        typing.style.display = 'none';
        input.value = '';
        input.style.height = 'auto';
        sendBtn.disabled = true;
        messages.scrollTop = 0;

        // 5. Perbarui sambutan & WhatsApp sesuai tenant
        applyTenantUi();
    };

    // Deteksi otomatis: setiap kali halaman mengubah window.__PAKDE_TENANT_ID
    // (misal dari dropdown), chat langsung dimulai ulang.
    try {
        Object.defineProperty(window, '__PAKDE_TENANT_ID', {
            configurable: true,
            enumerable: true,
            get: () => tenantId,
            set: (val) => {
                const next = val ? String(val) : '';
                if (next === tenantId) return;
                tenantId = next;
                tenantMeta = {}; // metadata tenant lama tidak boleh terbawa
                resetChat();
            }
        });
    } catch (e) { /* abaikan bila browser menolak */ }

    // API publik
    window.PakdeAI = {
        /**
         * @param {string} id        tenant id, mis. 'tenant_healthcare_01'
         * @param {object} [opts]    { name: 'Nama Bisnis', whatsapp: '0812-4455-6677' }
         */
        setTenant: (id, opts = {}) => {
            tenantId = id ? String(id) : '';
            tenantMeta = {};
            if (opts.name) tenantMeta.name = String(opts.name);
            if (opts.whatsapp) {
                const url = toWaUrl(opts.whatsapp);
                if (url) tenantMeta.whatsappUrl = url;
            }
            resetChat();
        },
        reset: () => resetChat(),
        getTenant: () => tenantId,
        open: () => togglePanel(true),
        close: () => togglePanel(false),
    };

    // Penanda versi: cek di Console untuk memastikan browser tidak memakai widget.js lama (cache)
    try { console.info('[PakdeAI] widget v2.2 aktif'); } catch (e) {}

    // ------------------------------------------------------------------
    // Pemicu cadangan ganti tenant (tidak bergantung pada skrip halaman)
    // 1) Event:  window.dispatchEvent(new CustomEvent('pakde:tenant-change',
    //              { detail: { id: 'tenant_x', name: 'Nama', whatsapp: '0812...' } }))
    // 2) Atribut: <select data-pakde-tenant> -> otomatis dipantau
    //             (opsional per <option>: data-name, data-whatsapp)
    // ------------------------------------------------------------------
    window.addEventListener('pakde:tenant-change', (e) => {
        const d = (e && e.detail) || {};
        const id = d.id || d.tenantId || d.tenant_id || '';
        if (String(id) === tenantId) return;
        window.PakdeAI.setTenant(id, { name: d.name, whatsapp: d.whatsapp });
    });

    const bindTenantSelect = (sel) => {
        if (!sel || sel.dataset.pakdeBound) return;
        sel.dataset.pakdeBound = '1';
        sel.addEventListener('change', () => {
            const opt = sel.options[sel.selectedIndex];
            if (String(sel.value) === tenantId) return;
            window.PakdeAI.setTenant(sel.value, {
                name: opt?.dataset?.name || '',
                whatsapp: opt?.dataset?.whatsapp || '',
            });
        });
    };
    document.querySelectorAll('select[data-pakde-tenant]').forEach(bindTenantSelect);

    // ------------------------------------------------------------------
    // Interaksi panel
    // ------------------------------------------------------------------
    function togglePanel(open) {
        const wasOpen = panel.classList.contains('is-open');
        panel.classList.toggle('is-open', open);
        panel.setAttribute('aria-hidden', String(!open));
        panel.inert = !open;

        // Chat ditutup -> riwayat dihapus (UI, memori, dan sesi baru di server)
        if (wasOpen && !open) {
            resetChat();
        }

        if (open) {
            setTimeout(() => { input.focus(); messages.scrollTop = messages.scrollHeight; }, 150);
        }
    }

    launcher.addEventListener('click', () => togglePanel(!panel.classList.contains('is-open')));
    closeBtn.addEventListener('click', () => togglePanel(false));

    document.querySelectorAll('[data-ai], #webia-nav-consult').forEach(b => {
        b.addEventListener('click', (e) => { e.preventDefault(); togglePanel(true); });
    });

    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = `${Math.min(input.scrollHeight, 100)}px`;
        sendBtn.disabled = input.value.trim().length === 0;
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) {
                if (form.requestSubmit) form.requestSubmit();
                else form.dispatchEvent(new Event('submit', { cancelable: true }));
            }
        }
    });

    // ------------------------------------------------------------------
    // Markdown renderer (input di-escape terlebih dahulu)
    // ------------------------------------------------------------------
    const renderMarkdown = (rawText) => {
        if (!rawText) return '';
        let text = rawText
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Tables
        text = text.replace(/((?:^|\n)\|[^\n]+\|\r?\n\|[-:\s|]+\|\r?\n(?:\|[^\n]+\|\r?\n?)+)/g, (match) => {
            const rows = match.trim().split('\n').map(r => r.trim()).filter(Boolean);
            if (rows.length < 2) return match;
            const headerCells = rows[0].replace(/^\||\|$/g, '').split('|').map(c => `<th>${c.trim()}</th>`).join('');
            const thead = `<thead><tr>${headerCells}</tr></thead>`;
            const bodyRows = rows.slice(2).map(r => {
                const cells = r.replace(/^\||\|$/g, '').split('|').map(c => `<td>${c.trim()}</td>`).join('');
                return `<tr>${cells}</tr>`;
            }).join('');
            return `\n\n<div class="pakde-ai-table-wrap"><table class="pakde-ai-table">${thead}<tbody>${bodyRows}</tbody></table></div>\n\n`;
        });

        // Bold & Inline Code
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/`([^`\n]+)`/g, '<code>$1</code>');

        // Markdown Links (hanya http/https)
        text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

        // Raw URLs
        text = text.replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');

        // Lists (ordered & unordered)
        const lines = text.split('\n');
        const outputLines = [];
        let inList = null;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const trimmed = line.trim();
            const ulMatch = trimmed.match(/^[-*]\s+(.*)$/);
            const olMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);

            if (ulMatch) {
                if (inList !== 'ul') {
                    if (inList) outputLines.push(`</${inList}>\n`);
                    else outputLines.push('\n');
                    outputLines.push('<ul class="pakde-ai-list">');
                    inList = 'ul';
                }
                outputLines.push(`<li>${ulMatch[1]}</li>`);
            } else if (olMatch) {
                if (inList !== 'ol') {
                    if (inList) outputLines.push(`</${inList}>\n`);
                    else outputLines.push('\n');
                    outputLines.push('<ol class="pakde-ai-list">');
                    inList = 'ol';
                }
                outputLines.push(`<li>${olMatch[2]}</li>`);
            } else {
                if (inList) {
                    outputLines.push(`</${inList}>\n`);
                    inList = null;
                }
                outputLines.push(line);
            }
        }
        if (inList) outputLines.push(`</${inList}>`);

        const joined = outputLines.join('\n');
        const blocks = joined.split(/\n{2,}/);
        return blocks.map(b => {
            const t = b.trim();
            if (!t) return '';
            if (t.startsWith('<ul') || t.startsWith('<ol') || t.startsWith('<div class="pakde-ai-table-wrap"')) {
                return t;
            }
            return `<p>${t.replace(/\n/g, '<br>')}</p>`;
        }).filter(Boolean).join('');
    };

    // ------------------------------------------------------------------
    // Pesan & kartu aksi
    // ------------------------------------------------------------------
    const appendMessage = (role, text) => {
        const group = document.createElement('div');
        group.className = `pakde-ai-msg-group pakde-ai-msg-group--${role}`;
        const bubble = document.createElement('div');
        bubble.className = 'pakde-ai-bubble';
        if (role === 'assistant') {
            bubble.innerHTML = renderMarkdown(text ? text.trim() : '');
        } else {
            bubble.textContent = text ? text.trim() : '';
        }
        group.appendChild(bubble);
        messages.insertBefore(group, typing);
        messages.scrollTop = messages.scrollHeight;
        return group;
    };

    const createStreamingBubble = () => {
        const group = document.createElement('div');
        group.className = 'pakde-ai-msg-group pakde-ai-msg-group--assistant';
        const bubble = document.createElement('div');
        bubble.className = 'pakde-ai-bubble';
        group.appendChild(bubble);
        messages.insertBefore(group, typing);
        messages.scrollTop = messages.scrollHeight;
        return {
            update: (fullText) => {
                bubble.innerHTML = renderMarkdown(fullText);
                messages.scrollTop = messages.scrollHeight;
            },
            element: bubble,
        };
    };

    const renderActionCard = (routing) => {
        if (!routing) return;
        const card = document.createElement('div');
        card.className = 'pakde-ai-action-card';

        // Fallback WhatsApp: milik tenant (L4) atau default PakDe (layer lain)
        const waFallback = isTenantLayer ? (tenantMeta.whatsappUrl || '') : DEFAULT_WA_URL;

        if (routing.action === 'navigate') {
            const url = safeUrl(routing.target_url);
            if (!url) return;
            card.innerHTML = `
                <span class="pakde-ai-action-label">✦ Rekomendasi Solusi</span>
                <a href="${esc(url)}" class="pakde-ai-action-btn pakde-ai-action-btn--primary">
                    ${esc(routing.button_text || 'Lihat Layanan →')}
                </a>
            `;
            messages.insertBefore(card, typing);
        } else if (routing.action === 'brief') {
            const url = safeUrl(routing.target_url) || waFallback;
            if (!url) return;
            card.innerHTML = `
                <span class="pakde-ai-action-label">📝 AI Business Brief Generator</span>
                ${routing.prompt_guide ? `<p style="font-size: 11.5px; color: var(--pakde-ai-muted); margin-bottom: 8px; line-height: 1.4;">${esc(routing.prompt_guide)}</p>` : ''}
                <a href="${esc(url)}" target="_blank" rel="noopener noreferrer" class="pakde-ai-action-btn pakde-ai-action-btn--primary">
                    ${esc(routing.button_text || 'Konsultasi Brief via WhatsApp →')}
                </a>
            `;
            messages.insertBefore(card, typing);
        } else if (routing.action === 'handoff') {
            const url = safeUrl(routing.target_url) || waFallback;
            if (!url) return;
            card.innerHTML = `
                <span class="pakde-ai-action-label">💬 Customer Support Resmi</span>
                <a href="${esc(url)}" target="_blank" rel="noopener noreferrer" class="pakde-ai-action-btn pakde-ai-action-btn--whatsapp">
                    ${esc(routing.button_text || 'Hubungi CS via WhatsApp →')}
                </a>
            `;
            messages.insertBefore(card, typing);
        }
        messages.scrollTop = messages.scrollHeight;
    };

    // Meta dari server (routing, nomor WA tenant, nama tenant)
    const handleMeta = (payload) => {
        if (isTenantLayer) {
            const waValue = payload.whatsapp || payload.tenant_whatsapp;
            if (waValue) setWhatsApp(waValue);
            if (payload.tenant_name && !tenantMeta.name) {
                tenantMeta.name = String(payload.tenant_name);
                applyTenantUi();
            }
        }
        if (payload.routing) renderActionCard(payload.routing);
    };

    // ------------------------------------------------------------------
    // Kirim pesan
    // ------------------------------------------------------------------
    const sendMessage = async (text) => {
        const query = text ? text.trim() : input.value.trim();
        if (!query) return;

        // Pengaman: bila tenant berubah tanpa melewati setter, reset dulu
        const liveTenant = window.__PAKDE_TENANT_ID ? String(window.__PAKDE_TENANT_ID) : '';
        if (liveTenant !== tenantId) {
            tenantId = liveTenant;
            tenantMeta = {};
            resetChat();
        }

        if (chipsContainer) chipsContainer.style.display = 'none';

        appendMessage('user', query);
        history.push({ role: 'user', content: query });

        input.value = '';
        input.style.height = 'auto';
        sendBtn.disabled = true;
        typing.style.display = 'flex';
        messages.scrollTop = messages.scrollHeight;

        // Tangkap konteks request ini
        const myRequest = ++requestCounter;
        const isCurrent = () => myRequest === requestCounter;
        if (abortController) { try { abortController.abort(); } catch (e) {} }
        abortController = new AbortController();
        const signal = abortController.signal;
        const payloadHistory = history.slice(-MAX_HISTORY);
        const tenantAtSend = tenantId;
        const sessionAtSend = sessionId;

        // Menghapus pesan user terakhir dari riwayat bila request gagal
        const rollbackUserMessage = () => {
            if (isCurrent() && history.length && history[history.length - 1].role === 'user') {
                history.pop();
            }
        };

        try {
            const res = await fetch(chatEndpoint, {
                method: 'POST',
                signal,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream, application/json',
                    'X-Site-Key': siteKey,
                    ...(tenantAtSend ? { 'X-Tenant-Id': tenantAtSend } : {}),
                },
                body: JSON.stringify({
                    layer: activeConfig.layer,
                    tenant_id: tenantAtSend || null,
                    session_id: sessionAtSend,
                    messages: payloadHistory,
                    stream: true,
                }),
            });

            if (!isCurrent()) return;

            const contentType = res.headers.get('content-type') || '';
            if (res.ok && contentType.includes('text/event-stream')) {
                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                let fullText = '';
                let bubbleController = null;
                let buffer = '';
                let streamFailed = false;

                try {
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        if (!isCurrent()) { try { reader.cancel(); } catch (e) {} return; }

                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split('\n');
                        buffer = lines.pop();

                        for (const line of lines) {
                            const trimmed = line.trim();
                            if (!trimmed.startsWith('data:')) continue;
                            try {
                                const payload = JSON.parse(trimmed.slice(5).trim());
                                if (payload.type === 'meta') {
                                    typing.style.display = 'none';
                                    handleMeta(payload);
                                } else if (payload.type === 'token') {
                                    typing.style.display = 'none';
                                    if (!bubbleController) bubbleController = createStreamingBubble();
                                    fullText += payload.content;
                                    bubbleController.update(fullText);
                                } else if (payload.type === 'done') {
                                    typing.style.display = 'none';
                                }
                            } catch (e) { /* baris SSE tidak valid, lewati */ }
                        }
                    }
                } catch (streamErr) {
                    if (streamErr.name === 'AbortError') return;
                    streamFailed = true;
                }

                if (!isCurrent()) return;
                typing.style.display = 'none';

                if (fullText && !streamFailed) {
                    history.push({ role: 'assistant', content: fullText });
                } else if (streamFailed) {
                    if (!fullText) appendMessage('assistant', 'Terjadi gangguan koneksi ke server AI.');
                    rollbackUserMessage();
                } else if (!fullText) {
                    rollbackUserMessage();
                }
            } else if (res.ok) {
                const data = await res.json();
                if (!isCurrent()) return;
                typing.style.display = 'none';
                if (data.success && data.message) {
                    const reply = data.message.content || 'Terima kasih atas pesan Anda.';
                    appendMessage('assistant', reply);
                    history.push({ role: 'assistant', content: reply });
                    handleMeta({
                        routing: data.routing,
                        whatsapp: data.whatsapp,
                        tenant_name: data.tenant_name,
                    });
                } else {
                    appendMessage('assistant', 'Mohon maaf, asisten sedang mengalami kendala teknis.');
                    rollbackUserMessage();
                }
            } else {
                typing.style.display = 'none';
                appendMessage('assistant', 'Mohon maaf, asisten sedang mengalami kendala teknis.');
                rollbackUserMessage();
            }
        } catch (err) {
            if (err && err.name === 'AbortError') return; // dibatalkan karena reset / pesan baru
            if (!isCurrent()) return;
            typing.style.display = 'none';
            appendMessage('assistant', 'Terjadi gangguan koneksi ke server AI.');
            rollbackUserMessage();
        } finally {
            if (isCurrent()) {
                abortController = null;
                input.focus();
            }
        }
    };

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage();
    });

    container.querySelectorAll('.pakde-ai-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            if (chip.dataset.prompt) sendMessage(chip.dataset.prompt);
        });
    });

    // Terapkan UI awal (bila tenant sudah ditentukan sebelum widget dimuat)
    applyTenantUi();
})();