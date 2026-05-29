const API_BASE_URL = window.location.origin + '/api';

const Auth = {
    salvarSessao: (token, usuario) => {
        localStorage.setItem('recebi_token', token);
        localStorage.setItem('recebi_usuario', JSON.stringify(usuario));
    },

    getToken: () => localStorage.getItem('recebi_token'),

    getUsuario: () => {
        const u = localStorage.getItem('recebi_usuario');
        return u ? JSON.parse(u) : null;
    },

    logout: () => {
        const usuario = Auth.getUsuario();
        const token = Auth.getToken();
        if (usuario && token) {
            fetch(`${API_BASE_URL}/usuario/logout/${usuario.IdUsuario}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }).catch(err => console.log("Logout request failed:", err));
        }
        localStorage.removeItem('recebi_token');
        localStorage.removeItem('recebi_usuario');
        window.location.href = '/index.html';
    },

    isAutenticado: () => !!localStorage.getItem('recebi_token')
};
