# Registro de termos de uso (rastreio de conformidade)

> Não é aconselhamento jurídico. Termos mudam; reconfirme nas fontes oficiais antes de publicar.

## NBA.com — Terms of Use (documento fornecido pelo autor)
- Arquivo: `NBA_Logo.docx` — SHA-256 `2d5ae7743a601c388cce6e734672cebf005411007e0f3a48579cd8dfd01c2c3b` (registrado em `config/sources.yml`).
- **Seção "NBA Statistics"** (resumo, não literal): uso/exibição/publicação exige atribuição proeminente ao NBA.com;
  permitido apenas para jornalismo legítimo ou fins privados e não comerciais; proibido em patrocínio/identificação
  comercial, apostas, fantasy ou produto comercial, produtos com play-by-play, e **sites/produtos/serviços com banco de dados
  de estatísticas abrangente e atualizado regularmente sem consentimento prévio**.
- **Seção "Ownership and Use Restrictions"**: reuso/publicação de conteúdo para fins públicos ou comerciais exige permissão escrita; download para uso pessoal e não comercial é permitido.
- Busca por palavras-chave no documento não encontrou cláusula explícita sobre scraping/acesso automatizado nem sobre IA/ML. **Leitura integral ainda recomendada.**

## Basketball-Reference (Sports Reference) — NÃO verificado no site oficial
- Fonte da leitura: captura de terceiro (TOS Tracker, versão de abr/2026) + página oficial de tráfego de bots.
- Limite: 20 req/min (bloqueio de até 1 dia). Configuramos 10/min.
- Proibido (resumo): criar base que concorra/substitua a deles ou copiar parte materialmente significativa dos dados;
  scraping sem permissão que prejudique o site; **uso do conteúdo para treinar/ajustar/instruir modelos de IA, incluindo métodos de ML que prevejam/classifiquem/pontuem**.
- Permitido (resumo): compartilhar/usar/republicar dados de páginas individuais, com crédito explícito à fonte.

## Decisões de projeto derivadas
1. `data/` e `*.duckdb` nunca vão para o Git (raw e bronze são privados).
2. Só **dados agregados e derivados** são publicados, com atribuição a NBA.com e Basketball-Reference.
3. Sobre dados da BBR: apenas agregação, Monte Carlo e estatística descritiva. Clustering/aging/ML só sobre dados do NBA.com ou métricas próprias (caminho B).
4. Ingestão lenta, com cache; sem espelhar o site (somente tabelas necessárias).

## Perguntas em aberto
- Publicar um dashboard público com estatísticas derivadas do NBA.com é "jornalismo legítimo" ou "uso privado"? Zona cinzenta → considerar pedir consentimento escrito (NBA e Sports Reference).
- Ler os termos da BBR diretamente no site oficial e a página "Data Use".
