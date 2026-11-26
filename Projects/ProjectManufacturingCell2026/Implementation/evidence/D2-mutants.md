# D2 - Mutants

## Objetivo

Esta campanha verifica se os monitores do modelo detectam violacoes introduzidas deliberadamente. Cada mutant foi executado no projeto `Implementation/ManufacturingCellTeam.pproj` com estrategia aleatoria e limite de 1.000 schedules.

## Resultado da campanha

| Mutant | Alteracao exercitada | Teste | Seed | Resultado |
|---|---|---|---:|---|
| S1 | entrada sem a condicao de seguranca | `tcMutantS1` | 3271887019 | 1 bug no primeiro schedule |
| S2 | remocao da protecao de entrada | `tcMutantS2` | 3662861277 | 1 bug no primeiro schedule |
| S3 | obrigacao de saida nao cumprida | `tcMutantS3` | 2539613659 | 1 bug no primeiro schedule |
| L1 | obrigacao normativa ausente | `tcMutantL1` | 3953499931 | 1 bug no primeiro schedule |
| L2 | adaptacao iniciada sem condicao valida | `tcMutantL2` | 1266211740 | 1 bug no primeiro schedule |
| L3 | adaptacao iniciada fora do protocolo | `tcMutantL3` | 3079806130 | 1 bug no primeiro schedule |
| R3 | `COMMIT` antes de `HUMAN_ENTER` | `tcMutantR3` | 1742197821 | 1 bug no primeiro schedule |

S4 e tratado como o cenario comportamental pre-correcao: dois tecnicos podem reabrir o recurso enquanto ainda ha uma pessoa dentro. Esse cenario foi reproduzido por `tcCellTwoTechniciansPreFix` em 6 schedules, com o trace `output/verification/ET2-final-S4-trace.txt`.

## Evidencias

Para cada mutant, a saida completa esta em `output/verification/ET2-final-tcMutant<id>.txt`. Os traces correspondentes estao em `output/verification/ET2-final-mutant-<id>-trace.txt`, acompanhados pelos schedules com o mesmo prefixo.

Os mutants R1 e R2 sao de logs/runtime e dependem do PObserve; permanecem planejados para D3.

## Interpretacao

Todos os mutants de design time incluidos em D2 foram detectados pelo monitor correspondente. O resultado demonstra a capacidade de revelar as violacoes modeladas nesta campanha, dentro dos seeds e limites registrados. Ele nao constitui uma prova para execucoes, logs ou hipoteses que nao foram exercitados.

| S4 | modelo pre-correcao permite reabrir com humano dentro | 	cMutantS4 | 11558498 | 1 bug em 8 schedules |
