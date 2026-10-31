# 🏀 NBA GOAT Dual-Model Sensitivity Analysis (1974–2024)

[![dbt](https://img.shields.io/badge/dbt-1.12.6-orange)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.11.1-yellow)](https://duckdb.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)

## 📌 Visão Geral & Propósito
Este projeto quantifica o impacto do viés narrativo e dos prêmios de mídia no debate sobre quem é o maior jogador de basquete da história da NBA (GOAT).

Através da comparação de dois modelos estatísticos totalmente isolados via simulações de Monte Carlo com Priors de Dirichlet:
- **Modelo A (Pure On-Court / Estatístico):** Avalia estritamente eficiência, pico de 5 anos e volume acumulado (PER, BPM, VORP, WS), isolado de qualquer votação da mídia ou título coletivo.
- **Modelo B (Hardware & Accolades / Narrativo):** Avalia o legado narrativo, domínio em Finais e premiações oficiais (MVPs, FMVPs, All-NBA, All-Defensive).

---

## 🏗️ Arquitetura de Dados & SDLC (Medallion Architecture)

O pipeline utiliza **DuckDB** como Data Warehouse analítico local, transformado e auditado via **dbt**:
- **Bronze:** Ingestão bruta de estatísticas avançadas históricas por jogador/temporada (`bbr_season_advanced`).
- **Silver:** Normalização dos schemas em `stg_bbr_advanced` e isolamento do pool de candidatos em `int_goat_pool`.
- **Gold:** Tabelas multidimensionais e fatos (`fct_goat_season_zscores`, `gold_pool_candidates` e `gold_player_hardware`).
- **Práticas de SDLC e Qualidade:**
  - **Data Quality:** Suíte de testes automatizados `dbt test` (unicidade por atleta/temporada, plausibilidade estatística de WS e integridade referencial).
  - **Reprodutibilidade:** Transformações SQL versionadas no dbt, isolando a camada de persistência da simulação estocástica em Python.

---

## 🔬 Mitigação de Vieses Metodológicos

1. **Sample Size Bias (Viés do Tamanho da Amostra):**
   - *Desafio:* Jogadores em pico recente dominam médias por jogo em amostras curtas de carreira.
   - *Solução:* Decomposição vetorial balanceando **Pico das 5 Melhores Temporadas** com **Volume Acumulado**.
2. **Double Counting (Contagem Dupla):**
   - *Desafio:* Pontuar estatísticas avançadas (PER/WS) e prêmios (MVP) no mesmo modelo gera circularidade metodológica.
   - *Solução:* Isolamento 100% estrito entre o Modelo A (Estatístico) e o Modelo B (Hardware).
3. **Disparidade de Eras (1974–2024):**
   - *Desafio:* Métricas e prêmios foram introduzidos em épocas distintas da NBA.
   - *Solução:* Normalização Z-Score intra-temporada calculada exclusivamente ano a ano.

---

## 📊 Principais Descobertas & Painel Diagnóstico

### 1. Discrepância de Rankings (Dumbbell Plot)
![Dumbbell Plot](docs/assets/chart_1_dumbbell.png)

### 2. Sensibilidade ao Hardware (Ganhadores vs. Penalizados)
![Hardware Sensitivity](docs/assets/chart_2_sensitivity.png)

### 3. Reorganização da Hierarquia Histórica (Slope Chart)
![Slope Chart](docs/assets/chart_3_slope.png)

### 4. Matriz de Perfis Históricos (Scatter Quadrants)
![Scatter Quadrants](docs/assets/chart_4_quadrants.png)

---

## 📋 Análise de Casos Extremos & Anomalias de Modelo

Abaixo está o detalhamento dos atletas que apresentaram as maiores divergências estruturais entre a eficiência de quadra isolada (**Modelo A**) e o reconhecimento por títulos e premiações (**Modelo B**):

| Atleta | Rank Modelo A (Stats Puras) | Rank Modelo B (Hardware) | Variação (Δ) | Diagnóstico & Anomalia Metodológica |
| :--- | :---: | :---: | :---: | :--- |
| **Kobe Bryant** | **#19.97** | **#5.44** | **+14.53** | **O Maior Salto Narrativo:** No Modelo A (focado em PER/BPM/WS), Kobe fica fora do Top 15 devido à eficiência de arremesso e compartilhamento de posse. No Modelo B, dá um salto massivo de ~15 posições impulsionado por 5 Títulos, 2 FMVPs e 12x All-Defensive. |
| **Magic Johnson** | **#16.09** | **#5.29** | **+10.80** | **Eficiência x Volume x Títulos:** Apresenta médias de carreira altíssimas, mas sua aposentadoria precoce reduz o volume acumulado no Modelo A. No Modelo B, entra no Top 5 consolidado por 3x MVP, 3x FMVP e 5 Anéis em 13 temporadas. |
| **Tim Duncan** | **#13.78** | **#3.99** | **+9.79** | **Ancoragem Silenciosa:** O estilo de jogo utilitário e moderado de estatísticas por jogo o coloca em #13 no Modelo A, mas a consistência de 15x All-NBA, 15x All-Defensive e 5 Títulos o catapulta para o Top 4 do Modelo B. |
| **Chris Paul** | **#3.91** | **#25.86** | **-21.95** | **O Monstro da Eficiência sem Anéis:** Dono de uma das melhores razões de assistência/turnover e BPM da história (#4 em Stats), despenca 22 posições no Modelo B por nunca ter conquistado um título de campeão ou Finals MVP. |
| **James Harden** | **#6.73** | **#31.85** | **-25.12** | **A Maior Queda por Hardware:** Dominou métricas avançadas na década de 2010 (WS/VORP), garantindo Top 7 no Modelo A. A ausência de campeonatos o empurra para fora do Top 30 no Modelo B. |

---

### 🔍 Principais Insights Extraídos dos Dados

1. **A 'Cláusula Kobe & Magic' (O Peso do Anel na Percepção Histórica):**
   - Atletas com forte presença visual/narrativa e conquistas de time (Magic e Kobe) sofrem penalizações severas em modelos de estatísticas frias de box-score, mas dominam modelos que consideram prêmios da mídia.
2. **A Métrica Fria vs. O Teto de Campeão:**
   - Jogadores como **Chris Paul** e **James Harden** provam que estatísticas avançadas (PER/BPM/WS) tendem a inflar criadores de jogadas de alta posse de bola, mas o filtro de Hardware é implacável com a ausência de anéis.
3. **Consistência Absoluta no Topo (Tier 0):**
   - **Michael Jordan** e **LeBron James** são os únicos atletas que permanecem no **Top 2 em ambas as metodologias**, demonstrando que sua grandeza transcende qualquer debate entre *analytics* e narrativa clássica.

---

## 🧠 Conclusão da Análise: *Who is the GOAT?*

A resposta depende diretamente de como sua metodologia define "Grandeza":

1. **Se o critério for Eficiência Absoluta & Produção Individual (Modelo A):**
   - **LeBron James** é o GOAT (#1.00). Sua longevidade de 20+ temporadas em alto nível acumulou um volume inalcançável de VORP, Win Shares e picos de BPM, superando estatisticamente qualquer outro atleta.

2. **Se o critério for Narrativa, Domínio de Eras & Títulos (Modelo B):**
   - **Michael Jordan** é o GOAT (#1.10). Sua taxa de conversão em Finais (6/6 FMVPs), somada a 5 MVPs e 9 seleções All-Defensive, cria um "teto de hardware" imbatível.

3. **O Veredito Consenso (Monte Carlo Combined):**
   - **Michael Jordan** e **LeBron James** formam uma classe isolada (Tier 0). 
   - A inclusão do Hardware penaliza severamente atletas de alta eficiência sem anéis (ex: Chris Paul caindo 22 posições e James Harden caindo 25 posições), provando quantitativamente que a **percepção histórica da mídia inflaciona o valor de títulos coletivos sobre a eficiência individual**.

---

## 📐 Validação Estatística & Matriz de Confusão

Para avaliar a convergência entre a eficiência pura de quadra (Modelo A) e o reconhecimento por premiações/títulos (Modelo B), classificamos a capacidade do Modelo A em prever a entrada de um jogador no **TOP 3 Histórico (GOAT Tier)**:

### 1. Métricas de Desempenho do Modelo
- **Acurácia Global:** **87.5%** *(7 de 8 classificações de elite convergiram entre os modelos)*
- **Precisão (TOP 3):** **66.7%**
- **Recall (Sensibilidade TOP 3):** **100.0%** *(O Modelo A identificou 100% dos atletas que atingiram o TOP 3 de Hardware)*
- **F1-Score:** **0.80**

### 2. Matriz de Confusão (Predição de Elite TOP 3)

| | Previsto TOP 3 (Modelo A) | Previsto Fora do TOP 3 (Modelo A) |
| :--- | :---: | :---: |
| **Real TOP 3 (Modelo B)** | **2 (Verdadeiros Positivos)**<br>*(Jordan, Kareem)* | **0 (Falsos Negativos)**<br>*(Nenhum elite foi omitido)* |
| **Real Fora do TOP 3 (Modelo B)** | **1 (Falso Positivo)**<br>*(LeBron James - #1 em Stats, #2.77 em Hardware)* | **5 (Verdadeiros Negativos)**<br>*(Duncan, Kobe, Magic, CP3, Harden)* |

> **Diagnóstico da Matriz:** O único "Falso Positivo" do Modelo A no Top 3 foi LeBron James, demonstrando que a eficiência pura o coloca no topo absoluto, enquanto o acúmulo de Hardware de Jordan e Kareem o desloca levemente no Modelo B.

---

## ⚠️ Limitações Metodológicas & Análise de Vieses Estruturais

1. **Pace Bias (Ritmo de Jogo):** Eras aceleradas (anos 80) inflacionam estatísticas de volume em relação a eras defensivas lentas (anos 2000). *Mitigação:* Z-Scores normalizados intra-temporada.
2. **Data Availability Bias (Pré-1974):** A ausência de tocos, roubos e play-by-play em eras antigas subestima a produção defensiva avançada de lendas pré-1974. *Mitigação:* Foco analítico restrito à era 1974–2024.
3. **Media & Narrative Bias (Voter Fatigue):** O Modelo B herda escolhas jornalísticas subjetivas de MVP/All-NBA. *Mitigação:* Balanceamento com Finals MVPs e campeonatos como protagonista.
4. **Supporting Cast Bias (Contexto de Equipe):** Títulos e Win Shares dependem da estrutura da franquia, beneficiando jogadores de dinastias (Duncan, Magic). *Mitigação:* Distribuições Dirichlet em Monte Carlo variando a relevância do hardware.
5. **Usage vs. Efficiency Bias:** PER e True Shooting % favorecem armadores de alto aproveitamento, penalizando arremessadores de volume sob pressão (Kobe Bryant). *Mitigação:* Visualização isolada na Matriz de Perfis Históricos.

---

## 🚀 Como Executar o Projeto Localmente

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar o pipeline dbt (Build & Test)
python -m dbt.cli.main run --project-dir dbt --profiles-dir dbt
python -m dbt.cli.main test --project-dir dbt --profiles-dir dbt

# 3. Executar o confronto dos modelos
python scripts/compare_models.py