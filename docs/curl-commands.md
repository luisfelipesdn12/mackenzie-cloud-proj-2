# Comandos cURL para Postman

Substitua `localhost:8000` pela URL do seu servidor se for diferente.

## 1. GET Endpoint Raiz
```bash
curl --location 'http://localhost:8000/'
```

## 2. GET Todas as Receitas
```bash
curl --location 'http://localhost:8000/recipes/'
```

### GET Todas as Receitas com Paginação (offset=0, limit=10)
```bash
curl --location 'http://localhost:8000/recipes/?offset=0&limit=10'
```

## 3. GET Receita por ID
```bash
curl --location 'http://localhost:8000/recipes/1'
```

## 4. POST Criar Receita
```bash
curl --location 'http://localhost:8000/recipes/' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Biscoitos de Chocolate",
    "description": "Biscoitos caseiros clássicos de chocolate",
    "ingredients": "2 xícaras de farinha, 1 xícara de manteiga, 1 xícara de açúcar, 2 ovos, 1 xícara de gotas de chocolate",
    "instructions": "1. Misture manteiga e açúcar. 2. Adicione os ovos. 3. Adicione a farinha. 4. Misture as gotas de chocolate. 5. Asse a 180°C por 12 minutos.",
    "prep_time_minutes": 15,
    "cook_time_minutes": 12,
    "servings": 24
}'
```

### POST Criar Receita (Mínimo - apenas campos obrigatórios)
```bash
curl --location 'http://localhost:8000/recipes/' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Macarrão Simples",
    "ingredients": "macarrão, água, sal",
    "instructions": "Ferva a água, adicione sal, cozinhe o macarrão por 10 minutos"
}'
```

## 5. PUT Atualizar Receita (Atualização Completa)
```bash
curl --location --request PUT 'http://localhost:8000/recipes/1' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Biscoitos de Chocolate Atualizados",
    "description": "Descrição atualizada",
    "ingredients": "2 xícaras de farinha, 1 xícara de manteiga, 1 xícara de açúcar, 2 ovos, 1.5 xícaras de gotas de chocolate",
    "instructions": "1. Misture manteiga e açúcar. 2. Adicione os ovos. 3. Adicione a farinha. 4. Misture as gotas de chocolate. 5. Asse a 180°C por 15 minutos.",
    "prep_time_minutes": 20,
    "cook_time_minutes": 15,
    "servings": 30
}'
```

### PUT Atualizar Receita (Atualização Parcial - apenas nome)
```bash
curl --location --request PUT 'http://localhost:8000/recipes/1' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Novo Nome da Receita"
}'
```

### PUT Atualizar Receita (Atualização Parcial - múltiplos campos)
```bash
curl --location --request PUT 'http://localhost:8000/recipes/1' \
--header 'Content-Type: application/json' \
--data '{
    "description": "Apenas descrição atualizada",
    "prep_time_minutes": 25,
    "servings": 20
}'
```

## 6. DELETE Deletar Receita
```bash
curl --location --request DELETE 'http://localhost:8000/recipes/1'
```

---

## Exemplo de Fluxo Completo

### Passo 1: Criar uma receita
```bash
curl --location 'http://localhost:8000/recipes/' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Espaguete à Carbonara",
    "description": "Prato clássico italiano de massa",
    "ingredients": "400g de espaguete, 200g de pancetta, 4 ovos, 100g de queijo parmesão, pimenta preta",
    "instructions": "1. Cozinhe o espaguete. 2. Frite a pancetta. 3. Misture os ovos e o queijo. 4. Combine todos os ingredientes enquanto a massa está quente. 5. Adicione pimenta preta.",
    "prep_time_minutes": 10,
    "cook_time_minutes": 15,
    "servings": 4
}'
```

### Passo 2: Obter todas as receitas para ver a criada
```bash
curl --location 'http://localhost:8000/recipes/'
```

### Passo 3: Obter a receita específica (substitua {id} pelo ID do passo 2)
```bash
curl --location 'http://localhost:8000/recipes/1'
```

### Passo 4: Atualizar a receita (substitua {id} pelo ID real)
```bash
curl --location --request PUT 'http://localhost:8000/recipes/1' \
--header 'Content-Type: application/json' \
--data '{
    "servings": 6,
    "description": "Atualizado: Serve 6 pessoas"
}'
```

### Passo 5: Deletar a receita (substitua {id} pelo ID real)
```bash
curl --location --request DELETE 'http://localhost:8000/recipes/1'
```

