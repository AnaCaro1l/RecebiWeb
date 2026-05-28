document.addEventListener('DOMContentLoaded', () => {
    // 1. PROTEÇÃO DE ROTA (Auth Guard)
    if (!Auth.isAutenticado() || Auth.getUsuario().TipoUsuario.toLowerCase() !== 'sindico') {
        alert('Acesso negado. Área restrita a Síndicos.');
        Auth.logout();
        return;
    }

    // 2. DADOS DO USUÁRIO LOGADO
    document.getElementById('user-name').textContent = Auth.getUsuario().Nome;

    // 3. EVENTO DE LOGOUT
    document.getElementById('btn-logout').addEventListener('click', () => Auth.logout());

    // 4. ELEMENTOS DA TELA
    const menuUsuarios = document.getElementById('menu-usuarios');
    const menuLogs = document.getElementById('menu-logs');
    const tituloPagina = document.getElementById('titulo-pagina');
    const btnNovoUsuario = document.getElementById('btn-novo-usuario');
    const tabelaContainer = document.getElementById('tabela-container');

    // 5. LÓGICA DE NAVEGAÇÃO (MENU LATERAL)
    menuUsuarios.addEventListener('click', () => {
        mudarAbaAtiva(menuUsuarios, menuLogs);
        tituloPagina.textContent = 'Usuários do Sistema';
        btnNovoUsuario.classList.remove('hidden');
        carregarUsuarios();
    });

    menuLogs.addEventListener('click', () => {
        mudarAbaAtiva(menuLogs, menuUsuarios);
        tituloPagina.textContent = 'Logs de Auditoria';
        btnNovoUsuario.classList.add('hidden'); // Esconde o botão de "+ Novo Usuário" nos logs
        carregarLogs();
    });

    // Função visual para trocar a cor do menu selecionado
    function mudarAbaAtiva(abaAtiva, abaInativa) {
        // Estilo do botão clicado (Ativo)
        abaAtiva.className = "w-full text-left px-4 py-3 rounded-md bg-[#4a90e2] text-white font-medium transition-colors";
        // Estilo do botão não clicado (Inativo)
        abaInativa.className = "w-full text-left px-4 py-3 rounded-md text-slate-600 hover:bg-slate-200 font-medium transition-colors";
    }

    // 6. COMUNICAÇÃO COM A API (FETCH)
    async function carregarUsuarios() {
        tabelaContainer.innerHTML = '<p class="text-center text-slate-500 py-8">Carregando usuários...</p>';
        try {
            const response = await fetch(`${API_BASE_URL}/sindico/usuarios`, {
                headers: { 'Authorization': `Bearer ${Auth.getToken()}` }
            });
            const dados = await response.json();
            
            if (!response.ok) throw new Error(dados.message || 'Erro ao carregar usuários');

            if (dados.message) {
                tabelaContainer.innerHTML = `<p class="text-center text-slate-500 py-8">${dados.message}</p>`;
                return;
            }

            renderizarTabelaUsuarios(dados);
        } catch (error) {
            tabelaContainer.innerHTML = `<p class="text-center text-red-500 py-8">${error.message}</p>`;
        }
    }

    async function carregarLogs() {
        tabelaContainer.innerHTML = '<p class="text-center text-slate-500 py-8">Carregando logs...</p>';
        try {
            const response = await fetch(`${API_BASE_URL}/sindico/logs`, {
                headers: { 'Authorization': `Bearer ${Auth.getToken()}` }
            });
            const dados = await response.json();
            
            if (!response.ok) throw new Error(dados.message || 'Erro ao carregar logs');

            if (dados.message) {
                tabelaContainer.innerHTML = `<p class="text-center text-slate-500 py-8">${dados.message}</p>`;
                return;
            }

            renderizarTabelaLogs(dados);
        } catch (error) {
            tabelaContainer.innerHTML = `<p class="text-center text-red-500 py-8">${error.message}</p>`;
        }
    }

    // 7. RENDERIZAÇÃO DAS TABELAS NO HTML
    function renderizarTabelaUsuarios(usuarios) {
        let html = `
            <table class="w-full text-sm text-left text-slate-500">
                <thead class="text-xs text-slate-700 uppercase bg-slate-100 border-b border-slate-200">
                    <tr>
                        <th class="px-6 py-3">Nome</th>
                        <th class="px-6 py-3">E-mail</th>
                        <th class="px-6 py-3">Perfil</th>
                        <th class="px-6 py-3">Apt</th>
                        <th class="px-6 py-3 text-center">Status</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
        `;

        usuarios.forEach(u => {
            const statusClass = u.Status === 'Ativo' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
            html += `
                <tr class="bg-white hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-4 font-medium text-slate-900">${u.Nome}</td>
                    <td class="px-6 py-4">${u.Email}</td>
                    <td class="px-6 py-4 capitalize">${u.TipoUsuario}</td>
                    <td class="px-6 py-4">${u.Apartamento || '-'}</td>
                    <td class="px-6 py-4 text-center">
                        <span class="px-2.5 py-0.5 rounded text-xs font-medium ${statusClass}">${u.Status}</span>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        tabelaContainer.innerHTML = html;
    }

    function renderizarTabelaLogs(logs) {
        let html = `
            <table class="w-full text-sm text-left text-slate-500">
                <thead class="text-xs text-slate-700 uppercase bg-slate-100 border-b border-slate-200">
                    <tr>
                        <th class="px-6 py-3">Data/Hora</th>
                        <th class="px-6 py-3">Ação</th>
                        <th class="px-6 py-3">Responsável</th>
                        <th class="px-6 py-3">Detalhes</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
        `;

        logs.forEach(l => {
            const dataFormatada = new Date(l.DataHora).toLocaleString('pt-BR');
            html += `
                <tr class="bg-white hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-4 whitespace-nowrap">${dataFormatada}</td>
                    <td class="px-6 py-4 font-medium text-slate-900">${l.Acao}</td>
                    <td class="px-6 py-4">${l.Usuario}</td>
                    <td class="px-6 py-4 text-xs">
                        ${l.EncomendaDescricao !== 'Sem referência' ? `Ref: ${l.EncomendaDescricao}` : 'N/A'}
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        tabelaContainer.innerHTML = html;
    }

    // Ao abrir a página, simula um clique na aba de usuários para carregar a lista inicial
    menuUsuarios.click();
});