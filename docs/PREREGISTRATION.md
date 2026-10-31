# Pré-registro da regra do pool

Objetivo: impedir que o pool de candidatos seja calibrado olhando o ranking.

1. Explore a **distribuição** dos dados (silver) para calibrar parâmetros — sem gerar nenhum ranking.
2. Feche os valores em `dbt/dbt_project.yml` (`vars:`), removendo os rótulos DRAFT.
3. `git commit` e `git tag pool-rule-v1`. Anote o hash do commit no README.
4. Só então rode `gold_pool_candidates` e as etapas de ranking.
5. Qualquer mudança posterior exige nova tag (`pool-rule-v2`) e fica registrada, com justificativa, no README.
