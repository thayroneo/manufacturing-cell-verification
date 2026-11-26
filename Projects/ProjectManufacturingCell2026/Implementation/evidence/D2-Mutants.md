# D2 — Mutants

## Objetivo

Esta campanha verifica se os monitores do modelo detectam violações introduzidas deliberadamente. Cada mutant foi executado no projeto `Implementation/ManufacturingCellTeam.pproj` com estratégia aleatória e limite de 1.000 schedules.

## Resultado da campanha

| Mutant | Alteração exercitada | Teste | Seed | Resultado |
|---|---|---|---:|---|
| S1 | entrada sem a condição de segurança | `tcMutantS1` | 3271887019 | 1 bug no primeiro schedule |
| S2 | remoção da proteção de entrada | `tcMutantS2` | 3662861277 | 1 bug no primeiro schedule |
| S3 | obrigação de saída não cumprida | `tcMutantS3` | 2539613659 | 1 bug no primeiro schedule |
| L1 | obrigação normativa ausente | `tcMutantL1` | 3953499931 | 1 bug no primeiro schedule |
| L2 | adaptação iniciada sem condição válida | `tcMutantL2` | 1266211740 | 1 bug no primeiro schedule |
| L3 | adaptação iniciada fora do protocolo | `tcMutantL3` | 3079806130 | 1 bug no primeiro schedule |
| R3 | `COMMIT` antes de `HUMAN_ENTER` | `tcMutantR3` | 1742197821 | 1 bug no primeiro schedule |

S4 é tratado como o cenário comportamental pré-correção: dois técnicos podem reabrir o recurso enquanto ainda há uma pessoa dentro. Esse cenário foi reproduzido por `tcCellTwoTechniciansPreFix` em 6 schedules, com o trace `output/verification/ET2-final-S4-trace.txt`.

## Evidências

Para cada mutant, a saída completa está em `output/verification/ET2-final-tcMutant<id>.txt`. Os traces correspondentes estão em `output/verification/ET2-final-mutant-<id>-trace.txt`, acompanhados pelos schedules com o mesmo prefixo.

Os mutants R1 e R2 são de logs/runtime e dependem do PObserve; permanecem planejados para D3.

## Interpretação

Todos os mutants de design time incluídos em D2 foram detectados pelo monitor correspondente. O resultado demonstra a capacidade de revelar as violações modeladas nesta campanha, dentro dos seeds e limites registrados. Ele não constitui uma prova para execuções, logs ou hipóteses que não foram exercitados.
