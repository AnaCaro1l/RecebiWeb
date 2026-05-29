document.addEventListener('DOMContentLoaded', () => {
    if (!Auth.isAutenticado() || Auth.getUsuario().TipoUsuario.toLowerCase() !== 'morador') {
        alert('Acesso negado. Área restrita a Moradores.');
        Auth.logout();
        return;
    }

    const usuario = Auth.getUsuario();
    document.getElementById('user-name').textContent = usuario.Nome;
    document.getElementById('user-apt').textContent = `Morador - Apt ${usuario.Apartamento || 'N/A'}`;
    
    document.getElementById('btn-logout').addEventListener('click', () => Auth.logout());

    const tabelaContainer = document.getElementById('tabela-container');
    const msgFeedback = document.getElementById('msg-feedback');

    let paginaAtual = 1;
    const filtroData = document.getElementById('filtro-morador-data');
    const filtroStatus = document.getElementById('filtro-morador-status');
    const btnLimpar = document.getElementById('btn-limpar-morador-filtros');
    
    const btnAnterior = document.getElementById('btn-morador-anterior');
    const btnProximo = document.getElementById('btn-morador-proximo');
    const textoPaginas = document.getElementById('texto-paginas-morador');
    const containerPaginacao = document.getElementById('paginacao-morador-container');

    const opcoesDataBR = {
        timeZone: 'America/Sao_Paulo',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };

    if (filtroStatus) {
        filtroStatus.addEventListener('change', () => {
            paginaAtual = 1; // Reseta para a primeira página ao alterar o status
            carregarMinhasEncomendas();
        });
    }

    if (filtroData) {
        filtroData.addEventListener('change', () => {
            paginaAtual = 1; // Reseta para a primeira página ao escolher uma nova data
            carregarMinhasEncomendas();
        });
    }

    if (btnLimpar) {
        btnLimpar.addEventListener('click', () => {
            filtroData.value = '';
            filtroStatus.value = 'Ambos';
            paginaAtual = 1;
            carregarMinhasEncomendas();
        });
    }

    // Lógica de clique nos botões de paginação
    if (btnAnterior && btnProximo) {
        btnAnterior.addEventListener('click', () => {
            if (paginaAtual > 1) {
                paginaAtual--;
                carregarMinhasEncomendas();
            }
        });

        btnProximo.addEventListener('click', () => {
            paginaAtual++;
            carregarMinhasEncomendas();
        });
    }

    // 4. BUSCAR AS ENCOMENDAS DO MORADOR (ATUALIZADA)
    async function carregarMinhasEncomendas() {
        tabelaContainer.innerHTML = '<p class="text-center text-slate-500 py-8">Carregando suas encomendas...</p>';
        try {
            const statusVal = filtroStatus ? filtroStatus.value : 'Ambos';
            const dataVal = filtroData ? filtroData.value.trim() : '';

            // Repassa os filtros e a página atual via query string para o Flask
            const url = `${API_BASE_URL}/morador/encomendas?page=${paginaAtual}&status=${statusVal}&data=${encodeURIComponent(dataVal)}`;

            const response = await fetch(url, {
                headers: { 'Authorization': `Bearer ${Auth.getToken()}` }
            });
            const dados = await response.json();
            
            if (!response.ok) throw new Error(dados.message || 'Erro ao carregar encomendas');

            if (!dados.encomendas || dados.encomendas.length === 0) {
                tabelaContainer.innerHTML = `<p class="text-center text-slate-500 py-8">Nenhuma encomenda encontrada para os filtros aplicados.</p>`;
                if (containerPaginacao) containerPaginacao.classList.add('hidden');
                return;
            }

            // Exibe e atualiza o estado dos botões com base no retorno do back-end
            if (containerPaginacao) containerPaginacao.classList.remove('hidden');
            if (textoPaginas && btnAnterior && btnProximo) {
                textoPaginas.textContent = `Página ${dados.paginacao.pagina_atual} de ${dados.paginacao.total_paginas}`;
                btnAnterior.disabled = !dados.paginacao.tem_anterior;
                btnProximo.disabled = !dados.paginacao.tem_proximo;
                paginaAtual = dados.paginacao.pagina_atual;
            }

            renderizarTabela(dados.encomendas);

        } catch (error) {
            tabelaContainer.innerHTML = `<p class="text-center text-red-500 py-8">${error.message}</p>`;
        }
    }

    // 5. RENDERIZAR TABELA COM DATA FORMATADA
    function renderizarTabela(encomendas) {
        let html = `
            <table class="w-full text-sm text-left text-slate-500">
                <thead class="text-xs text-slate-700 uppercase bg-slate-100 border-b border-slate-200">
                    <tr>
                        <th class="px-6 py-3">Descrição do Pacote</th>
                        <th class="px-6 py-3">Data de Chegada</th>
                        <th class="px-6 py-3">Status</th>
                        <th class="px-6 py-3 text-center">Ação</th>
                    </tr>
                </thead>
                <tbody>
        `;

        encomendas.forEach(e => {
            const dataChegada = e.DataEntrada ? new Date(e.DataEntrada).toLocaleString('pt-BR', opcoesDataBR) : 'N/A';
            const dataRetirada = e.DataRetirada ? new Date(e.DataRetirada).toLocaleString('pt-BR', opcoesDataBR) : null;
            
            const isPendente = e.Status === 'Pendente';
            const statusClass = isPendente ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800';

            html += `
                <tr class="bg-white border-b hover:bg-slate-50">
                    <td class="px-6 py-4">
                        <span class="font-medium text-slate-900 block">${e.Descricao}</span>
                        ${e.CodigoRastreio ? `<span class="text-xs text-slate-400">Rastreio: ${e.CodigoRastreio}</span>` : ''}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">${dataChegada}</td>
                    <td class="px-6 py-4">
                        <span class="px-2.5 py-0.5 rounded text-xs font-medium ${statusClass}">${e.Status}</span>
                    </td>
                    <td class="px-6 py-4 text-center">
                        ${isPendente 
                            ? `<button onclick="confirmarRecebimento(${e.IdEncomenda})" class="bg-[#4a90e2] text-white px-3 py-1.5 rounded shadow text-xs font-medium hover:bg-[#357abd] transition-colors">Confirmar Retirada</button>` 
                            : `<span class="text-xs text-slate-400 block">Retirada em:<br>${dataRetirada}</span>`
                        }
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        tabelaContainer.innerHTML = html;
    }

    // 6. FUNÇÃO GLOBAL PARA CONFIRMAR RECEBIMENTO
    window.confirmarRecebimento = async function(idEncomenda) {
        if (!confirm('Deseja confirmar que já está com esta encomenda em mãos?')) return;

        try {
            const response = await fetch(`${API_BASE_URL}/morador/confirmar-recebimento/${idEncomenda}`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${Auth.getToken()}` }
            });
            
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.message || data.erro || 'Erro ao confirmar.');

            mostrarMensagem('Recebimento confirmado com sucesso!', 'sucesso');
            carregarMinhasEncomendas(); 

        } catch (error) {
            mostrarMensagem(error.message, 'erro');
        }
    };

    function mostrarMensagem(texto, tipo) {
        msgFeedback.textContent = texto;
        msgFeedback.className = `mb-6 text-center text-sm p-3 rounded block ${
            tipo === 'sucesso' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'
        }`;
        setTimeout(() => msgFeedback.classList.add('hidden'), 4000);
    }

    // Chamada automática inicial
    carregarMinhasEncomendas();
});