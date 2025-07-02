// Sidebar tab switching
const sidebarBtns = document.querySelectorAll('.sidebar-btn');
const tabs = document.querySelectorAll('.admin-tab');
sidebarBtns.forEach(btn => {
    btn.onclick = () => {
        tabs.forEach(tab => tab.classList.add('hidden'));
        document.getElementById('tab-' + btn.dataset.tab).classList.remove('hidden');
        sidebarBtns.forEach(b => b.classList.remove('bg-blue-600'));
        btn.classList.add('bg-blue-600');
    };
});
sidebarBtns[0].click();

// Modal helper
function createModal(content) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/40';
    modal.innerHTML = `<div class='bg-white dark:bg-slate-800 p-8 rounded-xl shadow-xl min-w-[320px] max-w-lg'>${content}</div>`;
    modal.onclick = e => { if (e.target === modal) modal.remove(); };
    document.body.appendChild(modal);
    return modal;
}

// --- USERS CRUD ---
async function loadUsers() {
    const res = await fetch('/api/v1/auth/user/all');
    const users = await res.json();
    const table = document.getElementById('users-table');
    table.innerHTML = '';
    users.forEach(u => {
        const tr = document.createElement('tr');
        tr.className = 'border-b border-gray-200 dark:border-slate-700';
        tr.innerHTML = `
            <td class="py-2 px-4">${u.full_name || '-'}</td>
            <td class="py-2 px-4">${u.email}</td>
            <td class="py-2 px-4">${u.business_profile_id}</td>
            <td class="py-2 px-4">${u.id}</td>
            <td class="py-2 px-4 flex gap-2">
                <button class="edit-user-btn bg-blue-500 hover:bg-blue-700 text-white px-2 py-1 rounded text-xs" data-id="${u.id}">Edit</button>
                <button class="delete-user-btn bg-red-500 hover:bg-red-700 text-white px-2 py-1 rounded text-xs" data-id="${u.id}">Delete</button>
            </td>
        `;
        table.appendChild(tr);
    });
    bindUserActions();
}
function bindUserActions() {
    document.querySelectorAll('.edit-user-btn').forEach(btn => {
        btn.onclick = function() {
            const row = btn.closest('tr');
            const id = btn.dataset.id;
            const name = row.children[0].innerText;
            const email = row.children[1].innerText;
            const modal = createModal(`
                <h3 class='font-bold text-lg mb-4 gradient-text'>Edit User</h3>
                <form id='edit-user-form' class='space-y-3'>
                    <input type='text' name='full_name' class='w-full border rounded px-3 py-2' value='${name}' placeholder='Full Name' required />
                    <input type='email' name='email' class='w-full border rounded px-3 py-2' value='${email}' placeholder='Email' required />
                    <input type='password' name='password' class='w-full border rounded px-3 py-2' placeholder='New Password (leave blank to keep)' />
                    <div class='flex gap-2 mt-4'>
                        <button type='submit' class='bg-blue-600 text-white px-4 py-2 rounded'>Save</button>
                        <button type='button' class='close-modal px-4 py-2 rounded border'>Cancel</button>
                    </div>
                </form>
            `);
            modal.querySelector('.close-modal').onclick = () => modal.remove();
            modal.querySelector('#edit-user-form').onsubmit = async function(e) {
                e.preventDefault();
                const form = e.target;
                const data = {
                    full_name: form.full_name.value,
                    email: form.email.value,
                    password: form.password.value
                };
                if (!data.password) delete data.password;
                const res = await fetch(`/api/v1/auth/user/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (res.ok) {
                    modal.remove();
                    loadUsers();
                } else {
                    alert('Failed to update user.');
                }
            };
        };
    });
    document.querySelectorAll('.delete-user-btn').forEach(btn => {
        btn.onclick = async function() {
            if (!confirm('Delete this user?')) return;
            const id = btn.dataset.id;
            const res = await fetch(`/api/v1/auth/user/${id}`, { method: 'DELETE' });
            if (res.ok) loadUsers();
            else alert('Failed to delete user.');
        };
    });
}
// Add User Modal
function addUserModal() {
    const modal = createModal(`
        <h3 class='font-bold text-lg mb-4 gradient-text'>Add User</h3>
        <form id='add-user-form' class='space-y-3'>
            <input type='text' name='full_name' class='w-full border rounded px-3 py-2' placeholder='Full Name' required />
            <input type='email' name='email' class='w-full border rounded px-3 py-2' placeholder='Email' required />
            <input type='password' name='password' class='w-full border rounded px-3 py-2' placeholder='Password' required />
            <div class='flex gap-2 mt-4'>
                <button type='submit' class='bg-blue-600 text-white px-4 py-2 rounded'>Add</button>
                <button type='button' class='close-modal px-4 py-2 rounded border'>Cancel</button>
            </div>
        </form>
    `);
    modal.querySelector('.close-modal').onclick = () => modal.remove();
    modal.querySelector('#add-user-form').onsubmit = async function(e) {
        e.preventDefault();
        const form = e.target;
        const data = {
            full_name: form.full_name.value,
            email: form.email.value,
            password: form.password.value
        };
        const res = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            modal.remove();
            loadUsers();
        } else {
            alert('Failed to add user.');
        }
    };
}
document.querySelector('.add-user-btn').onclick = addUserModal;

// Search/filter logic for users
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    input.addEventListener('input', function() {
        const val = this.value.toLowerCase();
        Array.from(table.children).forEach(row => {
            row.style.display = row.innerText.toLowerCase().includes(val) ? '' : 'none';
        });
    });
}
filterTable('search-users', 'users-table');

// --- CHATBOTS CRUD ---
async function loadChatbots() {
    const res = await fetch('/api/v1/chatbot/');
    const chatbots = await res.json();
    const table = document.getElementById('chatbots-table');
    table.innerHTML = '';
    for (const bot of chatbots) {
        let ownerEmail = bot.owner_email || '';
        if (!ownerEmail && bot.owner_id) {
            try {
                const userRes = await fetch(`/api/v1/auth/user/${bot.owner_id}`);
                if (userRes.ok) {
                    const user = await userRes.json();
                    ownerEmail = user.email || '';
                }
            } catch {}
        }
        const tr = document.createElement('tr');
        tr.className = 'border-b border-gray-200 dark:border-slate-700';
        tr.innerHTML = `
            <td class="py-2 px-4">${bot.name}</td>
            <td class="py-2 px-4">${ownerEmail}</td>
            <td class="py-2 px-4">${bot.owner_id}</td>
            <td class="py-2 px-4">${bot.business_profile_id}</td>
            <td class="py-2 px-4 truncate max-w-xs">${bot.prompt}</td>
            <td class="py-2 px-4 flex gap-2">
                <button class="edit-chatbot-btn bg-blue-500 hover:bg-blue-700 text-white px-2 py-1 rounded text-xs" data-id="${bot.id}">Edit</button>
                <button class="delete-chatbot-btn bg-red-500 hover:bg-red-700 text-white px-2 py-1 rounded text-xs" data-id="${bot.id}">Delete</button>
            </td>
        `;
        table.appendChild(tr);
    }
    bindChatbotActions();
}
function bindChatbotActions() {
    document.querySelectorAll('.edit-chatbot-btn').forEach(btn => {
        btn.onclick = function() {
            const row = btn.closest('tr');
            const id = btn.dataset.id;
            const name = row.children[0].innerText;
            const prompt = row.children[4].innerText;
            const owner_id = row.children[2].innerText;
            const business_profile_id = row.children[3].innerText;
            const modal = createModal(`
                <h3 class='font-bold text-lg mb-4 gradient-text'>Edit Chatbot</h3>
                <form id='edit-chatbot-form' class='space-y-3'>
                    <input type='text' name='name' class='w-full border rounded px-3 py-2' value='${name}' placeholder='Name' required />
                    <textarea name='prompt' class='w-full border rounded px-3 py-2' placeholder='Prompt'>${prompt}</textarea>
                    <div class='flex gap-2 mt-4'>
                        <button type='submit' class='bg-blue-600 text-white px-4 py-2 rounded'>Save</button>
                        <button type='button' class='close-modal px-4 py-2 rounded border'>Cancel</button>
                    </div>
                </form>
            `);
            modal.querySelector('.close-modal').onclick = () => modal.remove();
            modal.querySelector('#edit-chatbot-form').onsubmit = async function(e) {
                e.preventDefault();
                const form = e.target;
                const data = {
                    name: form.name.value,
                    prompt: form.prompt.value,
                    owner_id: owner_id,
                    business_profile_id: business_profile_id
                };
                const res = await fetch(`/api/v1/chatbot/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (res.ok) {
                    modal.remove();
                    loadChatbots();
                } else {
                    alert('Failed to update chatbot.');
                }
            };
        };
    });
    document.querySelectorAll('.delete-chatbot-btn').forEach(btn => {
        btn.onclick = async function() {
            if (!confirm('Delete this chatbot?')) return;
            const id = btn.dataset.id;
            const res = await fetch(`/api/v1/chatbot/${id}`, { method: 'DELETE' });
            if (res.ok) loadChatbots();
            else alert('Failed to delete chatbot.');
        };
    });
}
function addChatbotModal() {
    const modal = createModal(`
        <h3 class='font-bold text-lg mb-4 gradient-text'>Add Chatbot</h3>
        <form id='add-chatbot-form' class='space-y-3'>
            <input type='text' name='name' class='w-full border rounded px-3 py-2' placeholder='Name' required />
            <input type='text' name='owner_id' class='w-full border rounded px-3 py-2' placeholder='Owner ID' required />
            <input type='text' name='business_profile_id' class='w-full border rounded px-3 py-2' placeholder='Business Profile ID' required />
            <textarea name='prompt' class='w-full border rounded px-3 py-2' placeholder='Prompt'></textarea>
            <div class='flex gap-2 mt-4'>
                <button type='submit' class='bg-blue-600 text-white px-4 py-2 rounded'>Add</button>
                <button type='button' class='close-modal px-4 py-2 rounded border'>Cancel</button>
            </div>
        </form>
    `);
    modal.querySelector('.close-modal').onclick = () => modal.remove();
    modal.querySelector('#add-chatbot-form').onsubmit = async function(e) {
        e.preventDefault();
        const form = e.target;
        const data = {
            name: form.name.value,
            owner_id: form.owner_id.value,
            business_profile_id: form.business_profile_id.value,
            prompt: form.prompt.value
        };
        const res = await fetch('/api/v1/chatbot/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            modal.remove();
            loadChatbots();
        } else {
            alert('Failed to add chatbot.');
        }
    };
}
document.querySelector('.add-chatbot-btn').onclick = addChatbotModal;
filterTable('search-chatbots', 'chatbots-table');

// --- CHATBOT SUGGESTIONS CRUD ---
async function loadSuggestions() {
    // For each chatbot, load its suggestions
    const res = await fetch('/api/v1/chatbot/');
    const chatbots = await res.json();
    const table = document.getElementById('suggestions-table');
    table.innerHTML = '';
    for (const bot of chatbots) {
        let ownerId = bot.owner_id || '';
        let ownerEmail = bot.owner_email || '';
        if (!ownerEmail && ownerId) {
            try {
                const userRes = await fetch(`/api/v1/auth/user/${ownerId}`);
                if (userRes.ok) {
                    const user = await userRes.json();
                    ownerEmail = user.email || '';
                }
            } catch {}
        }
        const resSug = await fetch(`/api/v1/chatbot/${bot.id}/suggestions`);
        if (!resSug.ok) continue;
        const suggestion = await resSug.json();
        const tr = document.createElement('tr');
        tr.className = 'border-b border-gray-200 dark:border-slate-700';
        tr.innerHTML = `
            <td class="py-2 px-4">${bot.name}</td>
            <td class="py-2 px-4">${bot.id}</td>
            <td class="py-2 px-4">${ownerId}</td>
            <td class="py-2 px-4">${ownerEmail}</td>
            <td class="py-2 px-4">${Object.values(suggestion.suggestions).join('<br>')}</td>
            <td class="py-2 px-4 flex gap-2">
                <button class="edit-suggestion-btn bg-blue-500 hover:bg-blue-700 text-white px-2 py-1 rounded text-xs" data-id="${bot.id}">Edit</button>
            </td>
        `;
        table.appendChild(tr);
    }
    bindSuggestionActions();
}
function bindSuggestionActions() {
    document.querySelectorAll('.edit-suggestion-btn').forEach(btn => {
        btn.onclick = async function() {
            const chatbot_id = btn.dataset.id;
            const res = await fetch(`/api/v1/chatbot/${chatbot_id}/suggestions`);
            if (!res.ok) return alert('Failed to load suggestions.');
            const suggestion = await res.json();
            const suggestions = suggestion.suggestions || {};
            const modal = createModal(`
                <h3 class='font-bold text-lg mb-4 gradient-text'>Edit Suggestions</h3>
                <form id='edit-suggestion-form' class='space-y-3'>
                    <textarea name='suggestions' class='w-full border rounded px-3 py-2' placeholder='One suggestion per line'>${Object.values(suggestions).join('\n')}</textarea>
                    <div class='flex gap-2 mt-4'>
                        <button type='submit' class='bg-blue-600 text-white px-4 py-2 rounded'>Save</button>
                        <button type='button' class='close-modal px-4 py-2 rounded border'>Cancel</button>
                    </div>
                </form>
            `);
            modal.querySelector('.close-modal').onclick = () => modal.remove();
            modal.querySelector('#edit-suggestion-form').onsubmit = async function(e) {
                e.preventDefault();
                const form = e.target;
                const lines = form.suggestions.value.split('\n').map(s => s.trim()).filter(Boolean);
                const data = { suggestions: {} };
                lines.forEach((line, i) => data.suggestions[`q${i+1}`] = line);
                const res2 = await fetch(`/api/v1/chatbot/${chatbot_id}/suggestions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (res2.ok) {
                    modal.remove();
                    loadSuggestions();
                } else {
                    alert('Failed to update suggestions.');
                }
            };
        };
    });
}
document.querySelector('.add-suggestion-btn').onclick = () => alert('To add suggestions, create a chatbot first.');
filterTable('search-suggestions', 'suggestions-table');

// --- TENANTS (BUSINESS PROFILES) CRUD ---
async function loadTenants() {
    const res = await fetch('/api/v1/tenant/');
    const tenants = await res.json();
    const table = document.getElementById('tenants-table');
    table.innerHTML = '';
    for (const t of tenants) {
        let ownerId = t.owner_id || '';
        let ownerEmail = t.owner_email || '';
        if ((!ownerId || !ownerEmail) && t.id) {
            // Try to fetch the first user with this business_profile_id
            try {
                const usersRes = await fetch('/api/v1/auth/user/all');
                if (usersRes.ok) {
                    const users = await usersRes.json();
                    const owner = users.find(u => u.business_profile_id === t.id);
                    if (owner) {
                        ownerId = owner.id;
                        ownerEmail = owner.email;
                    }
                }
            } catch {}
        }
        const tr = document.createElement('tr');
        tr.className = 'border-b border-gray-200 dark:border-slate-700';
        tr.innerHTML = `
            <td class="py-2 px-4">${t.name}</td>
            <td class="py-2 px-4">${ownerEmail}</td>
            <td class="py-2 px-4">${ownerId}</td>
            <td class="py-2 px-4">${t.id}</td>
            <td class="py-2 px-4 truncate max-w-xs">${JSON.stringify(t.settings)}</td>
            <td class="py-2 px-4 flex gap-2">
                <button class="edit-tenant-btn bg-blue-500 hover:bg-blue-700 text-white px-2 py-1 rounded text-xs" data-id="${t.id}">Edit</button>
                <button class="delete-tenant-btn bg-red-500 hover:bg-red-700 text-white px-2 py-1 rounded text-xs" data-id="${t.id}">Delete</button>
            </td>
        `;
        table.appendChild(tr);
    }
    bindTenantActions();
}
function bindTenantActions() {
    document.querySelectorAll('.edit-tenant-btn').forEach(btn => {
        btn.onclick = function() {
            const row = btn.closest('tr');
            const id = btn.dataset.id;
            const name = row.children[0].innerText;
            const settings = row.children[4].innerText;
            const modal = createModal(`
                <h3 class='font-bold text-lg mb-4 gradient-text'>Edit Business Profile</h3>
                <form id='edit-tenant-form' class='space-y-3'>
                    <input type='text' name='name' class='w-full border rounded px-3 py-2' value='${name}' placeholder='Name' required />
                    <textarea name='settings' class='w-full border rounded px-3 py-2' placeholder='Settings (JSON)'>${settings}</textarea>
                    <div class='flex gap-2 mt-4'>
                        <button type='submit' class='bg-blue-600 text-white px-4 py-2 rounded'>Save</button>
                        <button type='button' class='close-modal px-4 py-2 rounded border'>Cancel</button>
                    </div>
                </form>
            `);
            modal.querySelector('.close-modal').onclick = () => modal.remove();
            modal.querySelector('#edit-tenant-form').onsubmit = async function(e) {
                e.preventDefault();
                const form = e.target;
                let settings;
                try {
                    settings = JSON.parse(form.settings.value);
                } catch {
                    alert('Invalid JSON in settings!');
                    return;
                }
                const data = {
                    name: form.name.value,
                    settings: settings
                };
                const res = await fetch(`/api/v1/tenant/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (res.ok) {
                    modal.remove();
                    loadTenants();
                } else {
                    alert('Failed to update business profile.');
                }
            };
        };
    });
    document.querySelectorAll('.delete-tenant-btn').forEach(btn => {
        btn.onclick = async function() {
            if (!confirm('Delete this business profile?')) return;
            const id = btn.dataset.id;
            const res = await fetch(`/api/v1/tenant/${id}`, { method: 'DELETE' });
            if (res.ok) loadTenants();
            else alert('Failed to delete business profile.');
        };
    });
}
function addTenantModal() {
    const modal = createModal(`
        <h3 class='font-bold text-lg mb-4 gradient-text'>Add Business Profile</h3>
        <form id='add-tenant-form' class='space-y-3'>
            <input type='text' name='name' class='w-full border rounded px-3 py-2' placeholder='Name' required />
            <textarea name='settings' class='w-full border rounded px-3 py-2' placeholder='Settings (JSON)'></textarea>
            <div class='flex gap-2 mt-4'>
                <button type='submit' class='bg-blue-600 text-white px-4 py-2 rounded'>Add</button>
                <button type='button' class='close-modal px-4 py-2 rounded border'>Cancel</button>
            </div>
        </form>
    `);
    modal.querySelector('.close-modal').onclick = () => modal.remove();
    modal.querySelector('#add-tenant-form').onsubmit = async function(e) {
        e.preventDefault();
        const form = e.target;
        let settings = {};
        try {
            settings = form.settings.value ? JSON.parse(form.settings.value) : {};
        } catch {
            alert('Invalid JSON in settings!');
            return;
        }
        const data = {
            name: form.name.value,
            settings: settings
        };
        const res = await fetch('/api/v1/tenant/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            modal.remove();
            loadTenants();
        } else {
            alert('Failed to add business profile.');
        }
    };
}
document.querySelector('.add-tenant-btn').onclick = addTenantModal;
filterTable('search-tenants', 'tenants-table');

// --- BUSINESS DOCUMENTS CRUD ---
async function loadDocuments() {
    // For demo, load all tenants and their documents
    const tenantsRes = await fetch('/api/v1/tenant/');
    const tenants = await tenantsRes.json();
    const table = document.getElementById('documents-table');
    table.innerHTML = '';
    for (const t of tenants) {
        const docsRes = await fetch(`/api/v1/tenant/business-document/?business_profile_id=${t.id}`);
        if (!docsRes.ok) continue;
        const docs = await docsRes.json();
        docs.forEach(doc => {
            const uploaded = doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleString() : '';
            const tr = document.createElement('tr');
            tr.className = 'border-b border-gray-200 dark:border-slate-700';
            tr.innerHTML = `
                <td class="py-2 px-4">${doc.filename || doc.url || ''}</td>
                <td class="py-2 px-4">${doc.type}</td>
                <td class="py-2 px-4">${t.name}</td>
                <td class="py-2 px-4">${uploaded}</td>
                <td class="py-2 px-4 flex gap-2">
                    <button class="view-document-btn bg-blue-500 hover:bg-blue-700 text-white px-2 py-1 rounded text-xs" data-id="${doc.id}">View</button>
                    <button class="delete-document-btn bg-red-500 hover:bg-red-700 text-white px-2 py-1 rounded text-xs" data-id="${doc.id}">Delete</button>
                    <a href="/api/v1/tenant/business-document/${doc.id}/download" class="bg-green-500 hover:bg-green-700 text-white px-2 py-1 rounded text-xs" target="_blank">Download</a>
                </td>
            `;
            table.appendChild(tr);
        });
    }
    bindDocumentActions();
    bindViewDocumentActions();
}
function bindDocumentActions() {
    document.querySelectorAll('.delete-document-btn').forEach(btn => {
        btn.onclick = async function() {
            if (!confirm('Delete this document?')) return;
            const id = btn.dataset.id;
            const res = await fetch(`/api/v1/tenant/business-document/${id}`, { method: 'DELETE' });
            if (res.ok) loadDocuments();
            else alert('Failed to delete document.');
        };
    });
}
function bindViewDocumentActions() {
    document.querySelectorAll('.view-document-btn').forEach(btn => {
        btn.onclick = async function() {
            const id = btn.dataset.id;
            const res = await fetch(`/api/v1/tenant/business-document/${id}/preview`);
            if (!res.ok) return alert('Failed to load document preview.');
            const data = await res.json();
            let content = '';
            if (data.text) {
                content = `<pre style='max-height:400px;overflow:auto;'>${data.text}</pre>`;
            } else if (data.rows) {
                content = '<table class="w-full text-xs">' + data.rows.map(row => `<tr>${row.map(cell => `<td class='border px-1'>${cell}</td>`).join('')}</tr>`).join('') + '</table>';
            } else if (data.error) {
                content = `<div class='text-red-600'>Error: ${data.error}</div>`;
            } else {
                content = '<div>No extracted data available.</div>';
            }
            createModal(`<h3 class='font-bold text-lg mb-4 gradient-text'>Extracted Data</h3>${content}`);
        };
    });
}
function addDocumentModal() {
    // To add a document, select tenant, type, and upload file or enter URL
    fetch('/api/v1/tenant/').then(res => res.json()).then(tenants => {
        const modal = createModal(`
            <h3 class='font-bold text-lg mb-4 gradient-text'>Add Document</h3>
            <form id='add-document-form' class='space-y-3'>
                <select name='business_profile_id' class='w-full border rounded px-3 py-2' required>
                    <option value=''>Select Business Profile</option>
                    ${tenants.map(t => `<option value='${t.id}'>${t.name}</option>`).join('')}
                </select>
                <input type='text' name='type' class='w-full border rounded px-3 py-2' placeholder='Type (e.g. pdf, csv)' required />
                <input type='file' name='file' class='w-full border rounded px-3 py-2' />
                <input type='url' name='url' class='w-full border rounded px-3 py-2' placeholder='Or enter URL' />
                <div class='flex gap-2 mt-4'>
                    <button type='submit' class='bg-blue-600 text-white px-4 py-2 rounded'>Add</button>
                    <button type='button' class='close-modal px-4 py-2 rounded border'>Cancel</button>
                </div>
            </form>
        `);
        modal.querySelector('.close-modal').onclick = () => modal.remove();
        modal.querySelector('#add-document-form').onsubmit = async function(e) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            const res = await fetch('/api/v1/tenant/business-document/', {
                method: 'POST',
                body: formData
            });
            if (res.ok) {
                modal.remove();
                loadDocuments();
            } else {
                alert('Failed to add document.');
            }
        };
    });
}
document.querySelector('.add-document-btn').onclick = addDocumentModal;
filterTable('search-documents', 'documents-table');

// --- INIT LOADERS ---
window.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    loadChatbots();
    loadSuggestions();
    loadTenants();
    loadDocuments();
}); 