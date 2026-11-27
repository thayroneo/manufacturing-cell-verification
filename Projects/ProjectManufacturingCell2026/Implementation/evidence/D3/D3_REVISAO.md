# D3 — Revisão local para veredito do responsável

**Estado:** REVIEW_COMPLETED_PUBLICATION_AUTHORIZED  
**Maturidade:** TECHNICAL_REVIEWED_SYNTHETIC  
**Data:** 27/11/2026, America/Fortaleza

## Conferência das evidências

- FACT: 41 pares log/monitor conferidos no CLI real: 29 resultados PASS e 12 violações intencionais previstas. Todos corresponderam à previsão; nenhum erro de parser, ordenação ou execução nesses resultados.
- FACT: 19 testes JUnit e nove testes Python passaram. A contagem Python é lida da execução, e não fixada no relatório.
- FACT: compilação do modelo original e do D2 concluída. A regressão corrigida do D2 explorou os 1.000 schedules solicitados, seed 42, sem bugs. Isso não é uma repetição da campanha histórica de 100.000 schedules.
- FACT: os hashes dos 16 logs coincidem com o manifesto. Código, monitores, testes e saídas históricos do D2 e exemplos originais permanecem inalterados.
- FACT: o PDF final tem oito páginas. Seu texto, as dez premissas, as 30 discussões de validade e todas as 41 linhas da matriz foram confrontados com as fontes. As oito páginas foram renderizadas e inspecionadas visualmente, sem cortes ou conteúdo ausente. O hash do PDF está em `review.json`.

## Ajustes realizados durante a revisão

1. O relatório agora explica que 41/41 inclui violações intencionais corretamente detectadas, e não 41 execuções sem violações.
2. Foram explicitadas as 28 adaptações ainda abertas ao fim das simulações. Elas não compõem a distribuição das 6.680 adaptações concluídas. O limite de oito ticks continua sendo uma escolha empírica para o corpus.
3. As limitações do relatório foram apresentadas em português, e a data de execução passou a ser obtida dos metadados.
4. O verificador passou a rejeitar resultados com erros de parser, ordenação ou execução mesmo quando também existe uma assertiva. Uma aprovação também exige eventos e chaves efetivamente verificados. Violações no primeiro evento permanecem válidas mesmo sem uma chave concluída com sucesso.
5. O runner agora exige a exploração completa dos schedules solicitados e obtém a contagem real dos testes Python. Três testes de regressão adicionais cobrem erros simultâneos, entrada vazia e exploração incompleta.

Depois desses ajustes, a campanha completa foi novamente executada com sucesso. `summary.json`, `results.json`, `commands.json`, `versions.json` e as saídas brutas registram essa execução.

## Fechamento da pendência documental

A revisão anterior continha apenas limitações resumidas e não atendia integralmente à discussão individual de premissas solicitada pela seção 7.7. Essa lacuna foi corrigida no complemento atual.

- FACT: `ManufacturingCell/D3_PREMISSAS.md` completa a tabela com as dez premissas, sua contraparte real, aproximação, propriedades afetadas e situação no D3.
- FACT: cada premissa P01–P10 é discutida uma vez sob validade interna, uma vez sob validade de construto e uma vez sob validade externa: 30 análises explícitas, com evidências e limites.
- FACT: o gerador incorpora essa fonte automaticamente ao relatório; a nova tabela é renderizada como tabela em HTML/PDF. A análise não depende de uma edição manual que seria perdida na próxima execução.
- FACT: a campanha completa foi executada após a alteração: 41/41 vereditos esperados, 19 JUnit, nove testes Python e 1.000 schedules de regressão D2, todos conforme os critérios registrados.
- FACT: a seção 5 de `ManufacturingCell/INSTRUCTIONS.md` agora registra os resultados locais D3 separadamente das referências históricas.

## Conferência do escopo D3

| Exigência | Evidência local | Situação |
|---|---|---|
| Pacote PObserve, parser, JUnit e runner — seção 8 | `gradle_build.txt`, `junit/`, código e `D3_GUIA.md` | Atendida localmente |
| Exemplos two-phase/naive — seção 7.4 | `results.json`, `pobserve/original_*/` | Aprovações e violações previstas confirmadas |
| Logs com dois técnicos — seção 8 | `logs/two_technicians_*.log`, resultados S4 e demais monitores | Pré-correção e correção verificadas |
| Falhas reais do sistema R1/R2 — seção 7.4 | `system_sanction_suppressed`, `system_commit_delayed`, proveniência em `cases.json` | Detectadas com logging fiel à simulação |
| Pelo menos dois defeitos de log, originais preservados e causas explicadas — seção 7.4 | Quatro mutações `log_*`, `original_twophase.log`, relatório e guia | Atendida; os alarmes aparentes são distinguidos das falhas do sistema |
| Calibração ADAPT_START até COMMIT, incluindo protocolo — seções 7.4 e 8 | `calibration.json`, seeds 64/299 e resultados R2 | B=8 empírico; pendências no EOF declaradas |
| Comandos, versões, seeds, saídas e reprodução — ASSIGNMENT.md | `commands.json`, `versions.json`, `cases.json`, saídas brutas e guia | Registrados |
| Premissas e validade — seção 7.7 | Fonte `D3_PREMISSAS.md` incorporada no relatório final | Tabela e três categorias completas |
| Instrumentação JaCaMo — extensão opcional da seção 7.4 | Não executada | Opcional; não apresentada como conclusão do D3 |

INFERENCE / TECHNICAL_REVIEWED_SYNTHETIC: a pendência documental identificada foi resolvida e os itens técnicos e documentais do escopo D3 conferido estão atendidos nesta entrega local. Publicação e avaliação pelo responsável são passos separados; esta conclusão não equivale à aprovação do avaliador nem à validação física da célula.

## Limites da conclusão

INFERENCE: o material está tecnicamente consistente para a avaliação do responsável pelo D3, dentro dos cenários e ferramentas registrados.

Os dados são sintéticos. Não houve validação de uma célula física, garantia para todas as execuções futuras nem prova de refinamento do simulador em relação ao modelo assíncrono P. As 1.000 simulações usadas na calibração medem durações; não são 1.000 execuções verificadas integralmente por PObserve.

## Autorização de publicação

A revisão técnica e documental foi concluída, e o usuário autorizou a etapa 2: criar o commit e publicar a branch `d3-runtime` no GitHub. A revisão usou como base `1543a98f3d98b1cec6696b018ff0f66ccaefa9b8`; o resultado do envio será confirmado pelas referências Git locais e remotas. Essa autorização não altera os resultados nem o alcance da validação. A etapa 3, de entrega formal, permanece adiada.
