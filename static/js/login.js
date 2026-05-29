document.addEventListener('DOMContentLoaded', () => {
    if (Auth.isAutenticado()) {
        redirecionarPorPerfil(Auth.getUsuario().TipoUsuario);
    }

    const form = document.getElementById('login-form');
    const errorDiv = document.getElementById('error-message');
    const btnLogin = document.getElementById('btn-login');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value.trim();
            const senha = document.getElementById('senha').value.trim();

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
                    throw new Error(data.message || 'E-mail ou senha incorretos.');
                }

                Auth.salvarSessao(data.token, data.usuario);
                redirecionarPorPerfil(data.usuario.TipoUsuario);

            } catch (error) {
                errorDiv.textContent = error.message;
                errorDiv.classList.remove('hidden');
            } finally {
                btnLogin.textContent = 'Entrar';
                btnLogin.disabled = false;
            }
        });
    }

    function redirecionarPorPerfil(perfil) {
        if (!perfil) return;
        const p = perfil.toLowerCase();
        if (p === 'sindico') {
            window.location.href = '/sindico.html';
        } else if (p === 'porteiro') {
            window.location.href = '/porteiro.html';
        } else if (p === 'morador') {
            window.location.href = '/morador.html';
        } else {
            Auth.logout();
        }
    }
});
