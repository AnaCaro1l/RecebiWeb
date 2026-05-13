# [cite_start]Recebi - Sistema de Gestão de Encomendas para Condomínios [cite: 5]

[cite_start]O **Recebi** é uma plataforma digital centralizada desenvolvida para modernizar e otimizar a gestão e rastreabilidade de encomendas em condomínios residenciais[cite: 12, 17]. [cite_start]O sistema substitui registos manuais por um fluxo digital auditável que monitoriza desde a entrada do pacote pelo porteiro até à retirada pelo morador[cite: 13, 18].

## [cite_start]🚀 Funcionalidades Principais [cite: 32, 33]

* [cite_start]**Módulo do Porteiro:** Registo de encomendas com descrição, código de rastreio e vínculo automático ao morador/apartamento[cite: 38].
* [cite_start]**Módulo do Morador:** Painel para consulta de encomendas pendentes, retiradas e histórico pessoal[cite: 43].
* [cite_start]**Módulo do Síndico:** Gestão completa de utilizadores (CRUD) e auditoria global através de logs de segurança[cite: 45, 46, 47].
* [cite_start]**Segurança Jurídica:** Rastreabilidade total garantida por logs automáticos que registam o estado anterior e posterior dos dados (`RegistrarHistoricoAsync`)[cite: 30, 31, 51].
* [cite_start]**Controle de Acesso:** Autenticação baseada em tokens (RBAC) com sessões de 8 horas e diferenciação de perfis[cite: 34, 35, 36, 50].

## [cite_start]🛠️ Tecnologias Utilizadas [cite: 54]

* [cite_start]**Backend:** Python com framework Flask [cite: 15, 56]
* [cite_start]**Arquitetura:** MVC (Model-View-Controller) [cite: 15, 55]
* [cite_start]**Banco de Dados:** MySQL (Relacional) [cite: 52]
* [cite_start]**Frontend:** HTML, CSS e JavaScript (com Fetch API para comunicação assíncrona) [cite: 58]
* [cite_start]**Comunicação:** API RESTful com dados em formato JSON [cite: 59]
* [cite_start]**Autenticação:** Sistema baseado em Tokens JWT [cite: 60]

## 📋 Pré-requisitos

Antes de começar, é necessário ter instalado (preferencialmente via WSL/Ubuntu):
* Python 3.10+
* MySQL Server
* Git

## 🔧 Instalação e Configuração

Siga os passos abaixo para configurar o ambiente de desenvolvimento local:

1.  **Clonar o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd projeto_recebi
    ```

2.  **Criar o ambiente virtual (venv):**
    ```bash
    python3 -m venv venv
    ```

3.  **Ativar o ambiente virtual:**
    ```bash
    source venv/bin/activate
    ```

4.  **Instalar as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configurar as Variáveis de Ambiente:**
    * Crie um ficheiro chamado `.env` na raiz do projeto.
    * Copie o conteúdo de `.env.example` e insira as suas credenciais locais do MySQL.

6.  **Preparar o Banco de Dados:**
    * No terminal do MySQL, crie o esquema:
    ```sql
    CREATE DATABASE recebi_db;
    ```

7.  **Executar a aplicação:**
    ```bash
    python run.py
    ```
    O servidor estará disponível em `http://127.0.0.1:5000`.

## [cite_start]👥 Equipe (CC3N - UVV) [cite: 9]

* [cite_start]Ana Carollina Silva Dias Ferreira [cite: 6]
* [cite_start]Lucas Cunha Missagia [cite: 7]
* [cite_start]Pedro Quinellato Dutra Vieira [cite: 8]

---
[cite_start]**Instituição:** Universidade Vila Velha (UVV) [cite: 9]