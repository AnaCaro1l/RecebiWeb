// Recebi API Configuration
const API_BASE_URL = window.location.origin + '/api';

const Auth = {
    // Save authentication details
    salvarSessao: (token, usuario) => {
        localStorage.setItem('recebi_token', token);
        localStorage.setItem('recebi_usuario', JSON.stringify(usuario));
    },

    // Retrieve active JWT token
    getToken: () => localStorage.getItem('recebi_token'),

    // Retrieve active user profile
    getUsuario: () => {
        const u = localStorage.getItem('recebi_usuario');
        return u ? JSON.parse(u) : null;
    },

    // Clear local storage and log out user
    logout: () => {
        const usuario = Auth.getUsuario();
        const token = Auth.getToken();
        if (usuario && token) {
            // Non-blocking logout call to server
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

    // Check if user session exists
    isAutenticado: () => !!localStorage.getItem('recebi_token')
};
