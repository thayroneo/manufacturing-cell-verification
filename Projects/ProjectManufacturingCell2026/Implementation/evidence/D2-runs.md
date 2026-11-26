# D2 — Registro de execuções

Diretório de execução: `manufacturing-cell-verification/Projects/ProjectManufacturingCell2026/Implementation`  
Data: 26/11/2026  
P: 3.1.0.0 · .NET SDK 8.0.427 · Java 17.0.21 · Gradle 8.10.2 · Python 3.12.10

| Experimento | Comando | Seed | Schedules | Resultado | Evidência |
|---|---|---:|---:|---|---|
| Compilação | `p compile` | — | — | 0 warnings, 0 errors | saída da compilação |
| E4 pré-correção / S4 | `p check -tc tcCellTwoTechniciansPreFix -s 100000` | 877628034 | 6 até a falha | 1 bug | `ET2-final-S4-trace.txt`, `ET2-final-S4-summary.txt` |
| E4 corrigido | `p check -tc tcCellTwoTechniciansFixed -s 100000` | 3106042342 | 100000 | 0 bugs; 464 timelines | `ET2-final-fixed-100000-summary.txt`, `ET2-final-fixed-100000-coverage.txt` |
| Mutant S1 | `p check -tc tcMutantS1 -s 1000` | 3271887019 | 1 | 1 bug | `ET2-final-mutant-S1-trace.txt` |
| Mutant S2 | `p check -tc tcMutantS2 -s 1000` | 3662861277 | 1 | 1 bug | `ET2-final-mutant-S2-trace.txt` |
| Mutant S3 | `p check -tc tcMutantS3 -s 1000` | 2539613659 | 1 | 1 bug | `ET2-final-mutant-S3-trace.txt` |
| Mutant L1 | `p check -tc tcMutantL1 -s 1000` | 3953499931 | 1 | 1 bug | `ET2-final-mutant-L1-trace.txt` |
| Mutant L2 | `p check -tc tcMutantL2 -s 1000` | 1266211740 | 1 | 1 bug | `ET2-final-mutant-L2-trace.txt` |
| Mutant L3 | `p check -tc tcMutantL3 -s 1000` | 3079806130 | 1 | 1 bug | `ET2-final-mutant-L3-trace.txt` |
| Mutant R3 | `p check -tc tcMutantR3 -s 1000` | 1742197821 | 1 | 1 bug | `ET2-final-mutant-R3-trace.txt` |

R1/R2 não foram executados neste registro porque são mutants de runtime/PObserve, planejados para D3.

| Mutant S4 | p check -tc tcMutantS4 -s 1000 | 11558498 | 8 | 1 bug | ET2-final-mutant-S4-trace.txt |
