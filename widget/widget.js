/**
 * Universal PakDe AI Widget (Multi-Tier: D-KREASI, WEBIA, D-KARSA)
 * Automatically adapts title, persona, theme styling, and suggestion chips
 * based on data-site-key or data-layer.
 */
(() => {
    'use strict';

    // Locate script tag
    const currentScript = document.currentScript || Array.from(document.querySelectorAll('script')).find(s => s.src.includes('widget.js'));
    const siteKey = currentScript?.dataset?.siteKey || 'site_dkreasi_public';
    const layerParam = currentScript?.dataset?.layer;
    const baseUrl = (currentScript?.dataset?.apiUrl || window.location.origin || 'http://localhost:8001').replace(/\/$/, '');
    const chatEndpoint = `${baseUrl}/api/v1/chat`;

    // Multi-Tier Configuration Catalog
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
            chips: [],
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
            chips: [],
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
            chips: [],
            footer: "Tanya D'Karsa · Konsultan Undangan Digital by PakDe Group"
        }
    };

    // Determine active profile
    let activeConfig = CONFIGS[siteKey] || CONFIGS['site_dkreasi_public'];
    if (layerParam === 'l2' || siteKey.includes('dkarsa')) activeConfig = CONFIGS['site_dkarsa_public'];
    if (layerParam === 'l3' || siteKey.includes('webia')) activeConfig = CONFIGS['site_webia_public'];

    // Inject CSS
    if (!document.querySelector('link[href*="widget.css"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = `${baseUrl}/widget/widget.css`;
        document.head.appendChild(link);
    }

    // Session Management
    const SESSION_KEY = `pakde_ai_session_${activeConfig.layer}`;
    let sessionId = sessionStorage.getItem(SESSION_KEY);
    if (!sessionId) {
        sessionId = `sess_${activeConfig.layer}_` + Math.random().toString(36).substring(2, 10);
        sessionStorage.setItem(SESSION_KEY, sessionId);
    }

    const history = [];

    // Render Chips HTML
    const chipsHtml = activeConfig.chips.map(c => 
        `<button type="button" class="pakde-ai-chip" data-prompt="${c.prompt}">${c.label}</button>`
    ).join('');

    // Create Widget Container with dedicated theme class
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
                    <a href="https://wa.me/6281234567890" target="_blank" rel="noopener noreferrer" class="pakde-ai-wa-btn" id="pakde-ai-header-wa">
                        💬 CS
                    </a>
                    <button class="pakde-ai-close" id="pakde-ai-close" aria-label="Tutup">×</button>
                </div>
            </header>

            <div class="pakde-ai-messages" id="pakde-ai-messages">
                <div class="pakde-ai-welcome">
                    <span class="pakde-ai-eyebrow">${activeConfig.eyebrow}</span>
                    <h3>${activeConfig.welcomeTitle}</h3>
                    <p>${activeConfig.welcomeDesc}</p>
                </div>

                <div class="pakde-ai-msg-group pakde-ai-msg-group--assistant">
                    <div class="pakde-ai-bubble">${activeConfig.initialMsg}</div>
                </div>

                ${(activeConfig.chips && activeConfig.chips.length > 0) ? `
                <div class="pakde-ai-chips" id="pakde-ai-chips">
                    ${chipsHtml}
                </div>` : ''}

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

    const togglePanel = (open) => {
        panel.classList.toggle('is-open', open);
        panel.setAttribute('aria-hidden', String(!open));
        panel.inert = !open;
        if (open) {
            setTimeout(() => { input.focus(); messages.scrollTop = messages.scrollHeight; }, 150);
        }
    };

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
            if (!sendBtn.disabled) form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    });

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

        // Markdown Links
        text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^\s\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

        // Raw URLs
        text = text.replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');

        // Headings (h1 - h4)
        text = text.replace(/^####\s+(.*)$/gm, '<h5 class="pakde-ai-h5">$1</h5>');
        text = text.replace(/^###\s+(.*)$/gm, '<h4 class="pakde-ai-h4">$1</h4>');
        text = text.replace(/^##\s+(.*)$/gm, '<h3 class="pakde-ai-h3">$1</h3>');
        text = text.replace(/^#\s+(.*)$/gm, '<h2 class="pakde-ai-h2">$1</h2>');

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
            if (t.startsWith('<ul') || t.startsWith('<ol') || t.startsWith('<div class="pakde-ai-table-wrap"') || t.startsWith('<h2') || t.startsWith('<h3') || t.startsWith('<h4') || t.startsWith('<h5')) {
                return t;
            }
            return `<p>${t.replace(/\n/g, '<br>')}</p>`;
        }).filter(Boolean).join('');
    };

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
        messages.appendChild(typing);
        messages.scrollTop = messages.scrollHeight;
        return {
            update: (fullText) => {
                bubble.innerHTML = renderMarkdown(fullText);
                messages.scrollTop = messages.scrollHeight;
            },
            element: bubble,
        };
    };

    const renderFollowupSuggestion = (query, replyText) => {
        // Hapus suggestion followup lama bila ada
        const oldSuggestions = messages.querySelectorAll('.pakde-ai-followup');
        oldSuggestions.forEach(el => el.remove());

        const text = (query + ' ' + replyText).toLowerCase();
        let prompt = '';
        let label = '';

        if (activeConfig.layer === 'l2' || activeConfig.theme === 'dkarsa') {
            // Logika saran kontekstual D-Karsa
            if (text.includes('harga') || text.includes('paket') || text.includes('biaya') || text.includes('tarif')) {
                label = '🌸 Ingin lihat pilihan tema desain yang cocok?';
                prompt = 'Bisa rekomendasikan pilihan tema desain undangan yang tersedia?';
            } else if (text.includes('haji') || text.includes('umroh') || text.includes('safar')) {
                label = '🕋 Ingin tahu detail paket dan cara pemesanan tema haji?';
                prompt = 'Berapa harga paket untuk tema Walimatus Safar Haji dan bagaimana cara pesannya?';
            } else if (text.includes('jawa') || text.includes('keraton') || text.includes('3d') || text.includes('wayang')) {
                label = '💍 Mau info rincian fitur Paket Eksklusif 3D?';
                prompt = 'Apa saja rincian fitur lengkap di Paket Eksklusif Rp180.000?';
            } else if (text.includes('batak') || text.includes('ulos')) {
                label = '💍 Mau konsultasi pemesanan tema Batak Istimewa?';
                prompt = 'Bagaimana alur pemesanan terima beres untuk tema Batak Istimewa?';
            } else if (text.includes('bayar') || text.includes('midtrans') || text.includes('qris')) {
                label = '💬 Mau konsultasi langsung dengan CS WhatsApp?';
                prompt = 'Saya ingin berkonsultasi langsung dengan CS D-Karsa seputar pesanan saya.';
            } else {
                label = '💍 Cek daftar harga paket undangan resmi?';
                prompt = 'Berapa daftar paket dan harga resmi undangan digital di D-Karsa?';
            }
        } else {
            // Logika saran kontekstual Webia (L3) & Portal (L1)
            if (text.includes('petshop') || text.includes('hewan') || text.includes('kucing') || text.includes('anjing')) {
                label = '🐾 Mau tahu perbedaan fitur PawMart vs Furry & Co.?';
                prompt = 'Apa perbedaan antara template PawMart dengan Furry & Co.?';
            } else if (text.includes('dental') || text.includes('gigi') || text.includes('dokter')) {
                label = '🦷 Mau cek fitur kalkulator cicilan di Sunset Dental?';
                prompt = 'Bisa jelaskan fitur kalkulator cicilan dan paket di Sunset Dental Care?';
            } else if (text.includes('harga') || text.includes('paket') || text.includes('pixel') || text.includes('pulse')) {
                label = '📝 Mau dibantu buatkan Business Brief website usaha Anda?';
                prompt = 'Bantu saya susun business brief untuk website usaha saya.';
            } else if (text.includes('bengkel') || text.includes('otomotif') || text.includes('mobil')) {
                label = '🚗 Cek rekomendasi paket untuk bengkel dan showroom?';
                prompt = 'Untuk usaha bengkel dan showroom mobil, paket website apa yang paling pas?';
            } else if (text.includes('cafe') || text.includes('resto') || text.includes('fnb') || text.includes('kopi')) {
                label = '☕ Mau lihat fitur reservasi meja di template Cafe Earthtone?';
                prompt = 'Apa saja fitur reservasi meja dan menu di template Cafe Earthtone?';
            } else {
                label = '💡 Mau tahu 4 paket website dan estimasi harganya?';
                prompt = 'Berapa daftar 4 paket dan harga resmi website di WEBIA?';
            }
        }

        if (label && prompt) {
            const wrap = document.createElement('div');
            wrap.className = 'pakde-ai-followup';
            wrap.innerHTML = `
                <span class="pakde-ai-followup-label">✦ Saran Pertanyaan Selanjutnya</span>
                <button type="button" class="pakde-ai-followup-btn">
                    <span>${label}</span>
                    <span style="opacity: 0.7;">→</span>
                </button>
            `;
            const btn = wrap.querySelector('.pakde-ai-followup-btn');
            btn.addEventListener('click', () => {
                wrap.remove();
                sendMessage(prompt);
            });
            messages.insertBefore(wrap, typing);
            messages.scrollTop = messages.scrollHeight;
        }
    };

    const renderActionCard = (routing) => {
        if (!routing) return;
        const card = document.createElement('div');
        card.className = 'pakde-ai-action-card';

        if (routing.action === 'navigate' && routing.target_url) {
            card.innerHTML = `
                <span class="pakde-ai-action-label">✦ Rekomendasi Solusi</span>
                <a href="${routing.target_url}" class="pakde-ai-action-btn pakde-ai-action-btn--primary">
                    ${routing.button_text || 'Lihat Layanan →'}
                </a>
            `;
            messages.insertBefore(card, typing);
        } else if (routing.action === 'brief') {
            card.innerHTML = `
                <span class="pakde-ai-action-label">📝 AI Business Brief Generator</span>
                ${routing.prompt_guide ? `<p style="font-size: 11.5px; color: var(--pakde-ai-muted); margin-bottom: 8px; line-height: 1.4;">${routing.prompt_guide}</p>` : ''}
                <a href="${routing.target_url || 'https://wa.me/6281234567890'}" target="_blank" rel="noopener noreferrer" class="pakde-ai-action-btn pakde-ai-action-btn--primary">
                    ${routing.button_text || 'Konsultasi Brief via WhatsApp →'}
                </a>
            `;
            messages.insertBefore(card, typing);
        } else if (routing.action === 'handoff') {
            card.innerHTML = `
                <span class="pakde-ai-action-label">💬 Customer Support Resmi</span>
                <a href="${routing.target_url || 'https://wa.me/6281234567890'}" target="_blank" rel="noopener noreferrer" class="pakde-ai-action-btn pakde-ai-action-btn--whatsapp">
                    ${routing.button_text || 'Hubungi CS via WhatsApp →'}
                </a>
            `;
            messages.insertBefore(card, typing);
        }
        messages.scrollTop = messages.scrollHeight;
    };

    const sendMessage = async (text) => {
        const query = text ? text.trim() : input.value.trim();
        if (!query) return;

        if (chipsContainer) chipsContainer.style.display = 'none';

        appendMessage('user', query);
        history.push({ role: 'user', content: query });

        input.value = '';
        input.style.height = 'auto';
        sendBtn.disabled = true;
        typing.style.display = 'flex';
        messages.appendChild(typing);
        messages.scrollTop = messages.scrollHeight;

        try {
            const res = await fetch(chatEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream, application/json',
                    'X-Site-Key': siteKey,
                },
                body: JSON.stringify({
                    layer: activeConfig.layer,
                    session_id: sessionId,
                    messages: history,
                    stream: true,
                }),
            });

            const contentType = res.headers.get('content-type') || '';
            if (res.ok && contentType.includes('text/event-stream')) {
                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                let fullText = '';
                let bubbleController = null;
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        const trimmed = line.trim();
                        if (trimmed.startsWith('data:')) {
                            try {
                                const payload = JSON.parse(trimmed.slice(5).trim());
                                if (payload.type === 'meta') {
                                    // Sembunyikan typing indicator hanya saat token pertama keluar
                                    if (payload.routing) renderActionCard(payload.routing);
                                } else if (payload.type === 'token') {
                                    typing.style.display = 'none';
                                    if (!bubbleController) {
                                        bubbleController = createStreamingBubble();
                                    }
                                    fullText += payload.content;
                                    bubbleController.update(fullText);
                                } else if (payload.type === 'done') {
                                    typing.style.display = 'none';
                                }
                            } catch (e) {}
                        }
                    }
                }
                typing.style.display = 'none';
                if (fullText) {
                    history.push({ role: 'assistant', content: fullText });
                    renderFollowupSuggestion(query, fullText);
                }
            } else if (res.ok) {
                const data = await res.json();
                typing.style.display = 'none';
                if (data.success && data.message) {
                    const reply = data.message.content || 'Terima kasih atas pesan Anda.';
                    appendMessage('assistant', reply);
                    history.push({ role: 'assistant', content: reply });
                    if (data.routing) renderActionCard(data.routing);
                    renderFollowupSuggestion(query, reply);
                } else {
                    appendMessage('assistant', 'Mohon maaf, asisten sedang mengalami kendala teknis.');
                }
            } else {
                typing.style.display = 'none';
                appendMessage('assistant', 'Mohon maaf, asisten sedang mengalami kendala teknis.');
            }
        } catch (err) {
            typing.style.display = 'none';
            appendMessage('assistant', 'Terjadi gangguan koneksi ke server AI.');
        }
        input.focus();
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
})();
