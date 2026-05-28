document.addEventListener('DOMContentLoaded', () => {
    // Se já estiver logado, nem deixa ver a tela de login
    if (Auth.isAutenticado()) {
        redirecionarPorPerfil(Auth.getUsuario().TipoUsuario);
    }

    const form = document.getElementById('login-form');
    const errorDiv = document.getElementById('error-message');
    const btnLogin = document.getElementById('btn-login');

    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Impede a página de recarregar

        // Pega os valores dos inputs
        const email = document.getElementById('email').value;
        const senha = document.getElementById('senha').value;

        // Limpa erros anteriores e desabilita o botão
        errorDiv.classList.add('hidden');
        errorDiv.textContent = '';
        btnLogin.textContent = 'Autenticando...';
        btnLogin.disabled = true;

        try {
            const response = await fetch(`${API_BASE_URL}/usuario/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, senha })
            });

            const data = await response.json();

            if (!response.ok) {
                // Se o backend retornou erro (ex: 401 Credenciais inválidas)
                throw new Error(data.message || 'Erro ao realizar login.');
            }

            // Deu certo! Salva o token e redireciona
            Auth.salvarSessao(data.token, data.usuario);
            redirecionarPorPerfil(data.usuario.TipoUsuario);

        } catch (error) {
            // Mostra o erro na tela
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('hidden');
        } finally {
            // Restaura o botão
            btnLogin.textContent = 'Entrar';
            btnLogin.disabled = false;
        }
    });

    // Função para rotear o usuário para a página correta
    function redirecionarPorPerfil(perfil) {
        const p = perfil.toLowerCase();
        if (p === 'sindico') {
            window.location.href = '../sindico/sindico.html';
        } else if (p === 'porteiro') {
            window.location.href = '../porteiro/porteiro.html';
        } else if (p === 'morador') {
            window.location.href = '../morador/morador.html';
        } else {
            Auth.logout();
        }
    }
});