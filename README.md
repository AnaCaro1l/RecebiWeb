# Recebi - Sistema de Gestão de Encomendas para Condomínios

O Recebi é uma plataforma digital centralizada desenvolvida para modernizar e otimizar a gestão e rastreabilidade de encomendas em condomínios residenciais. O sistema substitui registros manuais por um fluxo digital auditável que monitora desde a entrada do pacote pelo porteiro até a retirada pelo morador.

## Funcionalidades Principais

* Módulo do Porteiro: Registro de encomendas com descrição, código de rastreio e vínculo automático ao morador/apartamento.
* Módulo do Morador: Painel para consulta de encomendas pendentes, retiradas e histórico pessoal.
* Módulo do Síndico: Gestão completa de usuários (CRUD) e auditoria global através de logs de segurança.
* Segurança Jurídica: Rastreabilidade total garantida por logs automáticos que registram o estado anterior e posterior dos dados (`RegistrarHistoricoAsync`).
* Controle de Acesso: Autenticação baseada em tokens (RBAC) com sessões de 8 horas e diferenciação de perfis.

## Tecnologias Utilizadas

* Backend: Python com framework Flask
* Arquitetura: MVC (Model-View-Controller)
* Banco de Dados: SQLite (para desenvolvimento e testes) e MySQL (para produção)
* Frontend: HTML, CSS e JavaScript (com Fetch API para comunicação assíncrona)
* Comunicação: API RESTful com dados em formato JSON
* Autenticação: Sistema baseado em Tokens JWT

## Pré-requisitos

Antes de começar, é necessário ter instalado:
* Python 3.11+
* Git
* SQLite ou MySQL Server (dependendo do ambiente que deseja rodar)

## Instalação e Configuração

Siga os passos abaixo para configurar o ambiente de desenvolvimento local:

1. Clonar o repositório:
   ```bash
   git clone <url-do-seu-repositorio>
   cd RecebiWeb
   ```

2. Criar o ambiente virtual (venv):
   * No Windows:
     ```bash
     python -m venv venv
     ```
   * No Linux/macOS/WSL:
     ```bash
     python3 -m venv venv
     ```

3. Ativar o ambiente virtual:
   * No Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * No Windows (Prompt de Comando - CMD):
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   * No Linux/macOS/WSL:
     ```bash
     source venv/bin/activate
     ```

4. Instalar as dependências:
   Instale as dependências através do `pyproject.toml`:
   ```bash
   pip install -e ".[dev,test]"
   ```
   Isso instala todas as dependências do projeto, incluindo ferramentas de desenvolvimento e teste.

5. Configurar as Variáveis de Ambiente:

   **Opção 1 (Recomendada): Usar o script make_env.py**
   
   O projeto possui um script facilitador que cria automaticamente os arquivos de ambiente (`.env.dev`, `.env.test`, `.env.prod`) e configura a aplicação padrão:
   ```bash
   python make_env.py
   ```
   Este script criará o arquivo `.env` principal apontando por padrão para o ambiente de desenvolvimento local em SQLite. É a forma mais simples e segura de configurar o projeto.
   
   **Opção 2: Configuração Manual**
   
   Se preferir configurar manualmente, crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```env
   FLASK_ENV=development
   DATABASE_URI=sqlite:///instance/recebi.db
   JWT_SECRET_KEY=sua_chave_secreta_aqui
   ```
   
   Para utilizar o MySQL em vez de SQLite, altere a variável `DATABASE_URI`:
   ```env
   DATABASE_URI=mysql+pymysql://usuario:senha@localhost/recebi_db
   JWT_SECRET_KEY=sua_chave_secreta_aqui
   ```

6. Preparar o Banco de Dados:
   * **Se estiver utilizando SQLite (padrão):** O arquivo de banco de dados será criado automaticamente na pasta `instance/` ao rodar a inicialização.
   * **Se estiver utilizando MySQL:** Você deve primeiro criar o banco de dados manualmente no seu servidor MySQL antes de inicializar as tabelas:
     ```sql
     CREATE DATABASE recebi_db;
     ```
   
   Em seguida, para criar ou resetar todas as tabelas do banco de dados, execute:
   ```bash
   python tasks.py init-db
   ```

7. Criar o Usuário Administrador (Síndico):
   O sistema exige um usuário com perfil de Síndico para a gestão dos demais usuários. Crie o usuário padrão com o comando:
   ```bash
   python tasks.py create-sindico
   ```
   O usuário será criado com as seguintes credenciais padrão:
   * E-mail: sindico@recebi.com
   * Senha: senha123

8. Executar a Aplicação:
   Para iniciar o servidor de desenvolvimento do Flask, execute:
   ```bash
   python tasks.py run
   ```
   Ou diretamente com o comando do Flask:
   ```bash
   flask run
   ```
   A aplicação estará disponível em `http://127.0.0.1:5000`.

## Executando os Testes

Para executar a suíte de testes com cobertura e validações do pytest, utilize:
```bash
python tasks.py test
```
Ou diretamente:
```bash
pytest
```

## Equipe (CC5N - UVV)

* Ana Carollina Silva Dias Ferreira
* Lucas Cunha Missagia
* Pedro Quinellato Dutra Vieira

---
**Data do Projeto:** 25 de abril de 2026
**Instituição:** Universidade Vila Velha (UVV)
