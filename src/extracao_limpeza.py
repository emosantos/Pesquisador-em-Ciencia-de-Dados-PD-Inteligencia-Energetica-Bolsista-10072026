import pandas as pd
import numpy as np

def carregar_e_limpar(consumer_path='consumer_unit_data.xlsx', power_plant_path='power_plant_data.xlsx'):
    """
    Carrega, limpa e padroniza as bases da Digital Grid.
    Garante idempotência e gera o relatório de qualidade exigido na Q0.
    """
    # 1. Leitura dos arquivos brutos
    df_cons_raw = pd.read_excel(consumer_path)
    df_gen_raw = pd.read_excel(power_plant_path)
    
    # Criando dicionário para o relatório de qualidade
    relatorio = {
        'Métrica / Filtro': [],
        'Registros Impactados': [],
        'Ação Tomada': [],
        'Justificativa Negócio': []
    }
    
    # --- PROCESSAMENTO: BASE DE GERAÇÃO ---
    # Renomeando colunas
    df_gen = df_gen_raw.rename(columns={
        'Geração Mensal Referência Month': 'data_referencia',
        'Unidade Consumidora (UC) Usina (Nickname)': 'usina',
        'Geração Mensal SUM Energia Gerada (kWh)': 'g'
    })
    
    # Remover linha com data NaT (Registro órfão encontrado no index 0)
    linhas_antes_gen = len(df_gen)
    df_gen = df_gen.dropna(subset=['data_referencia'])
    linhas_removidas_gen = linhas_antes_gen - len(df_gen)
    
    # --- PROCESSAMENTO: BASE DE CONSUMO ---
    # Renomeando colunas
    df_cons = df_cons_raw.rename(columns={
        'Geração Mensal Referência Month': 'data_referencia',
        'Unidade Consumidora (UC) Número de Instalação': 'uc',
        'Conta Consumo (kWh)': 'ec',
        'Conta Saldo Acumulado (kWh)': 'cr'
    })
    
    # Tratamento de Consumos Negativos (Truncar em 0)
    consumos_negativos = (df_cons['ec'] < 0).sum()
    df_cons.loc[df_cons['ec'] < 0, 'ec'] = 0
    
    # Tratamento de Duplicatas (Agrupamento por UC e Mês)
    # Somamos o consumo (ec) e mantemos o último saldo (cr)
    linhas_antes_dedup = len(df_cons)
    
    df_cons_limpo = df_cons.groupby(['data_referencia', 'uc']).agg({
        'ec': 'sum',
        'cr': 'last'
    }).reset_index()
    
    linhas_agrupadas = linhas_antes_dedup - len(df_cons_limpo)
    
    # --- CONSTRUÇÃO DO RELATÓRIO DE QUALIDADE ---
    relatorio = pd.DataFrame({
        'Etapa/Dataset': ['Geração', 'Consumo', 'Consumo'],
        'Anomalia Detectada': ['Registro com data nula (NaT)', 'Valores de consumo (Ec) negativos', 'Registros duplicados (Mesma UC/Mês)'],
        'Volumetria': [linhas_removidas_gen, consumos_negativos, linhas_agrupadas * 2 if linhas_agrupadas > 0 else 0],
        'Tratamento Adotado': ['Remoção da linha (Drop)', 'Substituição (Truncado para 0)', 'Agrupamento (Soma do Ec e Último Cr)'],
        'Justificativa': [
            'Evitar ruído na série temporal da usina.',
            'Consumo físico não pode ser negativo; assume-se faturamento zerado no mês.',
            'Garantir a integridade estrutural para que a soma dos rateios (Sigma P) resulte em 1.'
        ]
    })
    
    return df_cons_limpo, df_gen, relatorio

# Execução no Notebook:
# df_consumo, df_geracao, df_qualidade = carregar_e_limpar()
# display(df_qualidade)