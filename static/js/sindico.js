document.addEventListener('DOMContentLoaded', () => {
    // --- 1. ROUTE PROTECTION ---
    if (!Auth.isAutenticado() || Auth.getUsuario().TipoUsuario.toLowerCase() !== 'sindico') {
        alert('Acesso negado. Esta página é restrita a Síndicos.');
        Auth.logout();
        return;
    }

    const usuario = Auth.getUsuario();
    const userNameEl = document.getElementById('user-name');
    if (userNameEl) {
        userNameEl.textContent = `👤 ${usuario.Nome}`;
    }

    // --- 2. LOGOUT ---
    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
        btnLogout.addEventListener('click', () => {
            Auth.logout();
        });
    }

    // --- 3. TAB NAVIGATION ---
    const menuUsuarios = document.getElementById('menu-usuarios');
    const menuLogs = document.getElementById('menu-logs');
    const tituloPagina = document.getElementById('titulo-pagina');
    const btnNovoUsuario = document.getElementById('btn-novo-usuario');
    const tabelaContainer = document.getElementById('tabela-container');

    let currentTab = 'usuarios';

    if (menuUsuarios && menuLogs) {
        menuUsuarios.addEventListener('click', () => {
            currentTab = 'usuarios';
            mudarAbaAtiva(menuUsuarios, menuLogs);
            tituloPagina.textContent = 'Usuários do Sistema';
            btnNovoUsuario.classList.remove('hidden');
            carregarUsuarios();
        });

        menuLogs.addEventListener('click', () => {
            currentTab = 'logs';
            mudarAbaAtiva(menuLogs, menuUsuarios);
            tituloPagina.textContent = 'Logs de Auditoria';
            btnNovoUsuario.classList.add('hidden');
            carregarLogs();
        });
    }

    function mudarAbaAtiva(abaAtiva, abaInativa) {
        abaAtiva.classList.add('bg-indigo-600', 'text-white');
        abaAtiva.classList.remove('text-slate-300', 'hover:bg-slate-800');
        abaInativa.classList.remove('bg-indigo-600', 'text-white');
        abaInativa.classList.add('text-slate-300', 'hover:bg-slate-800');
    }

    // --- 4. API CALLS ---
    async function carregarUsuarios() {
        tabelaContainer.innerHTML = '<div class="p-6 text-center text-slate-500">Carregando usuários...</div>';
        try {
            const token = Auth.getToken();
            const response = await fetch(`${API_BASE_URL}/sindico/usuarios`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.message || 'Erro ao carregar usuários.');

            if (!Array.isArray(data) || data.length === 0) {
                tabelaContainer.innerHTML = '<div class="p-6 text-center text-slate-500">Nenhum usuário cadastrado.</div>';
                return;
            }

            let html = `
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 text-slate-600 text-xs font-semibold uppercase border-b border-slate-200">
                            <th class="p-4">Nome</th>
                            <th class="p-4">E-mail</th>
                            <th class="p-4">Perfil</th>
                            <th class="p-4">Apt</th>
                            <th class="p-4">Status</th>
                            <th class="p-4 text-center">Ações</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 text-sm">
            `;

            data.forEach(u => {
                const statusBadge = u.Status === 'Ativo' 
                    ? '<span class="px-2 py-1 text-xs font-semibold text-emerald-800 bg-emerald-100 rounded-full">Ativo</span>'
                    : '<span class="px-2 py-1 text-xs font-semibold text-rose-800 bg-rose-100 rounded-full">Inativo</span>';

                html += `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-4 font-medium text-slate-900">${u.Nome}</td>
                        <td class="p-4 text-slate-600">${u.Email}</td>
                        <td class="p-4 text-slate-600 font-semibold">${u.TipoUsuario}</td>
                        <td class="p-4 text-slate-600">${u.Apartamento || '-'}</td>
                        <td class="p-4">${statusBadge}</td>
                        <td class="p-4 text-center space-x-2">
                            <button onclick="editarUsuario(${u.IdUsuario}, '${u.Nome}', '${u.Email}', '${u.TipoUsuario}', '${u.Apartamento || ''}')" class="px-3 py-1 bg-indigo-50 text-indigo-600 hover:bg-indigo-100 rounded transition font-medium">Editar</button>
                            <button onclick="toggleUsuarioStatus(${u.IdUsuario}, '${u.Status === 'Ativo' ? 'Inativo' : 'Ativo'}')" class="px-3 py-1 ${u.Status === 'Ativo' ? 'bg-rose-50 text-rose-600 hover:bg-rose-100' : 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100'} rounded transition font-medium">
                                ${u.Status === 'Ativo' ? 'Inativar' : 'Ativar'}
                            </button>
                        </td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            tabelaContainer.innerHTML = html;

        } catch (error) {
            tabelaContainer.innerHTML = `<div class="p-6 text-center text-rose-500 font-medium">${error.message}</div>`;
        }
    }

    async function carregarLogs() {
        tabelaContainer.innerHTML = '<div class="p-6 text-center text-slate-500">Carregando logs de auditoria...</div>';
        try {
            const token = Auth.getToken();
            const response = await fetch(`${API_BASE_URL}/sindico/logs`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();

            if (!response.ok) throw new Error(data.message || 'Erro ao carregar logs.');

            if (!Array.isArray(data) || data.length === 0) {
                tabelaContainer.innerHTML = '<div class="p-6 text-center text-slate-500">Nenhum registro de log encontrado.</div>';
                return;
            }

            let html = `
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 text-slate-600 text-xs font-semibold uppercase border-b border-slate-200">
                            <th class="p-4">Data/Hora</th>
                            <th class="p-4">Responsável</th>
                            <th class="p-4">Ação</th>
                            <th class="p-4">Detalhes</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 text-xs text-slate-600">
            `;

            data.forEach(log => {
                const dateFormatted = new Date(log.DataHora).toLocaleString('pt-BR');
                const detailsText = log.Detalhes ? JSON.stringify(log.Detalhes) : '-';

                html += `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-4 whitespace-nowrap font-medium text-slate-900">${dateFormatted}</td>
                        <td class="p-4 font-semibold text-slate-700">${log.Usuario}</td>
                        <td class="p-4 text-slate-900 font-medium">${log.Acao}</td>
                        <td class="p-4 max-w-xs truncate" title='${detailsText}'>${detailsText}</td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            tabelaContainer.innerHTML = html;

        } catch (error) {
            tabelaContainer.innerHTML = `<div class="p-6 text-center text-rose-500 font-medium">${error.message}</div>`;
        }
    }

    // --- 5. MODAL SYSTEM FOR CREATE/EDIT ---
    window.editarUsuario = (id, nome, email, tipoUsuario, apartamento) => {
        abrirModal(id, nome, email, tipoUsuario, apartamento);
    };

    window.toggleUsuarioStatus = async (id, novoStatus) => {
        if (!confirm(`Deseja alterar o status do usuário para ${novoStatus}?`)) return;
        try {
            const token = Auth.getToken();
            const response = await fetch(`${API_BASE_URL}/sindico/atualizar/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ status: novoStatus })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.message || 'Erro ao atualizar status.');

            alert('Status atualizado com sucesso!');
            carregarUsuarios();

        } catch (error) {
            alert(error.message);
        }
    };

    btnNovoUsuario.addEventListener('click', () => {
        abrirModal();
    });

    function abrirModal(id = null, nome = '', email = '', tipoUsuario = 'Morador', apartamento = '') {
        // Remove existing modal if any
        const existing = document.getElementById('user-modal');
        if (existing) existing.remove();

        const modalHtml = `
            <div id="user-modal" class="fixed inset-0 bg-slate-900 bg-opacity-50 flex items-center justify-center p-4 z-50 animate-fade-in">
                <div class="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
                    <div class="px-6 py-4 bg-slate-900 text-white flex justify-between items-center">
                        <h3 class="text-lg font-bold">${id ? 'Editar Usuário' : 'Novo Usuário'}</h3>
                        <button onclick="document.getElementById('user-modal').remove()" class="text-slate-400 hover:text-white">&times;</button>
                    </div>
                    <form id="modal-form" class="p-6 space-y-4">
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Nome</label>
                            <input type="text" id="modal-nome" required value="${nome}" class="w-full px-3 py-2 border border-slate-300 rounded focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">E-mail</label>
                            <input type="email" id="modal-email" required value="${email}" class="w-full px-3 py-2 border border-slate-300 rounded focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                        </div>
                        ${id ? '' : `
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Senha</label>
                            <input type="password" id="modal-senha" required class="w-full px-3 py-2 border border-slate-300 rounded focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                        </div>
                        `}
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Perfil</label>
                            <select id="modal-perfil" class="w-full px-3 py-2 border border-slate-300 rounded focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                                <option value="Morador" ${tipoUsuario === 'Morador' ? 'selected' : ''}>Morador</option>
                                <option value="Porteiro" ${tipoUsuario === 'Porteiro' ? 'selected' : ''}>Porteiro</option>
                                <option value="Sindico" ${tipoUsuario === 'Sindico' ? 'selected' : ''}>Síndico</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Apartamento (opcional)</label>
                            <input type="text" id="modal-apartamento" value="${apartamento}" class="w-full px-3 py-2 border border-slate-300 rounded focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                        </div>
                        
                        <div class="pt-4 flex justify-end space-x-2 border-t border-slate-100">
                            <button type="button" onclick="document.getElementById('user-modal').remove()" class="px-4 py-2 border border-slate-300 text-slate-700 rounded text-sm hover:bg-slate-50 transition">Cancelar</button>
                            <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700 transition">Salvar</button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        const form = document.getElementById('modal-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = Auth.getToken();

            const bodyData = {
                nome: document.getElementById('modal-nome').value.trim(),
                email: document.getElementById('modal-email').value.trim(),
                tipoUsuario: document.getElementById('modal-perfil').value,
                apartamento: document.getElementById('modal-apartamento').value.trim() || null
            };

            const url = id 
                ? `${API_BASE_URL}/sindico/atualizar/${id}`
                : `${API_BASE_URL}/sindico/criar`;

            if (!id) {
                bodyData.senha = document.getElementById('modal-senha').value.trim();
            }

            try {
                const response = await fetch(url, {
                    method: id ? 'PUT' : 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(bodyData)
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.message || 'Erro ao salvar dados.');

                alert('Dados salvos com sucesso!');
                document.getElementById('user-modal').remove();
                carregarUsuarios();

            } catch (error) {
                alert(error.message);
            }
        });
    }

    // Default load
    carregarUsuarios();
});
