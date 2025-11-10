# Passo a Passo - Deploy no AWS

Este documento descreve todos os passos necessários para colocar a aplicação no ar na AWS.

## Pré-requisitos

- Conta AWS ativa
- AWS CLI instalado e configurado
- GitHub Actions habilitado no repositório
- Conhecimento básico de AWS (VPC, ECS, RDS, API Gateway, Lambda)

---

## 1. Criar VPC e Configuração de Rede

### 1.1 Criar VPC

1. Acesse o **AWS Console** → **VPC**
2. Clique em **Create VPC**
3. Configure:
   - **Name tag**: `receitas-vpc`
   - **IPv4 CIDR block**: `10.0.0.0/16`
   - **Tenancy**: Default
4. Clique em **Create VPC**

### 1.2 Criar Subnets

#### Subnet Pública (para ECS Fargate)

1. No menu lateral, clique em **Subnets** → **Create subnet**
2. Configure:
   - **VPC ID**: Selecione `receitas-vpc`
   - **Subnet name**: `receitas-public-subnet-1`
   - **Availability Zone**: `us-east-1a` (ou sua preferência)
   - **IPv4 CIDR block**: `10.0.1.0/24`
3. Clique em **Create subnet**
4. Repita para criar uma segunda subnet pública:
   - **Subnet name**: `receitas-public-subnet-2`
   - **Availability Zone**: `us-east-1b`
   - **IPv4 CIDR block**: `10.0.2.0/24`

#### Subnet Privada (para RDS)

1. Crie subnet privada 1:
   - **Subnet name**: `receitas-private-subnet-1`
   - **Availability Zone**: `us-east-1a`
   - **IPv4 CIDR block**: `10.0.3.0/24`
2. Crie subnet privada 2:
   - **Subnet name**: `receitas-private-subnet-2`
   - **Availability Zone**: `us-east-1b`
   - **IPv4 CIDR block**: `10.0.4.0/24`

### 1.3 Criar Internet Gateway

1. No menu lateral, clique em **Internet Gateways** → **Create internet gateway**
2. **Name tag**: `receitas-igw`
3. Clique em **Create internet gateway**
4. Selecione o IGW criado → **Actions** → **Attach to VPC**
5. Selecione `receitas-vpc` e confirme

### 1.4 Criar Route Tables

#### Route Table Pública

1. **Route Tables** → **Create route table**
2. Configure:
   - **Name**: `receitas-public-rt`
   - **VPC**: `receitas-vpc`
3. Clique em **Create**
4. Selecione a route table → **Routes** → **Edit routes** → **Add route**:
   - **Destination**: `0.0.0.0/0`
   - **Target**: Selecione o Internet Gateway `receitas-igw`
5. **Subnet associations** → **Edit subnet associations**:
   - Marque `receitas-public-subnet-1` e `receitas-public-subnet-2`
   - Salve

#### Route Table Privada

1. Crie route table privada:
   - **Name**: `receitas-private-rt`
   - **VPC**: `receitas-vpc`
2. **Subnet associations** → Associe `receitas-private-subnet-1` e `receitas-private-subnet-2`
3. **Não adicione rota para Internet Gateway** (mantém privada)

### 1.5 Criar Security Groups

#### Security Group para ECS Fargate

1. **Security Groups** → **Create security group**
2. Configure:
   - **Name**: `receitas-ecs-sg`
   - **Description**: `Security group for ECS Fargate tasks`
   - **VPC**: `receitas-vpc`
3. **Inbound rules**:
   - **Type**: Custom TCP
   - **Port**: `80`
   - **Source**: `0.0.0.0/0` (ou apenas do ALB/API Gateway)
4. **Outbound rules**: Deixe padrão (All traffic)
5. Clique em **Create security group**

#### Security Group para RDS

1. **Create security group**
2. Configure:
   - **Name**: `receitas-rds-sg`
   - **Description**: `Security group for RDS PostgreSQL`
   - **VPC**: `receitas-vpc`
3. **Inbound rules**:
   - **Type**: PostgreSQL
   - **Port**: `5432`
   - **Source**: Selecione o security group `receitas-ecs-sg` (permite acesso apenas do ECS)
4. **Outbound rules**: Deixe padrão
5. Clique em **Create security group**

---

## 2. Criar RDS PostgreSQL

### 2.0 Criar Database Subnet Group (ANTES de criar o RDS)

**⚠️ IMPORTANTE**: É necessário criar o Database Subnet Group separadamente antes de criar a instância RDS.

1. No console RDS, no menu lateral esquerdo, clique em **Subnet groups** (não em Databases)
2. Clique em **Create DB subnet group**
3. Configure:
   - **Name**: `receitas-db-subnet-group`
   - **Description**: `Subnet group for receitas RDS PostgreSQL`
   - **VPC**: Selecione `receitas-vpc`
4. **Availability Zones**: 
   - Selecione pelo menos 2 zonas diferentes (ex: `us-east-1a` e `us-east-1b`)
   - **⚠️ IMPORTANTE**: As subnets privadas devem estar em Availability Zones diferentes. Se ambas estiverem na mesma AZ, você precisará criar uma nova subnet privada em outra AZ.
5. **Subnets**:
   - Clique em **Add subnets**
   - Selecione `receitas-private-subnet-1` e `receitas-private-subnet-2`
   - Se as subnets não aparecerem, verifique:
     - Se estão em Availability Zones diferentes (obrigatório)
     - Se estão na VPC `receitas-vpc`
6. Clique em **Create**

### 2.1 Criar Instância RDS

1. Acesse **RDS** → **Databases** → **Create database**
2. Configure:
   - **Engine type**: PostgreSQL
   - **Version**: Escolha a versão mais recente (ex: PostgreSQL 15.x)
   - **Template**: Free tier (se disponível) ou Production
3. **Settings**:
   - **DB instance identifier**: `receitas-db` ⚠️ **Este é o nome da INSTÂNCIA RDS, não do banco de dados**
   - **Master username**: `admin` (ou seu preferido)
   - **Master password**: Crie uma senha forte e **ANOTE**
4. **Instance configuration**:
   - **DB instance class**: `db.t3.micro` (free tier) ou maior
5. **Storage**:
   - **Storage type**: General Purpose SSD (gp3)
   - **Allocated storage**: `20 GB`
6. **Connectivity**:
   - **VPC**: `receitas-vpc`
   - **Subnet group**: Selecione `receitas-db-subnet-group` (criado no passo 2.0)
     - Se não aparecer no dropdown, volte ao passo 2.0 e verifique se o Subnet Group foi criado corretamente
   - **Public access**: **No** (mantém privado)
   - **VPC security group**: Selecione `receitas-rds-sg`
   - **Availability Zone**: Deixe padrão
7. **Database authentication**: Password authentication
8. **Additional configuration**:
   - **Initial database name**: `receitas` ⚠️ **IMPORTANTE: Este é o nome do BANCO DE DADOS que será usado na variável DB_NAME**
   - **Backup retention**: `7 days`
9. Clique em **Create database**

**⚠️ DIFERENÇA IMPORTANTE**:
- **DB instance identifier** (`receitas-db`): Nome da instância RDS (usado para identificar a instância)
- **Initial database name** (`receitas`): Nome do banco de dados dentro da instância (usado na variável `DB_NAME`)

### 2.2 Obter Endpoint do RDS

1. Após a criação (pode levar alguns minutos), vá em **Databases**
2. Clique na instância `receitas-db`
3. Na seção **Connectivity & security**, copie o **Endpoint** (ex: `receitas-db.xxxxx.us-east-1.rds.amazonaws.com`)
4. **ANOTE** este endpoint - será usado nas variáveis de ambiente

---

## 3. Criar ECR Repository

1. Acesse **ECR** (Elastic Container Registry) → **Repositories** → **Create repository**
2. Configure:
   - **Visibility settings**: Private
   - **Repository name**: `receitas-api`
3. Clique em **Create repository**
4. Na página do repositório, copie o **URI** (ex: `123456789012.dkr.ecr.us-east-1.amazonaws.com/receitas-api`)
5. **ANOTE** este URI

---

## 4. Criar ECS Cluster

1. Acesse **ECS** → **Clusters** → **Create cluster**
2. Configure:
   - **Cluster name**: `receitas-cluster`
   - **Infrastructure**: AWS Fargate (Serverless)
3. Clique em **Create**

---

## 5. Criar Task Definition

1. No cluster criado, vá em **Task definitions** → **Create new task definition**
2. Configure:
   - **Task definition family**: `receitas-api-task`
   - **Launch type**: Fargate
   - **Task size**:
     - **CPU**: `0.25 vCPU` (256)
     - **Memory**: `0.5 GB` (512)
3. **Container details**:
   - **Container name**: `receitas-api`
   - **Image URI**: Use temporariamente `123456789012.dkr.ecr.us-east-1.amazonaws.com/receitas-api:latest` (será atualizado pelo CI/CD)
   - **Port mappings**: 
     - **Container port**: `80`
     - **Protocol**: `tcp`
4. **Environment variables** (adicionar):
   ```
   DB_HOST=<RDS_ENDPOINT>
   DB_PORT=5432
   DB_USER=admin
   DB_PASSWORD=<SENHA_DO_RDS>
   DB_NAME=receitas
   ```
   **⚠️ IMPORTANTE**: 
   - Substitua `<RDS_ENDPOINT>` pelo endpoint copiado na seção 2.2 (ex: `receitas-db.xxxxx.us-east-1.rds.amazonaws.com`)
   - Substitua `<SENHA_DO_RDS>` pela senha criada na seção 2.1
   - **DB_NAME deve ser `receitas`** (nome do banco criado na seção 2.1, passo 8), **NÃO** `receitas-db` (que é o nome da instância)
5. **Task role** (se disponível):
   - **⚠️ IMPORTANTE**: Se houver opção de selecionar Task Role, selecione `LabRole` (ou o nome da role do AWS Academy Learner Lab)
   - **NÃO** crie uma nova role automaticamente, pois ela não terá as permissões necessárias
6. **Execution role** (se disponível):
   - **⚠️ IMPORTANTE**: Se houver opção de selecionar Execution Role, selecione `LabRole` (ou o nome da role do AWS Academy Learner Lab)
   - **NÃO** crie uma nova role automaticamente
7. **App environment**: Production
8. Clique em **Create**

---

## 6. Criar ECS Service

1. No cluster `receitas-cluster`, clique em **Services** → **Create**
2. Configure:
   - **Launch type**: Fargate
   - **Task definition**: `receitas-api-task`
   - **Service name**: `receitas-api-service`
   - **Number of tasks**: `1`
3. **Networking**:
   - **VPC**: `receitas-vpc`
   - **Subnets**: Selecione `receitas-public-subnet-1` e `receitas-public-subnet-2`
   - **Security groups**: Selecione `receitas-ecs-sg`
   - **Auto-assign public IP**: **Enabled** (necessário para acessar RDS inicialmente)
4. **Load balancing**: Opcional (pode adicionar depois)
5. **Deployment configuration**:
   - **Minimum healthy percent**: `100` (ou `0` se quiser permitir downtime durante deploy)
   - **Maximum percent**: `200`
6. **Auto-restart** (comportamento padrão do ECS Service):
   - O ECS Service automaticamente reinicia tasks que falharem ou pararem
   - Se uma task falhar, o ECS criará uma nova task automaticamente para manter o número desejado de tasks
   - Isso garante alta disponibilidade da aplicação
7. Clique em **Create**

**⚠️ NOTA**: O serviço pode falhar inicialmente porque ainda não há imagem no ECR. Isso será resolvido quando o CI/CD fizer o primeiro deploy.

---

## 7. Configurar Lambda Function

### 7.1 Criar Lambda Function

1. Acesse **Lambda** → **Functions** → **Create function**
2. Configure:
   - **Function name**: `receitas-report`
   - **Runtime**: Node.js 20.x (ou versão compatível)
   - **Architecture**: x86_64
3. **Execution role**:
   - **⚠️ IMPORTANTE**: Selecione **Use an existing role**
   - Escolha `LabRole` (ou o nome da role do AWS Academy Learner Lab)
   - **NÃO** selecione "Create a new role" ou "Create a new role with basic Lambda permissions", pois essas roles não terão as permissões necessárias do Learner Lab
4. Clique em **Create function**

### 7.2 Configurar Código

1. No editor de código da Lambda, cole o conteúdo de `src/lambda.js`
2. **⚠️ IMPORTANTE - Configuração do Handler**:
   - Se o arquivo no console da Lambda for `index.js` ou `index.mjs`: Handler = `index.handler`
   - Se o arquivo no console da Lambda for `lambda.js`: Handler = `lambda.handler`
   - **Para ES Modules** (código usa `export const handler`):
     - Certifique-se de que o **Runtime** está configurado como **Node.js 20.x** ou superior
     - O código já está usando ES modules (`export const handler`), então não precisa de configuração adicional
   - **Se aparecer erro "exports is not defined"**: Verifique se o handler está configurado corretamente e se o runtime suporta ES modules
3. **Variável de ambiente** (será configurada após criar o API Gateway):
   - Vá em **Configuration** → **Environment variables**
   - Adicione:
     - **Key**: `API_GATEWAY_URL`
     - **Value**: `https://<API_GATEWAY_INVOKE_URL>` (você atualizará isso após criar o API Gateway na seção 9.3)
   - Clique em **Save**

### 7.3 Configurar IAM Role

1. Na aba **Configuration** → **Permissions**
2. Clique no **Role name** para abrir no IAM
3. Adicione política para permitir acesso à VPC (se necessário) e logs do CloudWatch

### 7.4 Configurar VPC (se necessário)

Se a Lambda precisar acessar recursos na VPC:
1. **Configuration** → **VPC**
2. Selecione:
   - **VPC**: `receitas-vpc`
   - **Subnets**: `receitas-private-subnet-1`, `receitas-private-subnet-2`
   - **Security groups**: Crie um novo ou use existente

---

## 8. Configurar GitHub Secrets e CI/CD

**⚠️ IMPORTANTE**: Configure o CI/CD e faça o primeiro deploy ANTES de configurar o API Gateway, pois você precisará do IP público do ECS Task que só estará disponível após o deploy.

### 8.1 Configurar GitHub Secrets

#### 8.1.1 Obter Credenciais AWS (AWS Academy Learner Lab)

**⚠️ IMPORTANTE**: No AWS Academy Learner Lab, você não pode criar usuários IAM. Use as credenciais temporárias fornecidas pelo Learner Lab.

**Opção 1 - Usar Credenciais Temporárias do Learner Lab (Recomendado):**

1. No AWS Academy Learner Lab, vá em **AWS Details** (ou **Account Details**)
2. Clique em **Show** para revelar as credenciais
3. **ANOTE**:
   - **AWS_ACCESS_KEY_ID**
   - **AWS_SECRET_ACCESS_KEY**
   - **AWS_SESSION_TOKEN** (importante - estas são credenciais temporárias)
4. **⚠️ ATENÇÃO**: Essas credenciais expiram quando a sessão do Learner Lab expira. Você precisará atualizar os secrets no GitHub quando isso acontecer.

**Opção 2 - Usar AWS CLI com Role (Alternativa):**

Se você já tem AWS CLI configurado com a role do Learner Lab:
1. Execute: `aws sts get-caller-identity` para verificar sua identidade
2. Para obter credenciais temporárias via CLI:
   ```bash
   aws sts get-session-token
   ```
3. Use as credenciais retornadas (AccessKeyId, SecretAccessKey, SessionToken)

**⚠️ NOTA**: No GitHub Secrets, você precisará adicionar também `AWS_SESSION_TOKEN` se estiver usando credenciais temporárias.

#### 8.1.2 Adicionar Secrets no GitHub

1. No seu repositório GitHub, vá em **Settings** → **Secrets and variables** → **Actions**
2. Clique em **New repository secret** e adicione:

   - **Name**: `AWS_ACCESS_KEY_ID`
     - **Value**: Cole o Access Key ID obtido no passo 8.1.1

   - **Name**: `AWS_SECRET_ACCESS_KEY`
     - **Value**: Cole o Secret Access Key obtido no passo 8.1.1

   - **Name**: `AWS_SESSION_TOKEN` ⚠️ **OBRIGATÓRIO para Learner Lab**
     - **Value**: Cole o Session Token obtido no passo 8.1.1
     - **Nota**: Se não estiver usando credenciais temporárias, este secret pode ser omitido

   - **Name**: `AWS_REGION`
     - **Value**: `us-east-1` (ou a região do seu Learner Lab)

   - **Name**: `ECR_REPOSITORY`
     - **Value**: `receitas-api` (nome do repositório ECR)

   - **Name**: `ECS_CLUSTER`
     - **Value**: `receitas-cluster`

   - **Name**: `ECS_SERVICE`
     - **Value**: `receitas-api-service`

   - **Name**: `ECS_TASK_DEFINITION`
     - **Value**: `receitas-api-task`

**⚠️ IMPORTANTE - Renovação de Credenciais:**
- As credenciais do Learner Lab expiram quando a sessão expira
- Quando isso acontecer, você precisará:
  1. Obter novas credenciais do Learner Lab (passo 8.1.1)
  2. Atualizar os secrets `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` e `AWS_SESSION_TOKEN` no GitHub

### 8.2 Criar GitHub Actions Workflow

#### 8.2.1 Criar Arquivo de Workflow

1. No repositório, crie `.github/workflows/deploy.yml`
2. Use o conteúdo baseado no artigo de referência (ajustado para este projeto)

#### 8.2.2 Criar Task Definition JSON (Opcional)

**Nota**: O workflow do GitHub Actions pode baixar a task definition automaticamente do ECS. Se preferir usar um arquivo JSON local:

1. No ECS, vá em **Task definitions** → Selecione `receitas-api-task`
2. Clique em **Create new revision**
3. Na página de revisão, clique em **JSON** (canto superior direito)
4. Copie o JSON completo
5. No repositório, crie `task-definition.json` na raiz
6. Cole o JSON e ajuste:
   - Remova campos desnecessários
   - Mantenha a estrutura básica
   - O container name deve ser `receitas-api`

### 8.3 Fazer Primeiro Deploy

1. Certifique-se de que todos os secrets do GitHub estão configurados (passo 8.1.2)
2. Certifique-se de que o arquivo `.github/workflows/deploy.yml` está criado no repositório
3. Faça commit e push das alterações para o branch `main`:
   ```bash
   git add .
   git commit -m "Configure CI/CD workflow"
   git push origin main
   ```
4. Acesse o GitHub → **Actions** no seu repositório
5. Monitore o workflow em execução
6. Aguarde a conclusão do deploy (pode levar alguns minutos)
7. Verifique o status do serviço no ECS:
   - Vá em **ECS** → **Clusters** → `receitas-cluster` → **Services** → `receitas-api-service`
   - Verifique se o serviço está **Running** e tem tasks ativas
8. **Obter IP Público do ECS Task**:
   - Vá em **ECS** → **Clusters** → `receitas-cluster` → **Tasks**
   - Clique em uma task (ID da task)
   - Na seção **Network**, copie o **Public IP** e **ANOTE** (ex: `54.123.45.67`)
   - Este IP será usado na configuração do API Gateway

---

## 9. Criar API Gateway

**⚠️ IMPORTANTE**: Configure o API Gateway APÓS fazer o primeiro deploy (seção 8.3), pois você precisará do IP público do ECS Task que só estará disponível após o deploy estar rodando.

### 9.1 Criar REST API

1. Acesse **API Gateway** → **APIs** → **Create API**
2. Selecione **REST API** → **Build**
3. Configure:
   - **Protocol**: REST
   - **Create new API**: New API
   - **API name**: `receitas-api-gateway`
   - **Endpoint Type**: Regional
4. Clique em **Create API**

### 9.2 Criar Recursos e Métodos

#### Criar Resource `/recipes`

1. Clique em **Actions** → **Create Resource**
2. **Resource Name**: `recipes`
   - **Resource Path**: `/recipes`
3. Clique em **Create Resource**

#### Criar Métodos para `/recipes`

**⚠️ IMPORTANTE**: Use o IP público anotado no passo 8.3 (após o deploy). Se ainda não tiver feito o deploy, volte à seção 8.3 primeiro.

**Agora configure o método:**

1. Selecione `/recipes` → **Actions** → **Create Method** → Selecione `GET`
2. Configure:
   - **Integration type**: HTTP Proxy
   - **Endpoint URL**: `http://<ECS_PUBLIC_IP>:80/recipes/`
     - Substitua `<ECS_PUBLIC_IP>` pelo IP público anotado acima (ex: `http://54.123.45.67:80/recipes/`)
   - **HTTP Method**: GET
3. Clique em **Save**
4. Repita para outros métodos (POST, PUT, DELETE) se necessário
   - **POST**: `http://<ECS_PUBLIC_IP>:80/recipes/`
   - **PUT**: `http://<ECS_PUBLIC_IP>:80/recipes/{id}`
   - **DELETE**: `http://<ECS_PUBLIC_IP>:80/recipes/{id}`

#### Criar Resource `/reports`

1. **Actions** → **Create Resource** → `/reports`
2. Selecione `/reports` → **Actions** → **Create Method** → `GET`
3. Configure:
   - **Integration type**: Lambda Function
   - **Lambda Function**: `receitas-report`
   - Marque **Use Lambda Proxy integration**
4. Clique em **Save** → **OK** quando perguntado sobre permissões

### 9.3 Deploy API

1. **Actions** → **Deploy API**
2. Configure:
   - **Deployment stage**: `prod` (ou crie novo)
   - **Stage description**: `Production deployment`
3. Clique em **Deploy**
4. **ANOTE** a **Invoke URL** (ex: `https://xxxxx.execute-api.us-east-1.amazonaws.com/prod`)

### 9.4 Atualizar Lambda com URL do API Gateway

1. Volte para a Lambda `receitas-report`
2. Vá em **Configuration** → **Environment variables**
3. Atualize a variável `API_GATEWAY_URL`:
   - **Key**: `API_GATEWAY_URL`
   - **Value**: `https://<API_GATEWAY_INVOKE_URL>` (ex: `https://xxxxx.execute-api.us-east-1.amazonaws.com/prod`)
   - **⚠️ IMPORTANTE**: Não inclua `/recipes/` na URL, apenas a URL base do API Gateway
4. Clique em **Save**
5. A Lambda agora está configurada para buscar dados de `https://<API_GATEWAY_INVOKE_URL>/recipes/`

---

## 10. Como a API Docker Acessa o RDS

### 10.1 Configuração de Rede

- **ECS Fargate** está na subnet **pública** (com IP público)
2. **Security credentials** → **Create access key**
3. Escolha **Command Line Interface (CLI)**
4. **ANOTE** o **Access Key ID** e **Secret Access Key**

#### 8.1.2 Adicionar Secrets no GitHub

1. No seu repositório GitHub, vá em **Settings** → **Secrets and variables** → **Actions**
2. Clique em **New repository secret** e adicione:

   - **Name**: `AWS_ACCESS_KEY_ID`
     - **Value**: Cole o Access Key ID

   - **Name**: `AWS_SECRET_ACCESS_KEY`
     - **Value**: Cole o Secret Access Key

   - **Name**: `AWS_REGION`
     - **Value**: `us-east-1` (ou sua região)

   - **Name**: `ECR_REPOSITORY`
     - **Value**: `receitas-api` (nome do repositório ECR)

   - **Name**: `ECS_CLUSTER`
     - **Value**: `receitas-cluster`

   - **Name**: `ECS_SERVICE`
     - **Value**: `receitas-api-service`

   - **Name**: `ECS_TASK_DEFINITION`
     - **Value**: `receitas-api-task`

### 8.2 Criar GitHub Actions Workflow

#### 8.2.1 Criar Arquivo de Workflow

1. No repositório, crie `.github/workflows/deploy.yml`
2. Use o conteúdo baseado no artigo de referência (ajustado para este projeto)

#### 8.2.2 Criar Task Definition JSON (Opcional)

**Nota**: O workflow do GitHub Actions pode baixar a task definition automaticamente do ECS. Se preferir usar um arquivo JSON local:

1. No ECS, vá em **Task definitions** → Selecione `receitas-api-task`
2. Clique em **Create new revision**
3. Na página de revisão, clique em **JSON** (canto superior direito)
4. Copie o JSON completo
5. No repositório, crie `task-definition.json` na raiz
6. Cole o JSON e ajuste:
   - Remova campos desnecessários
   - Mantenha a estrutura básica
   - O container name deve ser `receitas-api`

### 8.3 Fazer Primeiro Deploy

1. Certifique-se de que todos os secrets do GitHub estão configurados (passo 8.1.2)
2. Certifique-se de que o arquivo `.github/workflows/deploy.yml` está criado no repositório
3. Faça commit e push das alterações para o branch `main`:
   ```bash
   git add .
   git commit -m "Configure CI/CD workflow"
   git push origin main
   ```
4. Acesse o GitHub → **Actions** no seu repositório
5. Monitore o workflow em execução
6. Aguarde a conclusão do deploy (pode levar alguns minutos)
7. Verifique o status do serviço no ECS:
   - Vá em **ECS** → **Clusters** → `receitas-cluster` → **Services** → `receitas-api-service`
   - Verifique se o serviço está **Running** e tem tasks ativas
8. **Obter IP Público do ECS Task**:
   - Vá em **ECS** → **Clusters** → `receitas-cluster` → **Tasks**
   - Clique em uma task (ID da task)
   - Na seção **Network**, copie o **Public IP** e **ANOTE** (ex: `54.123.45.67`)
   - Este IP será usado na configuração do API Gateway

---

## 9. Criar API Gateway

**⚠️ IMPORTANTE**: Configure o API Gateway APÓS fazer o primeiro deploy (seção 8.3), pois você precisará do IP público do ECS Task que só estará disponível após o deploy estar rodando.

### 9.1 Criar REST API

1. Acesse **API Gateway** → **APIs** → **Create API**
2. Selecione **REST API** → **Build**
3. Configure:
   - **Protocol**: REST
   - **Create new API**: New API
   - **API name**: `receitas-api-gateway`
   - **Endpoint Type**: Regional
4. Clique em **Create API**

### 9.2 Criar Recursos e Métodos

#### Criar Resource `/recipes`

1. Clique em **Actions** → **Create Resource**
2. **Resource Name**: `recipes`
   - **Resource Path**: `/recipes`
3. Clique em **Create Resource**

#### Criar Métodos para `/recipes`

**⚠️ IMPORTANTE**: Use o IP público anotado no passo 8.3 (após o deploy). Se ainda não tiver feito o deploy, volte à seção 8.3 primeiro.

**Configurar método ANY para `/recipes` (cobre GET e POST sem ID):**

1. Selecione `/recipes` → **Actions** → **Create Method** → Selecione `ANY`
2. Configure:
   - **Integration type**: HTTP Proxy
   - **Endpoint URL**: `http://<ECS_PUBLIC_IP>:80/recipes/`
     - Substitua `<ECS_PUBLIC_IP>` pelo IP público anotado no passo 8.3 (ex: `http://54.123.45.67:80/recipes/`)
   - **HTTP Method**: ANY
3. Clique em **Save**

**Configurar método ANY para `/recipes/{id}` (cobre GET, PUT, DELETE com ID):**

1. Selecione `/recipes` → **Actions** → **Create Resource**
   - **Resource Name**: `{id}`
   - **Resource Path**: `{id}`
   - Marque **Enable API Gateway CORS** (opcional)
2. Clique em **Create Resource**
3. Selecione `/recipes/{id}` → **Actions** → **Create Method** → Selecione `ANY`
4. Configure:
   - **Integration type**: HTTP Proxy
   - **Endpoint URL**: `http://<ECS_PUBLIC_IP>:80/recipes/{id}`
     - Substitua `<ECS_PUBLIC_IP>` pelo IP público anotado no passo 8.3 (ex: `http://54.123.45.67:80/recipes/{id}`)
     - **⚠️ IMPORTANTE**: Use `{id}` (variável do path parameter) no endpoint
   - **HTTP Method**: ANY
5. Clique em **Save**

**Nota**: O método `ANY` cobre todos os métodos HTTP (GET, POST, PUT, DELETE, PATCH, etc.), simplificando a configuração. Agora você tem:
- `/recipes` com ANY → cobre `GET /recipes/` e `POST /recipes/`
- `/recipes/{id}` com ANY → cobre `GET /recipes/{id}`, `PUT /recipes/{id}`, `DELETE /recipes/{id}`

#### Criar Resource `/reports`

1. **Actions** → **Create Resource** → `/reports`
2. Selecione `/reports` → **Actions** → **Create Method** → `GET`
3. Configure:
   - **Integration type**: Lambda Function
   - **Lambda Function**: `receitas-report`
   - Marque **Use Lambda Proxy integration**
4. Clique em **Save** → **OK** quando perguntado sobre permissões

### 9.3 Deploy API

1. **Actions** → **Deploy API**
2. Configure:
   - **Deployment stage**: `prod` (ou crie novo)
   - **Stage description**: `Production deployment`
3. Clique em **Deploy**
4. **ANOTE** a **Invoke URL** (ex: `https://xxxxx.execute-api.us-east-1.amazonaws.com/prod`)

### 9.4 Atualizar Lambda com URL do API Gateway

1. Volte para a Lambda `receitas-report`
2. Vá em **Configuration** → **Environment variables**
3. Atualize a variável `API_GATEWAY_URL`:
   - **Key**: `API_GATEWAY_URL`
   - **Value**: `https://<API_GATEWAY_INVOKE_URL>` (ex: `https://xxxxx.execute-api.us-east-1.amazonaws.com/prod`)
   - **⚠️ IMPORTANTE**: Não inclua `/recipes/` na URL, apenas a URL base do API Gateway
4. Clique em **Save**
5. A Lambda agora está configurada para buscar dados de `https://<API_GATEWAY_INVOKE_URL>/recipes/`

---

## 10. Como a API Docker Acessa o RDS

### 10.1 Configuração de Rede

- **ECS Fargate** está na subnet **pública** (com IP público)
- **RDS** está na subnet **privada** (sem IP público)
- Ambos estão na **mesma VPC** (`receitas-vpc`)
- O **Security Group do RDS** permite conexões do **Security Group do ECS** na porta 5432

### 10.2 Variáveis de Ambiente

As variáveis de ambiente configuradas na Task Definition permitem que a aplicação se conecte:
- `DB_HOST`: Endpoint do RDS (resolvido via DNS interno da AWS)
- `DB_PORT`: 5432 (PostgreSQL)
- `DB_USER`: Usuário do RDS
- `DB_PASSWORD`: Senha do RDS
- `DB_NAME`: Nome do banco de dados

### 10.3 Resolução DNS

A AWS resolve automaticamente o endpoint do RDS dentro da VPC. A aplicação Docker usa essas variáveis para conectar via SQLModel/SQLAlchemy.

### 10.4 Teste de Conectividade

Para testar se a conexão funciona:
1. Execute um task do ECS
2. Verifique os logs do CloudWatch
3. Se houver erro de conexão, verifique:
   - Security Groups (RDS deve permitir tráfego do ECS)
   - Variáveis de ambiente na Task Definition
   - Endpoint do RDS está correto

---

## 11. Checklist Final

Antes de fazer o deploy via CI/CD, verifique:

- [ ] VPC criada com subnets públicas e privadas
- [ ] Internet Gateway anexado e route tables configuradas
- [ ] Security Groups criados e configurados corretamente
- [ ] RDS PostgreSQL criado e endpoint anotado
- [ ] ECR repository criado
- [ ] ECS Cluster criado
- [ ] Task Definition criada com variáveis de ambiente e LabRole selecionada
- [ ] ECS Service criado (pode estar falhando, é normal)
- [ ] Lambda function criada com LabRole selecionada
- [ ] GitHub Secrets configurados
- [ ] Workflow do GitHub Actions criado
- [ ] Primeiro deploy realizado com sucesso
- [ ] IP público do ECS Task anotado
- [ ] API Gateway configurado e deployado

---

## 12. Troubleshooting

### ECS Service não inicia
- Verifique os logs do CloudWatch
- Verifique se a imagem existe no ECR
- Verifique as variáveis de ambiente

### API não conecta ao RDS
- Verifique Security Groups (RDS deve permitir tráfego do ECS na porta 5432)
- Verifique se o endpoint do RDS está correto na variável `DB_HOST`
- Verifique as credenciais nas variáveis de ambiente (`DB_USER`, `DB_PASSWORD`)
- **Erro "database 'receitas-db' does not exist"**:
  - **Solução automática**: A aplicação agora cria o banco automaticamente se ele não existir. Faça um novo deploy e verifique os logs.
  - **Solução manual** (se a automática não funcionar):
    1. Acesse **RDS** → **Databases** → `receitas-db`
    2. Clique na aba **Query Editor** (ou use o RDS Query Editor)
    3. Conecte-se usando as credenciais do RDS
    4. Execute: `CREATE DATABASE "receitas-db";` (ou o nome que você configurou)
    5. Verifique se `DB_NAME` na Task Definition corresponde ao nome do banco criado
  - **Nota**: Se você criou o banco como `receitas-db` no campo "Initial database name", então `DB_NAME` deve ser `receitas-db`. Se criou como `receitas`, então `DB_NAME` deve ser `receitas`.

### Lambda não acessa API
- Verifique a URL do API Gateway
- Verifique permissões da Lambda
- Verifique logs do CloudWatch

---

## 13. Checklist - Ao Iniciar o Lab Novamente

**⚠️ IMPORTANTE**: Quando você iniciar uma nova sessão do AWS Academy Learner Lab, atualize apenas o que mudou:

### 13.1 Atualizar Credenciais do GitHub (OBRIGATÓRIO)

**⚠️ CRÍTICO**: As credenciais do Learner Lab expiram quando a sessão expira.

1. Obter novas credenciais do AWS Academy Learner Lab (seção 8.1.1)
2. Atualizar no GitHub → **Settings** → **Secrets and variables** → **Actions**:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_SESSION_TOKEN` ⚠️ **OBRIGATÓRIO**

### 13.2 Atualizar IP Público no API Gateway (Se Mudou)

1. Obter o IP público do ECS Task:
   - **ECS** → **Clusters** → `receitas-cluster` → **Tasks** → Clique na task → Copie o **Public IP**
2. Atualizar o API Gateway:
   - **API Gateway** → `receitas-api-gateway` → **Resources**
   - Método `/recipes` → Endpoint URL: `http://<NOVO_IP>:80/recipes/`
   - Método `/recipes/{id}` → Endpoint URL: `http://<NOVO_IP>:80/recipes/{id}`
   - **Actions** → **Deploy API** → Stage `prod`

---

## 14. Checklist - Toda Vez que a GitHub Action Rodar

**⚠️ IMPORTANTE**: Após cada execução do GitHub Actions (deploy), verifique apenas o que mudou:

### 14.1 Verificar Deploy no GitHub Actions

1. **GitHub** → **Actions** → Verificar se o workflow foi executado com sucesso (status verde ✓)
2. Se falhou:
   - Credenciais AWS expiradas → Atualizar secrets (seção 13.1)
   - Verificar logs do erro no GitHub Actions

### 14.2 Atualizar IP Público no API Gateway (Se Mudou)

- [ ] Verificar se o IP público do ECS Task mudou:
  - Vá em **ECS** → **Clusters** → `receitas-cluster` → **Tasks`
  - Clique na task mais recente
  - Copie o **Public IP**
- [ ] **Se o IP mudou**, atualizar o API Gateway:
  - Vá em **API Gateway** → `receitas-api-gateway` → **Resources**
  - Atualize os métodos:
    - `/recipes` → Endpoint URL: `http://<NOVO_IP>:80/recipes/`
    - `/recipes/{id}` → Endpoint URL: `http://<NOVO_IP>:80/recipes/{id}`
  - **Actions** → **Deploy API** → Stage `prod`

---

## Referências

- [Deploy App on AWS ECS Fargate using Github Actions](https://dev.to/aws-builders/deploy-app-on-aws-ecs-fargate-using-github-actions-13mf)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)

