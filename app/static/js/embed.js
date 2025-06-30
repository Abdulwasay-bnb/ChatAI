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
    // Add Tailwind CDN if not present
    if (!document.getElementById('tailwind-cdn')) {
        var tw = document.createElement('script');
        tw.src = `${host}/static/js/tailwind.min.js`;
        tw.id = 'tailwind-cdn';
        document.head.appendChild(tw);
    }

    // Get user_id from script tag or query param
    function getUserId() {
        // Try to find the script tag for embed.js
        var scripts = document.getElementsByTagName('script');
        for (var i = scripts.length - 1; i >= 0; i--) {
            var s = scripts[i];
            if (s.src && s.src.indexOf('embed.js') !== -1) {
                var uid = s.getAttribute('data-user-id');
                if (uid) return uid;
            }
        }
        // Fallback: try query param on host page
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('user_id');
    }

    // Create chat button
    var chatBtn = document.createElement('button');
    chatBtn.innerHTML = '💬';
    chatBtn.className = 'fixed bottom-6 right-6 z-50 bg-blue-600 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg hover:bg-blue-700 focus:outline-none';
    chatBtn.style.fontSize = '2rem';
    chatBtn.style.transition = 'background 0.2s';
    document.body.appendChild(chatBtn);

    // Create chat window (hidden by default)
    var chatWindow = document.createElement('div');
    chatWindow.className = 'fixed bottom-24 right-6 z-50 w-80 max-w-full bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col';
    chatWindow.style.display = 'none';
    chatWindow.style.height = '500px';
    chatWindow.innerHTML = '<div class="flex items-center justify-between p-4 border-b"><span class="font-bold text-lg">Chatbot</span><button id="closeChatbot" class="text-gray-400 hover:text-gray-700">&times;</button></div><iframe id="chatbotFrame" src="" class="flex-1 w-full border-0" style="height:420px;"></iframe>';
    document.body.appendChild(chatWindow);

    // Toggle chat window
    chatBtn.onclick = function() {
        chatWindow.style.display = chatWindow.style.display === 'none' ? 'flex' : 'none';
        if (chatWindow.style.display === 'flex') {
            // Load chatbot view
            var userId = getUserId();
            console.log('Chatbot user_id:', userId); // Debug
            var frame = document.getElementById('chatbotFrame');
            frame.src = `${host}/api/v1/chatbot/view?user_id=${userId}`;
        }
    };
    document.getElementById('closeChatbot').onclick = function() {
        chatWindow.style.display = 'none';
    };
})();
