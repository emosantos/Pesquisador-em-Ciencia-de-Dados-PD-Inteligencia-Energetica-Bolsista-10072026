# Desafio Técnico de Data Science — Digital Grid

Vaga: Pesquisador em Ciência de Dados — P&D Inteligência Energética (Bolsista)

Duração máxima: 3 horas

## Introdução: Geração Distribuída e Gestão Inteligente de Energia

Bem-vindo ao desafio técnico da Digital Grid! Este teste foi desenhado para avaliar suas habilidades em Data Science aplicadas ao setor de energia, com foco em **Geração Distribuída (GD)**. Nossa missão é criar modelos que otimizem a previsão de consumo, antecipem a geração de energia limpa e mapeiem o comportamento dos créditos de energia em larga escala.
No Brasil, o crescimento da GD trouxe o **Sistema de Compensação de Energia Elétrica (SCEE)**. Nele, a energia excedente gerada por uma usina é injetada na rede e convertida em créditos para abater o consumo futuro de múltiplas Unidades Consumidoras (UCs). O grande desafio é o **rateio (alocação) desses créditos**. Historicamente feito de forma estática, esse processo gera ineficiências devido à intermitência climática e à variação de consumo.
A Digital Grid automatiza e otimiza esse processo usando inteligência preditiva. Este teste simula desafios reais que enfrentamos no dia a dia.

---

## Recursos Fornecidos

Dois arquivos, na raiz deste repositório.

**`consumer_unit_data.xlsx`** — Histórico de consumo e saldo acumulado de créditos de várias UCs que estão atreladas a uma Usina. Vai de **julho/2023 a junho/2026** (36 meses).

**`power_plant_data.xlsx`** — Histórico de geração de uma Usina Teste que é a usina em questão. Vai de **julho/2022 a junho/2026** (48 meses) — repare que a janela **não** é a mesma da base de consumo.

Os dados são derivados de uma carteira real, anonimizados — **com os defeitos que dados de produção têm**. Não fizemos limpeza para você.

---

## Notação

| Símbolo | Significado |
| --- | --- |
| `Ec` | Energia consumida (kWh) |
| `OpF` | Quota de perfil — use `1.0` (100%) |
| `ECA` | Energia consumida aparente = `Ec × OpF` |
| `D` | Custo de disponibilidade — use `0` |
| `Cr` | Crédito acumulado na UC antes do rateio |
| `Co` | Cobertura — necessidade real de injeção de novos créditos |
| `P` | Percentual de rateio alocado para a UC |
| `G` | Geração total da usina |

**Mês de referência para todo o desafio: `2026-06-01`.**

---

## Q0 — Contrato de dados

Antes de qualquer modelo, construa a fundação.

Escreva uma função `carregar_e_limpar()` que leia os dois arquivos e devolva os dados
prontos para análise. Ela deve ser **idempotente** (rodar duas vezes dá o mesmo
resultado) e deve produzir um **relatório de qualidade**: uma tabela com quantos
registros entraram, quantos foram descartados ou corrigidos, e **por quê**.

Documente cada decisão de limpeza. Não existe resposta única. Porém, as decisões precisam ser bem justificadas.

---

## Q1 — Cobertura e rateio

Implemente a lógica de alocação de créditos:

1. **Consumo aparente:** `ECA = Ec × OpF`
2. **Cobertura:** a UC só precisa de crédito novo se o consumo aparente superar o
   saldo que ela já tem.
   `Co = ECA − (Cr + D)` se `ECA > (Cr + D)`; caso contrário `Co = 0`.
3. **Percentual de rateio:** `P = Co / Σ(Co de todas as UCs da usina)`

Sua função deve **receber o mês como parâmetro** e funcionar para qualquer mês do
histórico — não apenas o de referência.

O rateio é feito sobre o **consumo faturado** do mês — ou seja, o *valor* de cada linha
entra como está. Se você decidir imputar ou corrigir um valor, essa correção vale para a
modelagem (Q3), não para o rateio.

Isso vale para o **valor**, e não dispensa você de tratar a **estrutura** da base: se a
mesma UC aparece mais de uma vez no mesmo mês, o rateio dela está errado.

**Valide** que `Σ P = 1` — e pergunte-se se essa validação prova mesmo que o seu rateio
está correto.

**Responda no notebook:** o que acontece matematicamente com `P` se `Σ Co = 0`, ou
seja, se nenhuma UC precisar de crédito naquele mês? Como você trataria isso em
produção?

---

## Q2 — SQL

Carregue os dados **limpos** da Q0 em um banco (SQLite, DuckDB — sua escolha) e
escreva **uma única query** que retorne, para o mês de referência:

```
uc | eca | cr | co | p
```

com `Co` e `P` calculados **em SQL**, não em Python. O resultado deve bater com o da
Q1.

---

## Q3 — Previsão de consumo

Preveja o `Conta Consumo (kWh)` de **2026-07-01** para as **Top 10 UCs** por consumo
histórico.

- **Split:** treine com dados até `2026-05-01` e valide em `2026-06-01`.
- **Modelos:** um *baseline* estatístico simples e um modelo mais avançado.
  **Justifique a escolha do modelo à luz do tamanho e da estrutura dos dados** — não
  há vantagem por usar a ferramenta mais sofisticada, há vantagem por usar a adequada.
- **Métricas:** MAPE e MAE. Se alguma delas se comportar mal com estes dados, diga
  isso e proponha alternativa.
- **Compare** baseline vs. modelo avançado e explique **por que** um superou o outro.
  Se o baseline venceu, diga que venceu.
- Lembre-se: você validou em junho, mas o pedido é prever **julho**.

---

## Q4 — Rebalanceamento

A Digital Grid tem um sistema chamado **REBALANCE**, que redistribui energia para
evitar vacância e overbooking. Simule uma versão simplificada.

**Cenário:** a carteira tem crédito preso em UCs que não vão usá-lo. O REBALANCE
recupera esse crédito e o devolve a quem precisa.

1. **Calcule o excedente.** A partir dos seus dados limpos, apure quanto crédito está
   parado hoje em UCs que não consomem mais. Esse é o montante a redistribuir — não
   damos o número; ele sai da sua Q0.
2. **Redistribua entre as UCs ativas.** Escreva uma função que faça a alocação.
   - **Não distribua igualmente.** Priorize quem traz mais segurança ao negócio, e
     explique o critério. Se a Q3 ficou pronta, use a previsão; se não, use o histórico.
   - **Restrição obrigatória:** nenhuma UC pode **terminar** com saldo acima de **1 mês**
     do seu consumo médio dos últimos 12 meses. Crédito parado é crédito desperdiçado —
     é justamente o problema que estamos consertando.
   - UCs que **já** estão acima desse teto não recebem nada.
3. **Demonstre** em um DataFrame o saldo de cada UC antes e depois.

**Responda:** sobrou crédito que não coube em ninguém? Quanto? O que a Digital Grid
deveria fazer com ele?

---

## Q5 — Exploração e visão de negócio

**Qualidade:** que anomalias você encontrou nos dados? Como trataria cada uma numa
pipeline de produção (ETL)?

**Insights:** proponha **duas ações de negócio** concretas para a Digital Grid, com
base no que você viu. Ação de negócio é algo que alguém pode *fazer na segunda-feira* —
não é uma observação.

> Exemplo do formato esperado: *"20% das UCs concentram 80% do crédito ocioso.
> Recomendo um alerta automático que sinalize toda UC cujo saldo passe de N meses de
> consumo, para realocação."*

---

## Entrega

### 1. O código, num fork deste repositório

Faça um **fork** deste repositório (botão *Fork*, no topo da página), trabalhe nele e
nos mande o link do seu fork. Não abra Pull Request — assim um candidato não vê a
solução do outro.

O fork deve conter:

- um **Jupyter Notebook (.ipynb)** documentado, com as respostas e o raciocínio;
- um **`requirements.txt`** (ou `environment.yml`, ou `pyproject.toml`) — precisamos
  conseguir rodar seu código;
- um **`SOLUCAO.md`** curto, ou uma seção inicial no notebook, dizendo o que você fez,
  o que deixou de fora e por quê.

**Commite ao longo do trabalho**, não tudo de uma vez no fim. O histórico faz parte da
entrega: queremos ver como você pensou, não só onde chegou.

### 2. Um vídeo de 3 a 5 minutos

Não listado (YouTube, Loom, Drive), apresentando a solução como se fosse para o CTO e o
time de Produto:

- **1 min** — o problema: o que é o rateio na GD, e a dor da vacância/overbooking.
- **2 min** — a solução: qual modelo venceu na Q3 e **por quê**; como você pensou o
  rebalanceamento da Q4.
- **1 min** — o insight mais interessante da Q5 e o que a Digital Grid faz com ele.

### Para onde enviar

Mande **o link do seu fork** e **o link do vídeo** para **lucas@dg.energy**, com o
assunto:

```
Desafio Data Science — <seu nome completo>
```

---

## Como avaliamos

1. **Qualidade de dados (Q0/Q5)** — as anomalias que você encontrou e como as tratou.
   É o critério que mais pesa, de longe.
2. **Rigor na modelagem (Q3)** — o *porquê* por trás das métricas, não o número.
3. **Lógica de negócio (Q4)** — a priorização é defensável? conversa com a Q3?
4. **Correção técnica (Q1/Q2)** — fórmulas certas, código vetorizado, em funções.
5. **Insight acionável (Q5)** — algo que alguém possa fazer na segunda-feira.
6. **Comunicação** — notebook legível e vídeo sem jargão.

Boa sorte.
