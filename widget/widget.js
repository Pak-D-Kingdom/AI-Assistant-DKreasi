/**
 * Universal Embeddable PakDe AI Assistant Widget
 * Can be embedded via:
 * <script src="http://ai-server:8000/widget/widget.js" data-site-key="site_dkreasi_public" data-api-url="http://ai-server:8000"></script>
 */
(() => {
    'use strict';

    // Locate script tag to read configuration
    const currentScript = document.currentScript || Array.from(document.querySelectorAll('script')).pop();
    const siteKey = currentScript?.dataset?.siteKey || 'site_dkreasi_public';
    const baseUrl = currentScript?.dataset?.apiUrl || 'http://localhost:8000';
    const chatEndpoint = `${baseUrl.replace(/\/$/, '')}/api/ai/chat`;

    // Inject CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = `${baseUrl.replace(/\/$/, '')}/widget/widget.css`;
    document.head.appendChild(link);

    // Create Root DOM
    const container = document.createElement('div');
    container.className = 'pakde-ai-widget';
    container.innerHTML = `
        <button class="pakde-ai-launcher" id="pakde-ai-launcher" aria-label="Buka AI Assistant">
            <span class="pakde-ai-icon">✦</span>
            <span class="pakde-ai-label">AI Assistant</span>
        </button>

        <section class="pakde-ai-panel" id="pakde-ai-panel" aria-hidden="true">
            <header class="pakde-ai-header">
                <div class="pakde-ai-identity">
                    <div class="pakde-ai-avatar">✦</div>
                    <div>
                        <h2>PakDe Assistant</h2>
                        <p><span class="pakde-ai-dot"></span> Online</p>
                    </div>
                </div>
                <button class="pakde-ai-close" id="pakde-ai-close">×</button>
            </header>

            <div class="pakde-ai-messages" id="pakde-ai-messages">
                <div class="pakde-ai-msg pakde-ai-msg--assistant">
                    Halo! Ada yang bisa saya bantu terkait layanan digital PakDe Group?
                </div>
            </div>

            <form class="pakde-ai-form" id="pakde-ai-form">
                <input type="text" id="pakde-ai-input" placeholder="Ketik pertanyaan Anda..." autocomplete="off" />
                <button type="submit" id="pakde-ai-send">↑</button>
            </form>
        </section>
    `;
    document.body.appendChild(container);

    const launcher = container.querySelector('#pakde-ai-launcher');
    const panel = container.querySelector('#pakde-ai-panel');
    const closeBtn = container.querySelector('#pakde-ai-close');
    const messages = container.querySelector('#pakde-ai-messages');
    const form = container.querySelector('#pakde-ai-form');
    const input = container.querySelector('#pakde-ai-input');

    const togglePanel = (open) => {
        panel.classList.toggle('is-open', open);
    };

    launcher.addEventListener('click', () => togglePanel(!panel.classList.contains('is-open')));
    closeBtn.addEventListener('click', () => togglePanel(false));

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        // Render user message
        const userBubble = document.createElement('div');
        userBubble.className = 'pakde-ai-msg pakde-ai-msg--user';
        userBubble.textContent = text;
        messages.appendChild(userBubble);

        input.value = '';
        messages.scrollTop = messages.scrollHeight;

        try {
            const res = await fetch(chatEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Site-Key': siteKey,
                },
                body: JSON.stringify({
                    messages: [{ role: 'user', content: text }],
                }),
            });
            const data = await res.json();
            const botBubble = document.createElement('div');
            botBubble.className = 'pakde-ai-msg pakde-ai-msg--assistant';
            botBubble.textContent = data.message?.content || 'Terima kasih atas pesan Anda.';
            messages.appendChild(botBubble);

            if (data.routing && data.routing.action === 'navigate' && data.routing.target_url) {
                const btn = document.createElement('a');
                btn.href = data.routing.target_url;
                btn.className = 'pakde-ai-cta';
                btn.textContent = data.routing.button_text || 'Lihat Layanan →';
                messages.appendChild(btn);
            }
        } catch (err) {
            const errBubble = document.createElement('div');
            errBubble.className = 'pakde-ai-msg pakde-ai-msg--assistant';
            errBubble.textContent = 'Mohon maaf, terjadi gangguan koneksi ke server AI.';
            messages.appendChild(errBubble);
        }
        messages.scrollTop = messages.scrollHeight;
    });
})();
