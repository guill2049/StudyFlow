# StudyFlow

<p align="center">
  <strong>Organização acadêmica inteligente com inteligência artificial</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white" alt="Groq">
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic">
  <img src="https://img.shields.io/badge/Langfuse-000000?style=for-the-badge&logo=langfuse&logoColor=white" alt="Langfuse">
</p>

---

## Sobre o projeto

O **StudyFlow** é uma aplicação desenvolvida para auxiliar estudantes na organização de suas atividades acadêmicas e no planejamento de suas rotinas de estudo.

A aplicação permite cadastrar tarefas, definir prazos e níveis de dificuldade e utilizar inteligência artificial para gerar planos de execução personalizados.

O objetivo é transformar atividades acadêmicas em etapas mais organizadas e gerenciáveis, ajudando o estudante a compreender suas prioridades e administrar melhor o tempo disponível.

O sistema utiliza a API da Groq para geração dos planos, SQLite para persistência dos dados e Langfuse para observabilidade das interações com inteligência artificial.

## Funcionalidades

### Gerenciamento de atividades
- Cadastro de atividades acadêmicas.
- Definição de nome, descrição, prazo e dificuldade.
- Classificação de dificuldade em três níveis: Fácil, Média e Difícil.
- Validação dos dados antes do cadastro.
- Listagem das atividades cadastradas.
- Exclusão de atividades com confirmação.

### Planejamento com inteligência artificial
- Geração de planos personalizados utilizando IA.
- Organização do planejamento em uma estrutura de dados validada com Pydantic.
- Associação dos planos às respectivas atividades.
- Identificação de atividades que já possuem um plano.
- Restrição de geração para impedir múltiplos planos para uma mesma atividade.

### Histórico e acompanhamento
- Armazenamento dos planos gerados.
- Consulta ao histórico de planejamentos.
- Associação entre atividades e seus respectivos planos.
- Exclusão automática dos planos relacionados quando uma atividade é removida.

### Dashboard
- Painel de acompanhamento das atividades.
- Indicadores de organização acadêmica.
- Visualização de prazos e atividades.
- Acompanhamento da cobertura de planejamento.

### Interface
- Interface desenvolvida com Streamlit.
- Dashboard com navegação organizada.
- Componentes visuais personalizados com CSS.
- Cards informativos e indicadores.
- Layout voltado à simplicidade e facilidade de utilização.

## Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Linguagem principal da aplicação. |
| Streamlit | Construção da interface e interação com o usuário. |
| SQLite | Armazenamento persistente de atividades e planos. |
| Groq API | Integração com modelos de inteligência artificial. |
| Pydantic | Validação e estruturação dos dados retornados pela IA. |
| Langfuse | Observabilidade e acompanhamento das chamadas de IA. |
| HTML e CSS | Personalização dos componentes visuais da interface. |

## Arquitetura do projeto

A aplicação foi organizada em módulos para separar as responsabilidades principais do sistema.

```text
StudyFlow/
│
├── app.py              # Interface e fluxo principal da aplicação
├── db.py               # Operações e gerenciamento do banco de dados
├── ai.py               # Integração com a API da Groq e geração de planos
│
├── requirements.txt    # Dependências do projeto
├── .env.example        # Modelo das variáveis de ambiente
├── .gitignore          # Arquivos e diretórios ignorados pelo Git
├── README.MD           # Documentação do projeto
│
└── studyflow.db        # Banco de dados SQLite (gerado localmente)
```

### Responsabilidades dos módulos

**`app.py`**

Responsável pela interface gráfica, navegação entre páginas, cadastro de atividades, apresentação dos dados, interação com o usuário e acionamento das funcionalidades do sistema.

**`db.py`**

Responsável pela conexão com o SQLite e pelas operações de persistência, incluindo criação, consulta, exclusão e armazenamento de atividades e planos.

**`ai.py`**

Responsável pela comunicação com a API da Groq, geração dos planos de estudo e estruturação das respostas utilizando Pydantic.

## Banco de dados

O StudyFlow utiliza SQLite para armazenar os dados localmente.

O banco possui duas entidades principais:

### Atividades

Armazena as informações cadastradas pelo estudante.

Principais informações:
- Identificador da atividade.
- Nome.
- Descrição.
- Prazo.
- Nível de dificuldade.

### Planos

Armazena os planejamentos gerados pela inteligência artificial.

Principais informações:
- Identificador do plano.
- Identificador da atividade relacionada.
- Conteúdo do plano.
- Modelo de IA utilizado.
- Data de criação.

### Relacionamento

Uma atividade pode possuir um plano associado. O relacionamento utiliza uma chave estrangeira com `ON DELETE CASCADE`, garantindo que os planos relacionados sejam removidos automaticamente quando sua atividade correspondente for excluída.

O sistema também verifica a existência de um plano antes de permitir uma nova geração.

## Inteligência artificial

A geração dos planejamentos é realizada por meio da API da Groq.

O fluxo de funcionamento é:

1. O estudante cadastra uma atividade com suas informações.
2. A aplicação envia os dados necessários para o módulo de inteligência artificial.
3. O módulo `ai.py` realiza a comunicação com a API da Groq.
4. A resposta é estruturada e validada utilizando Pydantic.
5. O plano é apresentado ao usuário e armazenado no banco de dados.
6. O modelo utilizado e o conteúdo gerado são registrados para consulta posterior.

A utilização do Pydantic permite trabalhar com respostas estruturadas, reduzindo problemas relacionados a formatos inconsistentes de dados.

## Observabilidade com Langfuse

O projeto possui integração com Langfuse para observabilidade das operações relacionadas à inteligência artificial.

Essa integração permite acompanhar as chamadas realizadas durante a geração dos planos, auxiliando na análise do comportamento da aplicação e no monitoramento das interações com os modelos.

A observabilidade é importante para identificar possíveis falhas, compreender o funcionamento das chamadas e facilitar futuras melhorias na integração com IA.

## Instalação e execução

### Pré-requisitos

Antes de executar o projeto, certifique-se de possuir:

- Python instalado.
- Git instalado.
- Uma chave de API da Groq.
- Credenciais do Langfuse, caso queira utilizar a observabilidade.

### 1. Clonar o repositório

```bash
git clone https://github.com/guill2049/StudyFlow.git
```

Entre no diretório:

```bash
cd StudyFlow
```

### 2. Criar um ambiente virtual

```bash
python -m venv .venv
```

Ative o ambiente virtual.

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux:**

```bash
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Crie um arquivo `.env` a partir do modelo disponibilizado no projeto:

```bash
cp .env.example .env
```

No Windows, também é possível copiar o arquivo manualmente.

Abra o `.env` e preencha as variáveis necessárias com suas próprias credenciais, seguindo os nomes e as instruções presentes no `.env.example`.

Não compartilhe sua chave da Groq ou suas credenciais do Langfuse.

### 5. Executar a aplicação

Com o ambiente virtual ativado, execute:

```bash
streamlit run app.py
```

O Streamlit disponibilizará a aplicação no navegador, normalmente em:

```text
http://localhost:8501
```

## Segurança e boas práticas

Algumas medidas foram adotadas para proteger os dados e melhorar a organização do projeto:

- Utilização de variáveis de ambiente para armazenar credenciais.
- Arquivo `.env` excluído do versionamento por meio do `.gitignore`.
- Banco de dados local excluído do versionamento.
- Validação dos dados recebidos antes de sua persistência.
- Utilização de consultas parametrizadas no SQLite.
- Separação entre interface, persistência e integração com IA.

**Importante:** nunca publique o arquivo `.env` ou compartilhe credenciais de serviços externos.

## Possíveis evoluções

O StudyFlow possui uma estrutura que permite futuras expansões, como:

- Autenticação e gerenciamento de contas de usuários.
- Sincronização de dados em nuvem.
- Edição de atividades cadastradas.
- Replanejamento de atividades.
- Notificações sobre prazos próximos.
- Acompanhamento do progresso de execução dos planos.
- Exportação dos planejamentos.
- Melhorias na personalização das respostas da inteligência artificial.

## Objetivo acadêmico

O StudyFlow foi desenvolvido como um projeto acadêmico com o propósito de aplicar conhecimentos de programação, desenvolvimento de aplicações, persistência de dados e integração com inteligência artificial.

Durante seu desenvolvimento, foram trabalhados conceitos de:

- Desenvolvimento de aplicações com Python.
- Organização modular de código.
- Manipulação de banco de dados relacionais.
- Validação e estruturação de dados.
- Integração com APIs externas.
- Engenharia de prompts e utilização de modelos generativos.
- Observabilidade de aplicações com inteligência artificial.
- Construção de interfaces e experiência do usuário.

## Licença

Este projeto foi desenvolvido para fins acadêmicos. Caso seja disponibilizado publicamente para reutilização ou distribuição, recomenda-se definir uma licença apropriada.

---

<p align="center">
  <strong>StudyFlow</strong><br>
  Organização, planejamento e inteligência para a rotina acadêmica.
</p>