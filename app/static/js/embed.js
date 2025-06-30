// Embeddable Chatbot Widget
(function() {
    // Determine host: from script src, window.EMBED_HOST, or window.location.origin
    var host = null;
    var scripts = document.getElementsByTagName('script');
    for (var i = scripts.length - 1; i >= 0; i--) {
        var s = scripts[i];
        if (s.src && s.src.indexOf('embed.js') !== -1) {
            try {
                var url = new URL(s.src);
                host = url.origin;
                break;
            } catch (e) {}
        }
    }
    if (!host) host = typeof window.EMBED_HOST !== 'undefined' ? window.EMBED_HOST : window.location.origin;

    // Inject custom CSS for widget
    if (!document.getElementById('chatbot-embed-style')) {
        var style = document.createElement('style');
        style.id = 'chatbot-embed-style';
        style.innerHTML = `
        .cbt-embed-btn {
            position: fixed; bottom: 24px; right: 24px; z-index: 9999;
            background: #222; color: #fff; border: none;
            border-radius: 50%; width: 56px; height: 56px;
            font-size: 2rem; box-shadow: 0 4px 16px rgba(0,0,0,0.18);
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; transition: background 0.2s;
        }
        .cbt-embed-btn:hover { background: #444; }
        .cbt-embed-window {
            position: fixed; bottom: 104px; right: 24px; z-index: 9999;
            width: 370px; max-width: 98vw; height: 600px;
            background: #f5f6fa; border-radius: 18px;
             border-radius:12px;
            box-shadow: 0 4px 32px rgba(0,0,0,0.18);
            border: 1px solid #e0e0e0;
            display: flex; flex-direction: column;
            transition: background 0.3s, border 0.3s;
        }
        .cbt-embed-window.cbt-dark {
            background: #232526; border: 1px solid #333;
             border-radius:12px;
        }
        .cbt-embed-header {
            padding: 16px 20px; border-bottom: 1px solid #e0e0e0;
            font-size: 1.1rem; font-weight: 600; letter-spacing: 1px;
            display: flex; align-items: center; justify-content: space-between;
            background: transparent;
             border-radius:12px;
        }
        .cbt-embed-window.cbt-dark .cbt-embed-header {
            border-bottom: 1px solid #333;
             border-radius:12px;
        }
        .cbt-embed-close {
            background: none; border: none; color: #888;
            font-size: 1.5rem; cursor: pointer; margin-left: 8px;
            transition: color 0.2s;
        }
        .cbt-embed-close:hover { color: #222; }
        .cbt-embed-window.cbt-dark .cbt-embed-close:hover { color: #fff; }
        .cbt-embed-mode {
            background: none; border: 1px solid #e0e0e0; border-radius: 50%;
            width: 32px; height: 32px; cursor: pointer; font-size: 1.1rem;
            color: #888; margin-right: 8px; transition: border 0.2s, color 0.2s;
        }
        .cbt-embed-window.cbt-dark .cbt-embed-mode {
            border: 1px solid #333; color: #bbb;
        }
        .cbt-embed-iframe {
            flex: 1; width: 100%; border: none; height: 100%;
             border-radius:12px;
            background: transparent;
        }
        @media (max-width: 500px) {
            .cbt-embed-window { width: 98vw !important; right: 1vw; }
        }
        `;
        document.head.appendChild(style);
    }

    // Get user_id from script tag or query param
    function getUserId() {
        var scripts = document.getElementsByTagName('script');
        for (var i = scripts.length - 1; i >= 0; i--) {
            var s = scripts[i];
            if (s.src && s.src.indexOf('embed.js') !== -1) {
                var uid = s.getAttribute('data-user-id');
                if (uid) return uid;
            }
        }
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('user_id');
    }

    // Create chat button
    var chatBtn = document.createElement('button');
    chatBtn.innerHTML = '💬';
    chatBtn.className = 'cbt-embed-btn';
    document.body.appendChild(chatBtn);

    // Create chat window (hidden by default)
    var chatWindow = document.createElement('div');
    chatWindow.className = 'cbt-embed-window';
    chatWindow.style.display = 'none';
    chatWindow.innerHTML = `
      <div class="cbt-embed-header">
        <button class="cbt-embed-mode" title="Toggle light/dark mode">🌙</button>
        <span>Chatbot</span>
        <button class="cbt-embed-close" title="Close">&times;</button>
      </div>
      <iframe class="cbt-embed-iframe" allowtransparency="true"></iframe>
    `;
    document.body.appendChild(chatWindow);

    var modeBtn = chatWindow.querySelector('.cbt-embed-mode');
    var closeBtn = chatWindow.querySelector('.cbt-embed-close');
    var iframe = chatWindow.querySelector('iframe');

    // Light/dark mode logic
    function setMode(dark) {
        if (dark) {
            chatWindow.classList.add('cbt-dark');
            modeBtn.innerHTML = '☀️';
            modeBtn.title = 'Switch to light mode';
            localStorage.setItem('cbt-embed-dark', '1');
        } else {
            chatWindow.classList.remove('cbt-dark');
            modeBtn.innerHTML = '🌙';
            modeBtn.title = 'Switch to dark mode';
            localStorage.setItem('cbt-embed-dark', '0');
        }
        // Pass mode to iframe
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({ type: 'cbt-mode', dark }, '*');
        }
    }
    modeBtn.onclick = function() {
        var isDark = chatWindow.classList.contains('cbt-dark');
        setMode(!isDark);
    };
    (function initMode() {
        var dark = localStorage.getItem('cbt-embed-dark') === '1';
        setMode(dark);
    })();

    // Toggle chat window
    chatBtn.onclick = function() {
        chatWindow.style.display = chatWindow.style.display === 'none' ? 'flex' : 'none';
        if (chatWindow.style.display === 'flex') {
            var userId = getUserId();
            var url = `${host}/api/v1/chatbot/view?user_id=${userId}`;
            iframe.src = url;
            // Pass mode to iframe after load
            iframe.onload = function() {
                var dark = chatWindow.classList.contains('cbt-dark');
                iframe.contentWindow.postMessage({ type: 'cbt-mode', dark }, '*');
            };
        }
    };
    closeBtn.onclick = function() {
        chatWindow.style.display = 'none';
    };

    // Listen for mode change requests from iframe (optional, for two-way sync)
    window.addEventListener('message', function(e) {
        if (e.data && e.data.type === 'cbt-mode-request') {
            setMode(!!e.data.dark);
        }
    });
})();
