/**
 * AWS Lambda Handler para gerar relatórios de receitas
 * 
 * Esta função Lambda consome o endpoint /recipes da API via API Gateway
 * e retorna estatísticas sobre as receitas.
 */

const API_GATEWAY_URL = process.env.API_GATEWAY_URL || 'https://reg5ao0oij.execute-api.us-east-1.amazonaws.com/prod';

export const handler = async (event, context) => {
    try {
        // Busca todas as receitas da API
        const response = await fetch(`${API_GATEWAY_URL}/recipes/`);
        
        if (!response.ok) {
            throw new Error(`API returned status ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Verifica se há dados
        if (!data || data.length === 0) {
            return {
                statusCode: 200,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    message: 'Nenhuma receita encontrada',
                    stats: {}
                }, null, 2)
            };
        }
        
        // Calcula estatísticas de tempo de cozimento
        const cookTime = {
            'receitas rápidas (<= 10 min)': data.filter(x => x.cook_time_minutes && x.cook_time_minutes <= 10).length,
            'receitas médias (> 10 min e <= 15 min)': data.filter(x => x.cook_time_minutes && x.cook_time_minutes > 10 && x.cook_time_minutes <= 15).length,
            'receitas longas (> 15 min)': data.filter(x => x.cook_time_minutes && x.cook_time_minutes > 15).length
        };
        
        // Calcula tempo médio de cozimento
        const recipesWithCookTime = data.filter(x => x.cook_time_minutes != null);
        const avgCookTime = recipesWithCookTime.length > 0
            ? Math.round(recipesWithCookTime.reduce((acc, item) => acc + item.cook_time_minutes, 0) / recipesWithCookTime.length)
            : 0;
        
        // Calcula tempo médio de preparo
        const recipesWithPrepTime = data.filter(x => x.prep_time_minutes != null);
        const avgPrepTime = recipesWithPrepTime.length > 0
            ? Math.round(recipesWithPrepTime.reduce((acc, item) => acc + item.prep_time_minutes, 0) / recipesWithPrepTime.length)
            : 0;
        
        // Calcula tempo total médio (prep + cook)
        const avgTotalTime = avgPrepTime + avgCookTime;
        
        // Estatísticas finais
        const stats = {
            'total_receitas': data.length,
            'tempo_de_cozimento': cookTime,
            'tempo_medio_cozimento_minutos': avgCookTime,
            'tempo_medio_preparo_minutos': avgPrepTime,
            'tempo_medio_total_minutos': avgTotalTime,
            'tempo_medio_cozimento': `Tempo médio de cozimento em nossas receitas: ${avgCookTime} minutos`,
            'tempo_medio_preparo': `Tempo médio de preparo em nossas receitas: ${avgPrepTime} minutos`
        };
        
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify(stats, null, 2)
        };
        
    } catch (error) {
        console.error('Erro ao processar requisição:', error);
        
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                error: 'Erro ao processar requisição',
                message: error.message,
                details: error.stack
            }, null, 2)
        };
    }
};
