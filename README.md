# Projeto Integrador – Cloud Developing 2025/1

> CRUD simples + API Gateway + Lambda /report + RDS + CI/CD

<!-- AWS Academy Learner Lab [133979] -->

**Grupo**:

1. 10420572 - Luis Felipe Santos do Nascimento - Desenvolvimento da API, Docker
2. 10420317 - Arthur Jones Bicalho dos Santos -  Funçao lambda
3. 10420357 - Alex Cruz de Santana - Documentação

## 1. Visão geral
<!-- Descreva rapidamente o domínio escolhido, por que foi selecionado e o que o CRUD faz. -->

## 2. Arquitetura

![Diagrama](docs/arquitetura.png)

| Camada  | Serviço                       | Descrição                             |
| ------- | ----------------------------- | ------------------------------------- |
| Backend | ECS Fargate (ou EC2 + Docker) | API REST Node/Spring/…                |
| Banco   | Amazon RDS                    | PostgreSQL / MySQL em subnet privada  |
| Gateway | Amazon API Gateway            | Rotas CRUD → ECS · `/report` → Lambda |
| Função  | AWS Lambda                    | Consome a API, gera estatísticas JSON |
| CI/CD   | CodePipeline + GitHub         | push → build → ECR → deploy           |

## 3. Como rodar localmente

```bash
cp .env.example .env         # configure variáveis
docker compose up --build
# API em http://localhost:3000
```
