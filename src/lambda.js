const data = [
    {
        "id": 1,
        "name": "Brigadeiro Clássico",
        "description": "O doce mais amado do Brasil, perfeito para festas e sobremesas",
        "ingredients": "1 lata de leite condensado, 1 colher de sopa de manteiga, 4 colheres de sopa de chocolate em pó, chocolate granulado para decorar",
        "instructions": "1. Em uma panela, misture o leite condensado, a manteiga e o chocolate em pó. 2. Leve ao fogo médio, mexendo sempre até soltar do fundo da panela. 3. Deixe esfriar, unte as mãos com manteiga e faça bolinhas. 4. Passe no chocolate granulado e coloque em forminhas.",
        "prep_time_minutes": 5,
        "cook_time_minutes": 15,
        "servings": 20
    },
    {
        "id": 2,
        "name": "Spaghetti à Carbonara",
        "description": "Massa italiana cremosa com bacon e queijo parmesão",
        "ingredients": "400g de spaghetti, 200g de bacon em cubos, 4 ovos, 100g de queijo parmesão ralado, sal e pimenta-do-reino a gosto",
        "instructions": "1. Cozinhe o spaghetti em água fervente com sal até ficar al dente. 2. Frite o bacon até ficar crocante. 3. Bata os ovos com o queijo ralado. 4. Escorra a massa e misture com o bacon. 5. Desligue o fogo e adicione a mistura de ovos, mexendo rapidamente. 6. Tempere com pimenta e sirva imediatamente.",
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "servings": 4
    },
    {
        "id": 3,
        "name": "Tacos de Frango",
        "description": "Tacos mexicanos com frango temperado e guacamole caseiro",
        "ingredients": "500g de peito de frango em tiras, 8 tortillas de milho, 2 abacates, 1 tomate, 1 cebola, suco de 1 limão, coentro, cominho, páprica, sal",
        "instructions": "1. Tempere o frango com cominho, páprica e sal. 2. Grelhe o frango até dourar. 3. Amasse os abacates e misture com tomate picado, cebola, limão e coentro. 4. Aqueça as tortillas. 5. Monte os tacos com frango e guacamole.",
        "prep_time_minutes": 15,
        "cook_time_minutes": 12,
        "servings": 4
    },
    {
        "id": 4,
        "name": "Salada Caesar",
        "description": "Salada clássica com alface romana, croutons e molho Caesar",
        "ingredients": "1 pé de alface romana, 150g de peito de frango grelhado, 100g de parmesão, croutons, 2 colheres de maionese, 1 colher de mostarda Dijon, suco de limão, anchovas, alho",
        "instructions": "1. Lave e rasgue a alface. 2. Prepare o molho batendo maionese, mostarda, limão, anchovas e alho. 3. Corte o frango em tiras. 4. Misture tudo com croutons e parmesão em lascas.",
        "prep_time_minutes": 15,
        "cook_time_minutes": 10,
        "servings": 2
    },
    {
        "id": 5,
        "name": "Bolo de Cenoura com Cobertura de Chocolate",
        "description": "Bolo fofinho de cenoura com irresistível cobertura de chocolate",
        "ingredients": "3 cenouras médias, 3 ovos, 1 xícara de óleo, 2 xícaras de açúcar, 2 xícaras de farinha de trigo, 1 colher de fermento. Cobertura: 4 colheres de chocolate em pó, 2 colheres de manteiga, 3 colheres de açúcar, 1 xícara de leite",
        "instructions": "1. Bata no liquidificador cenouras, ovos e óleo. 2. Misture com açúcar, farinha e fermento. 3. Asse em forma untada a 180°C por 40 minutos. 4. Ferva os ingredientes da cobertura até engrossar e despeje sobre o bolo.",
        "prep_time_minutes": 20,
        "cook_time_minutes": 40,
        "servings": 12
    },
    {
        "id": 6,
        "name": "Risoto de Cogumelos",
        "description": "Risoto cremoso italiano com cogumelos frescos e parmesão",
        "ingredients": "300g de arroz arbóreo, 300g de cogumelos variados, 1 litro de caldo de legumes, 1 cebola picada, 100ml de vinho branco, 50g de manteiga, 100g de parmesão ralado, azeite, sal",
        "instructions": "1. Refogue a cebola no azeite. 2. Adicione o arroz e torre por 2 minutos. 3. Adicione o vinho e deixe evaporar. 4. Vá adicionando o caldo aos poucos, mexendo sempre. 5. Adicione os cogumelos salteados. 6. Finalize com manteiga e parmesão.",
        "prep_time_minutes": 10,
        "cook_time_minutes": 30,
        "servings": 4
    },
    {
        "id": 7,
        "name": "Hambúrguer Artesanal",
        "description": "Hambúrguer suculento com queijo cheddar e bacon crocante",
        "ingredients": "500g de carne moída (patinho), 4 pães de hambúrguer, 4 fatias de queijo cheddar, 8 fatias de bacon, alface, tomate, cebola roxa, picles, maionese, sal, pimenta",
        "instructions": "1. Tempere a carne com sal e pimenta e faça 4 hambúrgueres. 2. Grelhe os hambúrgueres por 4 minutos de cada lado. 3. Frite o bacon. 4. Monte o hambúrguer com todos os ingredientes nos pães tostados.",
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
        "servings": 4
    },
    {
        "id": 8,
        "name": "Pad Thai",
        "description": "Clássico macarrão tailandês agridoce com camarões e amendoim",
        "ingredients": "200g de macarrão de arroz, 300g de camarões, 2 ovos, brotos de feijão, cebolinha, amendoim torrado, molho de peixe, molho de tamarindo, açúcar mascavo, suco de limão, alho",
        "instructions": "1. Hidrate o macarrão. 2. Refogue alho e camarões. 3. Adicione ovos mexidos. 4. Junte o macarrão e molhos (peixe, tamarindo, açúcar, limão). 5. Finalize com brotos, cebolinha e amendoim triturado.",
        "prep_time_minutes": 20,
        "cook_time_minutes": 10,
        "servings": 2
    },
    {
        "id": 9,
        "name": "Feijoada Completa",
        "description": "Prato típico brasileiro com feijão preto e carnes variadas",
        "ingredients": "1kg de feijão preto, 500g de costelinha de porco, 300g de linguiça calabresa, 200g de bacon, 200g de carne seca, 2 folhas de louro, alho, cebola, sal, pimenta",
        "instructions": "1. Deixe o feijão de molho overnight. 2. Cozinhe o feijão com as carnes, louro, alho e cebola. 3. Cozinhe por cerca de 2 horas até as carnes ficarem macias. 4. Ajuste o sal e sirva com arroz, couve, laranja e farofa.",
        "prep_time_minutes": 30,
        "cook_time_minutes": 120,
        "servings": 8
    },
    {
        "id": 10,
        "name": "Cheesecake de Frutas Vermelhas",
        "description": "Torta cremosa de queijo com calda de frutas vermelhas",
        "ingredients": "200g de biscoito maisena triturado, 100g de manteiga derretida, 600g de cream cheese, 200g de açúcar, 3 ovos, 200ml de creme de leite, baunilha. Calda: 300g de frutas vermelhas congeladas, 100g de açúcar",
        "instructions": "1. Misture biscoito e manteiga, forre uma forma e leve à geladeira. 2. Bata cream cheese, açúcar, ovos, creme e baunilha. 3. Despeje sobre a base e asse em banho-maria a 160°C por 50 minutos. 4. Deixe esfriar. 5. Cozinhe frutas com açúcar para a calda e despeje sobre a torta.",
        "prep_time_minutes": 25,
        "cook_time_minutes": 50,
        "servings": 10
    }
]

async function reports() {
    try {
        data = await fetch('http://xxxxxx/reports').
            then(request = request.json())
        const cookTime = {
            'receitas rápidas (<= 10 min)': data.filter(x => x.cook_time_minutes <= 10).length,
            'receitas médias  (<= 15 min)': data.filter(x => x.cook_time_minutes > 10 && x.cook_time_minutes <= 15).length,
            'receitas longas (> 15 min)': data.filter(x => x.cook_time_minutes > 15).length
        }
        const avgCookTime = `Tempo médio de cozimento em nossas receitas: ${Math.round(data.reduce((acc, item) => {
            return acc + item.cook_time_minutes;
        }, 0) / data.length, 0)} minutos`
        const stats = {
            'Tempo de Cozimento': cookTime,
            'Tempo médio de Cozimento': avgCookTime
        }
        return JSON.stringify(stats, undefined, 4)
    } catch (error) {
        `Erro ao processar requisição. ${error}`
    }
}
