# Projeto Integrador – Cloud Developing 2025/2

> CRUD simples + API Gateway + Lambda /report + RDS + CI/CD

<!-- AWS Academy Learner Lab [133979] -->

**Grupo**:

1. 10420572 - Luis Felipe Santos do Nascimento - Desenvolvimento da API, Docker
2. 10420317 - Arthur Jones Bicalho dos Santos -  Funçao lambda
3. 10420357 - Alex Cruz de Santana - Documentação

## 1. Visão geral

Este projeto implementa uma API REST para gerenciamento de receitas culinárias, desenvolvida como parte do Projeto Integrador de Cloud Developing. O domínio de receitas foi escolhido por ser intuitivo e permitir demonstrar operações CRUD completas de forma clara.

A aplicação permite:
- **Criar** novas receitas com informações detalhadas (ingredientes, instruções, tempos de preparo, etc.)
- **Listar** todas as receitas cadastradas
- **Buscar** receitas específicas por ID
- **Atualizar** informações de receitas existentes
- **Deletar** receitas

Além disso, uma função Lambda consome a API para gerar estatísticas sobre as receitas (tempo médio de cozimento, categorização por duração, etc.), demonstrando integração entre serviços AWS.

## 2. Arquitetura

![Diagrama](docs/arquitetura.png)

| Camada  | Serviço                       | Descrição                                                                 |
| ------- | ----------------------------- | ------------------------------------------------------------------------- |
| Backend | ECS Fargate                   | API REST FastAPI containerizada, rodando em containers serverless        |
| Banco   | Amazon RDS                    | PostgreSQL em subnet privada, acessível apenas pela VPC                    |
| Gateway | Amazon API Gateway            | Rotas CRUD (`/recipes/*`) → ECS Fargate · `/reports` → Lambda             |
| Função  | AWS Lambda                    | Consome a API via API Gateway, processa dados e retorna estatísticas JSON |
| CI/CD   | GitHub Actions                | Automatiza build da imagem Docker, push para ECR e deploy no ECS          |

## 3. Como rodar localmente

### 3.1 Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.9+ (para desenvolvimento local sem Docker)

### 3.2 Configuração

1. Clone o repositório:
```bash
git clone https://github.com/luisfelipesdn12/mackenzie-cloud-proj-2
cd mackenzie-cloud-proj-2
```

2. Configure as variáveis de ambiente. Crie um arquivo `.env` na raiz do projeto:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=senha_segura
DB_NAME=receitas
```

### 3.3 Execução

```bash
cd src
docker compose up --build
```

A API estará disponível em `http://localhost:80`

### 3.4 Desenvolvimento Local (sem Docker)

```bash
cd src
pip install -r requirements.txt
# Configure as variáveis de ambiente
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=senha_segura
export DB_NAME=receitas
# Execute
fastapi run main.py --port 8000
```

## 4. Endpoints da API

### 4.1 CRUD de Receitas

| Método | Endpoint              | Descrição                          |
|--------|-----------------------|------------------------------------|
| GET    | `/`                   | Informações sobre a API            |
| GET    | `/recipes/`           | Lista todas as receitas            |
| GET    | `/recipes/{id}`       | Busca receita por ID               |
| POST   | `/recipes/`           | Cria nova receita                  |
| PUT    | `/recipes/{id}`       | Atualiza receita existente         |
| DELETE | `/recipes/{id}`       | Remove receita                     |

### 4.2 Exemplos de Uso

**Criar receita:**
```bash
curl -X POST "http://localhost/recipes/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Brigadeiro",
    "description": "Doce brasileiro",
    "ingredients": "Leite condensado, chocolate",
    "instructions": "Misture e cozinhe",
    "prep_time_minutes": 5,
    "cook_time_minutes": 15,
    "servings": 20
  }'
```

**Listar receitas:**
```bash
curl "http://localhost/recipes/"
```

**Buscar receita:**
```bash
curl "http://localhost/recipes/1"
```

**Atualizar receita:**
```bash
curl -X PUT "http://localhost/recipes/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Brigadeiro Gourmet",
    "servings": 25
  }'
```

**Deletar receita:**
```bash
curl -X DELETE "http://localhost/recipes/1"
```

### 4.3 Endpoint de Relatórios

| Método | Endpoint | Descrição                                    |
|--------|----------|----------------------------------------------|
| GET    | `/reports` | Retorna estatísticas sobre as receitas (via Lambda) |

O endpoint `/reports` é gerenciado pelo API Gateway e direcionado para uma função Lambda que consome a API e retorna estatísticas em JSON.

## 5. Modelo de Dados

### 5.1 Schema da Tabela `recipe`

```sql
CREATE TABLE recipe (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    servings INTEGER
);
```

### 5.2 Campos

- `id`: Identificador único (chave primária, auto-incremento)
- `name`: Nome da receita
- `description`: Descrição breve da receita
- `ingredients`: Lista de ingredientes (texto)
- `instructions`: Instruções de preparo (texto)
- `prep_time_minutes`: Tempo de preparo em minutos
- `cook_time_minutes`: Tempo de cozimento em minutos
- `servings`: Número de porções

## 6. Função Lambda

A função Lambda (`lambda.js`) consome o endpoint `/recipes` da API via API Gateway e gera estatísticas:

- Categorização de receitas por tempo de cozimento:
  - Receitas rápidas (≤ 10 min)
  - Receitas médias (11-15 min)
  - Receitas longas (> 15 min)
- Tempo médio de cozimento

## 7. Deploy na AWS

Resumo do processo:
1. Criar VPC com subnets públicas e privadas
2. Criar RDS PostgreSQL em subnet privada
3. Criar ECR repository
4. Criar ECS Cluster e Task Definition
5. Criar ECS Service
6. Criar Lambda function
7. Criar API Gateway
8. Configurar GitHub Secrets
9. Configurar GitHub Actions workflow

## 8. Variáveis de Ambiente

| Variável      | Descrição                    | Exemplo                          |
|---------------|------------------------------|----------------------------------|
| `DB_HOST`     | Host do banco de dados       | `receitas-db.xxx.rds.amazonaws.com` |
| `DB_PORT`     | Porta do banco               | `5432`                           |
| `DB_USER`     | Usuário do banco             | `admin`                          |
| `DB_PASSWORD` | Senha do banco               | `senha_segura`                   |
| `DB_NAME`     | Nome do banco de dados       | `receitas`                       |

## 9. Tecnologias Utilizadas

- **Backend**: FastAPI (Python)
- **ORM**: SQLModel
- **Banco de Dados**: PostgreSQL (RDS)
- **Containerização**: Docker
- **Orquestração**: Docker Compose (local), ECS Fargate (AWS)
- **CI/CD**: GitHub Actions
- **Cloud**: AWS (VPC, RDS, ECS, ECR, Lambda, API Gateway)
- **Infraestrutura como Código**: Configuração manual (documentada)

## 10. Estrutura do Projeto

```
mackenzie-cloud-proj-2/
├── src/
│   ├── main.py              # API FastAPI
│   ├── lambda.js            # Função Lambda para relatórios
│   ├── Dockerfile           # Imagem Docker da API
│   ├── docker-compose.yml   # Orquestração local
│   ├── requirements.txt     # Dependências Python
│   ├── initialize.sql      # Script de inicialização do banco
│   └── setup.sh             # Script de setup (se necessário)
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions workflow
├── task-definition.json     # Task definition do ECS
├── AWS-steps.md            # Guia passo a passo para AWS
└── README.md               # Este arquivo
```
