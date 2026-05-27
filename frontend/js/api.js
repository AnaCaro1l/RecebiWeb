// Configuração global da API
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Objeto auxiliar para gerenciar a autenticação e chamadas
const Auth = {
    // Salva os dados no navegador
    salvarSessao: (token, usuario) => {
        localStorage.setItem('recebi_token', token);
        localStorage.setItem('recebi_usuario', JSON.stringify(usuario));
    },

    // Pega o token para colocar no cabeçalho das requisições
    getToken: () => localStorage.getItem('recebi_token'),

    // Pega os dados do usuário logado (ex: para mostrar o nome dele na tela)
    getUsuario: () => JSON.parse(localStorage.getItem('recebi_usuario')),

    // Limpa tudo e desloga
    logout: () => {
        localStorage.removeItem('recebi_token');
        localStorage.removeItem('recebi_usuario');
        window.location.href = 'index.html'; // Redireciona pro login
    },

    // Verifica se está logado
    isAutenticado: () => !!localStorage.getItem('recebi_token')
};