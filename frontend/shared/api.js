const API_BASE_URL = 'http://127.0.0.1:5000/api';

const Auth = {
    salvarSessao: (token, usuario) => {
        localStorage.setItem('recebi_token', token);
        localStorage.setItem('recebi_usuario', JSON.stringify(usuario));
    },

    getToken: () => localStorage.getItem('recebi_token'),

    getUsuario: () => JSON.parse(localStorage.getItem('recebi_usuario')),

    logout: () => {
        localStorage.removeItem('recebi_token');
        localStorage.removeItem('recebi_usuario');
        window.location.href = '../login/index.html';
    },

    isAutenticado: () => !!localStorage.getItem('recebi_token')
};