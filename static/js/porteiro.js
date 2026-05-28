document.addEventListener('DOMContentLoaded', () => {
    // 1. PROTEÇÃO DE ROTA
    if (!Auth.isAutenticado() || Auth.getUsuario().TipoUsuario.toLowerCase() !== 'porteiro') {
        alert('Acesso negado. Área restrita a Porteiros.');
        Auth.logout();
        return;
    }

    document.getElementById('user-name').textContent = Auth.getUsuario().Nome;
    document.getElementById('btn-logout').addEventListener('click', () => Auth.logout());

    // 2. CONTROLE DE ABAS E NAVEGAÇÃO
    const menuRegistrar = document.getElementById('menu-registrar');
    const menuLista = document.getElementById('menu-lista');
    const secaoRegistrar = document.getElementById('secao-registrar');
    const secaoLista = document.getElementById('secao-lista');
    const tabelaContainer = document.getElementById('tabela-container');

    menuRegistrar.addEventListener('click', () => {
        mudarAbaAtiva(menuRegistrar, menuLista);
        secaoRegistrar.classList.remove('hidden');
        secaoLista.classList.add('hidden');
    });

    menuLista.addEventListener('click', () => {
        mudarAbaAtiva(menuLista, menuRegistrar);
        secaoLista.classList.remove('hidden');
        secaoRegistrar.classList.add('hidden');
        carregarEncomendas();
    });

    function mudarAbaAtiva(abaAtiva, abaInativa) {
        abaAtiva.className = "w-full text-left px-4 py-3 rounded-md bg-[#4a90e2] text-white font-medium transition-colors";
        abaInativa.className = "w-full text-left px-4 py-3 rounded-md text-slate-600 hover:bg-slate-200 font-medium transition-colors";
    }

    // 3. LÓGICA DE BUSCA INTELIGENTE DE MORADORES
    const inputBusca = document.getElementById('busca-morador');
    const listaResultados = document.getElementById('lista-moradores');
    const inputMoradorId = document.getElementById('morador-id-selecionado');
    let timeoutBusca = null;

    inputBusca.addEventListener('input', (e) => {
        const termo = e.target.value.trim();
        inputMoradorId.value = ''; // Limpa a seleção anterior se o porteiro voltar a digitar
        
        clearTimeout(timeoutBusca);

        if (termo.length < 2) {
            listaResultados.classList.add('hidden');
            return;
        }

        // Aguarda 300ms depois que o usuário parar de digitar para não inundar o servidor (Debounce)
        timeoutBusca = setTimeout(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/porteiro/buscar-moradores?query=${termo}`, {
                    headers: { 'Authorization': `Bearer ${Auth.getToken()}` }
                });
                const moradores = await response.json();
                mostrarResultadosBusca(moradores);
            } catch (error) {
                console.error('Erro ao buscar moradores:', error);
            }
        }, 300);
    });

    function mostrarResultadosBusca(moradores) {
        listaResultados.innerHTML = '';
        if (moradores.length === 0) {
            listaResultados.innerHTML = '<li class="p-3 text-sm text-slate-500">Nenhum morador encontrado.</li>';
        } else {
            moradores.forEach(m => {
                const li = document.createElement('li');
                li.className = 'p-3 hover:bg-slate-100 cursor-pointer text-sm border-b border-slate-100 last:border-0';
                li.innerHTML = `<strong>Apt ${m.Apartamento || 'N/A'}</strong> - ${m.Nome}`;
                
                // Ao clicar no morador da lista
                li.addEventListener('click', () => {
                    inputBusca.value = `Apt ${m.Apartamento || 'N/A'} - ${m.Nome}`;
                    inputMoradorId.value = m.IdUsuario;
                    listaResultados.classList.add('hidden');
                });
                
                listaResultados.appendChild(li);
            });
        }
        listaResultados.classList.remove('hidden');
    }

    // Esconde a lista de resultados se clicar fora
    document.addEventListener('click', (e) => {
        if (e.target !== inputBusca && e.target !== listaResultados) {
            listaResultados.classList.add('hidden');
        }
    });

    // 4. LÓGICA DE REGISTRO DE ENCOMENDA
    const formEncomenda = document.getElementById('form-encomenda');
    const msgFeedback = document.getElementById('msg-feedback');
    const btnSalvar = document.getElementById('btn-salvar');

    formEncomenda.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const moradorId = inputMoradorId.value;
        const descricao = document.getElementById('descricao').value;
        const rastreio = document.getElementById('rastreio').value;

        if (!moradorId) {
            mostrarMensagem('Por favor, selecione um morador válido na lista.', 'erro');
            return;
        }

        btnSalvar.disabled = true;
        btnSalvar.textContent = 'Registrando...';

        try {
            const response = await fetch(`${API_BASE_URL}/porteiro/registrar-encomenda`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${Auth.getToken()}`
                },
                body: JSON.stringify({ 
                    morador_id: moradorId, 
                    descricao: descricao, 
                    codigo_rastreio: rastreio 
                })
            });

            const data = await response.json();

            if (!response.ok) throw new Error(data.message || 'Erro ao registrar encomenda.');

            mostrarMensagem('Encomenda registrada com sucesso!', 'sucesso');
            formEncomenda.reset();
            inputMoradorId.value = '';

        } catch (error) {
            mostrarMensagem(error.message, 'erro');
        } finally {
            btnSalvar.disabled = false;
            btnSalvar.textContent = 'Registrar Recebimento';
        }
    });

    function mostrarMensagem(texto, tipo) {
        msgFeedback.textContent = texto;
        msgFeedback.className = `mt-3 text-center text-sm p-2 rounded block ${
            tipo === 'sucesso' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'
        }`;
        setTimeout(() => msgFeedback.classList.add('hidden'), 5000);
    }

    // 5. CARREGAR TABELA DE ENCOMENDAS (ABA LISTA)
    async function carregarEncomendas() {
        tabelaContainer.innerHTML = '<p class="text-center text-slate-500 py-8">Carregando encomendas...</p>';
        try {
            const response = await fetch(`${API_BASE_URL}/porteiro/encomendas`, {
                headers: { 'Authorization': `Bearer ${Auth.getToken()}` }
            });
            const dados = await response.json();
            
            if (!response.ok) throw new Error(dados.message || 'Erro ao carregar dados');

            if (dados.message) {
                tabelaContainer.innerHTML = `<p class="text-center text-slate-500 py-8">${dados.message}</p>`;
                return;
            }

            renderizarTabelaEncomendas(dados);
        } catch (error) {
            tabelaContainer.innerHTML = `<p class="text-center text-red-500 py-8">${error.message}</p>`;
        }
    }

    function renderizarTabelaEncomendas(encomendas) {
        let html = `
            <table class="w-full text-sm text-left text-slate-500">
                <thead class="text-xs text-slate-700 uppercase bg-slate-100 border-b border-slate-200">
                    <tr>
                        <th class="px-6 py-3">Apt</th>
                        <th class="px-6 py-3">Morador</th>
                        <th class="px-6 py-3">Descrição</th>
                        <th class="px-6 py-3">Status</th>
                        <th class="px-6 py-3">Data/Hora de Entrada</th>
                    </tr>
                </thead>
                <tbody>
        `;

        encomendas.forEach(e => {
            const statusClass = e.Status === 'Pendente' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800';
            const dataFormatada = new Date(e.DataEntrada).toLocaleString('pt-BR');
            html += `
                <tr class="bg-white border-b hover:bg-slate-50">
                    <td class="px-6 py-4 font-bold text-slate-900">${e.Apartamento || 'N/A'}</td>
                    <td class="px-6 py-4">${e.Morador}</td>
                    <td class="px-6 py-4">
                        ${e.Descricao}
                        ${e.CodigoRastreio ? `<br><span class="text-xs text-slate-400">Rastreio: ${e.CodigoRastreio}</span>` : ''}
                    </td>
                    <td class="px-6 py-4">
                        <span class="px-2.5 py-0.5 rounded text-xs font-medium ${statusClass}">${e.Status}</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">${dataFormatada}</td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        tabelaContainer.innerHTML = html;
    }
});