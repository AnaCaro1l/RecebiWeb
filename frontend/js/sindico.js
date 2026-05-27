document.addEventListener('DOMContentLoaded', () => {
    // --- 1. PROTEÇÃO DE ROTA ---
    // Se não tiver token ou o perfil não for Síndico, bloqueia o acesso
    if (!Auth.isAutenticado() || Auth.getUsuario().TipoUsuario.toLowerCase() !== 'sindico') {
        alert('Acesso negado. Esta página é restrita a Síndicos.');
        Auth.logout();
        return;
    }

    // --- 2. DADOS DO USUÁRIO ---
    const usuario = Auth.getUsuario();
    document.getElementById('user-name').textContent = `👤 ${usuario.Nome}`;

    // --- 3. EVENTO DE LOGOUT ---
    document.getElementById('btn-logout').addEventListener('click', () => {
        Auth.logout();
    });

    // --- 4. NAVEGAÇÃO INTERNA ---
    const menuUsuarios = document.getElementById('menu-usuarios');
    const menuLogs = document.getElementById('menu-logs');
    const tituloPagina = document.getElementById('titulo-pagina');
    const btnNovoUsuario = document.getElementById('btn-novo-usuario');
    const tabelaContainer = document.getElementById('tabela-container');

    menuUsuarios.addEventListener('click', () => {
        mudarAbaAtiva(menuUsuarios, menuLogs);
        tituloPagina.textContent = 'Usuários do Sistema';
        btnNovoUsuario.classList.remove('hidden');
        carregarUsuarios();
    });

    menuLogs.addEventListener('click', () => {
        mudarAbaAtiva(menuLogs, menuUsuarios);
        tituloPagina.textContent = 'Logs de Auditoria';
        btnNovoUsuario.classList.add('hidden'); // Esconde o botão de novo usuário na aba de logs
        carregarLogs();
    });

    // Função visual para trocar a cor do botão ativo no menu
    function mudarAbaAtiva(abaAtiva, abaInativa) {
        abaAtiva.classList.add('bg-indigo-600', 'text-white');
        abaAtiva.classList.remove('text-slate-300', 'hover:bg-slate-800');
        
        abaInativa.classList.remove('bg-indigo-600', 'text-white');
        abaInativa.classList.add('text-slate-300', 'hover:bg-slate-800');
    }

    // --- 5. CHAMADAS PARA A API (A implementar no próximo passo) ---
    async function carregarUsuarios() {
        tabelaContainer.innerHTML = '<p class="text-slate-500 py-4">Injetaremos a requisição Fetch (GET /api/sindico/usuarios) aqui.</p>';
    }

    async function carregarLogs() {
        tabelaContainer.innerHTML = '<p class="text-slate-500 py-4">Injetaremos a requisição Fetch (GET /api/sindico/logs) aqui.</p>';
    }

    // Inicia a página carregando os usuários por padrão
    carregarUsuarios();
});