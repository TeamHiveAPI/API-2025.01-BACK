# 🌦️ API-2025.01-BACK - Weather Station API

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-green) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue) ![GitHub](https://img.shields.io/badge/GitHub-Repository-lightgrey)

Bem-vindo ao backend da **Weather Station API**! Este projeto foi desenvolvido pela equipe **TeamHiveAPI** para gerenciar dados de estações meteorológicas, incluindo informações de estações, parâmetros, medidas, alertas e usuários. Utilizamos o framework **FastAPI** para criar uma API RESTful eficiente e o **PostgreSQL** como banco de dados relacional.

---

## 📋 Sobre o Projeto

Este é o backend da API para o projeto de estações meteorológicas do curso **2025.01**. Ele foi projetado para:

- Armazenar e gerenciar dados de estações meteorológicas.
- Monitorar parâmetros como temperatura, umidade, etc.
- Gerenciar alertas baseados em condições definidas.
- Oferecer autenticação e gerenciamento de usuários.

### **Funcionalidades**
- **Estações Meteorológicas**: Cadastro e gerenciamento de estações com informações como localização, status e data de instalação.
- **Parâmetros**: Registro de parâmetros de medição com unidades e fatores de conversão.
- **Medidas**: Armazenamento de medições realizadas pelas estações.
- **Alertas**: Definição e monitoramento de alertas com base em condições específicas.
- **Usuários**: Gerenciamento de usuários com níveis de acesso.

---

## 🚀 Como Começar

Siga os passos abaixo para clonar, configurar e rodar o projeto na sua máquina.

### **Pré-requisitos**
Antes de começar, você precisará instalar as seguintes ferramentas:

- [Git](https://git-scm.com/downloads) (para clonar o repositório)
- [Python 3.8+](https://www.python.org/downloads/) (para executar o backend)
- [PostgreSQL 15+](https://www.postgresql.org/download/) (para o banco de dados)
- [DBeaver](https://dbeaver.io/download/) ou [pgAdmin](https://www.pgadmin.org/download/) (opcional, para gerenciar o banco)
- [VS Code](https://code.visualstudio.com/) (opcional, para editar o código)

---

### **Passo 1: Clonar o Repositório**

1. Abra o terminal (PowerShell ou CMD no Windows).
2. Navegue até o diretório onde deseja salvar o projeto:
   ```bash
   cd Desktop
   ```
3. Clone o repositório:
  ```bash
  git clone https://github.com/TeamHiveAPI/API-2025.01-BACK.git
  ```
4. Entre na pasta do projeto:
  ```bash
  cd API-2025.01-BACK
  ```
Passo 2: Configurar o Ambiente Virtual
Crie um ambiente virtual para isolar as dependências:
  ```bash
  python -m venv venv
  ```
Ative o ambiente virtual:
No Windows:
  ```bash
  venv\Scripts\activate
  ```
No Linux/Mac:
  ```bash
  source venv/bin/activate
  ```
Passo 3: Instalar as Dependências
Instale as dependências listadas no arquivo requirements.txt:
  ```bash
  pip install -r requirements.txt
  ```
Nota: Se o arquivo requirements.txt não existir, instale as bibliotecas manualmente:
  ```bash
  pip install fastapi uvicorn sqlalchemy psycopg2-binary
  ```
Passo 4: Configurar o Banco de Dados
Crie o banco de dados no PostgreSQL:
Abra o DBeaver ou pgAdmin.
Conecte-se com o usuário e senha do PostgreSQL (ex.: usuário postgres, senha 1234).
Crie um banco chamado api:
No DBeaver: clique com o botão direito em "Databases" > "Create New Database" > nomeie como api.
No terminal do PostgreSQL:
```sql
CREATE DATABASE api;
```
Atualize a URL de conexão:
Abra o arquivo database.py e verifique a variável DATABASE_URL:
```python
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/api"
```
Ajuste o usuário (postgres), senha (1234), host (localhost), porta (5432) e nome do banco (api) conforme sua configuração.

Passo 5: Rodar a Aplicação
Inicie o servidor FastAPI com Uvicorn:
```bash
uvicorn main:app --reload
```
O parâmetro --reload faz o servidor reiniciar automaticamente ao alterar o código.
O servidor será iniciado em http://127.0.0.1:8000.
