# D3 — Guia de execução e entrega

O D3 verifica os eventos registrados com os monitores Java gerados pelo PObserve. O corpus desta entrega é **sintético**. Não representa operação de uma célula física. D1 é de Thayrone; D2 é de Micael; esta entrega corresponde ao D3.

## Entrada rápida neste computador

A partir de `C:\Users\55839\Desktop\Manufacturing Cell`, execute:

```powershell
powershell -ExecutionPolicy Bypass -File .\EXECUTAR_D3.ps1
```

O launcher local configura o ambiente desta execução e usa as ferramentas instaladas no disco D:. O código e a evidência ficam nesta cópia do repositório. Para outra máquina, siga as instruções portáveis abaixo.

## Reprodução em outra máquina

Requisitos: Python 3.10+, .NET SDK 8, P 3.1.0, JDK 17 e o Gradle wrapper 8.10.2 já versionado. Todos os comandos abaixo partem de `Projects/ProjectManufacturingCell2026`.

Instale a ferramenta P conforme o guia original e compile o CLI oficial do PObserve no commit `260da92`, como descrito em `ManufacturingCell/INSTRUCTIONS.md`, seção 3.2. O artefato é `PObserve-1.0.0.jar`. Para produzir apenas o CLI, a task Gradle `shadowJar` é suficiente.

```powershell
python tools/d3_run.py --cli "CAMINHO/PObserve-1.0.0.jar"
```

Em Linux/macOS, use `python3` se necessário e torne `ManufacturingCell/pobserve/gradlew` executável. O runner escolhe o wrapper da plataforma. A conexão é usada para obter dependências; o processamento dos logs ocorre localmente.

A campanha gera o corpus, executa testes Python, compila o modelo original e o projeto D2, executa `build uberjar` com JUnit, verifica cada par log/monitor usando o CLI real e roda uma regressão curta do modelo D2 corrigido (1.000 schedules, seed 42). Um erro de ferramenta ou um resultado diferente da previsão faz o runner terminar com erro.

## Execução por partes

```powershell
python tools/d3_generate.py
python -m unittest discover -s tools -p test_d3.py -v
```

```powershell
cd ManufacturingCell/pobserve
.\gradlew.bat --no-daemon build uberjar
cd ../..
python tools/d3_verify.py --cli "CAMINHO/PObserve-1.0.0.jar"
```

Depois da campanha completa, o relatório HTML pode ser formatado novamente com
`python tools/d3_report.py`. Para exportar também PDF com um navegador Chromium
local, acrescente `--browser "CAMINHO/msedge.exe"` (ou o executável Chromium).
O launcher deste computador executa essa exportação automaticamente.

Para visualizar um cenário sem Java, o simulador original foi estendido:

```powershell
python tools/simulate_logs.py --scenario cell --policy twophase --technicians 2 --lockout-policy fixed --seed 0 --ticks 60 --out two_fixed.log --check
python tools/simulate_logs.py --scenario cell --policy twophase --technicians 2 --lockout-policy prefix --seed 0 --ticks 60 --out two_prefix.log --check
```

`--check` continua sendo uma prévia Python. Seus resultados não substituem a execução de PObserve. O gerador principal preserva os exemplos originais byte a byte e cria cópias em `logs/`.

## Escolhas analíticas

- **FACT / LOCALLY_EXECUTED_SYNTHETIC:** a calibração usa 500 seeds para um técnico e 500 para dois técnicos, com 60 ticks por execução. Os intervalos são medidos de `ADAPT_START` a `COMMIT` ou `ADAPT_ABORT`, não apenas durante o drain.
- **ANALYTICAL_DECISION:** usar o máximo observado como limite do corpus. O evento `RUNTIME_CONFIG, MaxAdaptTicks=8` torna a escolha explícita. Logs antigos conservam o limite padrão de cinco ticks. A configuração permanece em vigor após cada commit.
- **FACT:** S4 é compilado a partir do monitor criado no D2 (`Implementation/PSpec/TeamSpecs.p`), sem reescrevê-lo.
- **ANALYTICAL_DECISION:** correlacionar os commits e aborts de R2 com a versão pendente. Um abort de outra versão não encerra a obrigação monitorada.
- **INFERENCE:** o sucesso dos testes sustenta conformidade desse corpus com os monitores incluídos; não demonstra segurança física nem ausência de bugs em todas as execuções.

## Falha do sistema versus defeito no log

Os casos `system_sanction_suppressed` e `system_commit_delayed` alteram o comportamento da simulação. No primeiro, a organização não aplica a sanção; no segundo, o commit efetivo de fechamento é adiado. O logger registra os fatos que ocorreram.

Os casos `log_missing_leave`, `log_deleted_sanction`, `log_duplicate_commit` e `log_duplicate_outcome` alteram a representação de uma execução correta depois que ela ocorreu. O log original é preservado. O comportamento real continua sendo o da origem, embora os monitores possam reportar uma violação aparente.

Por isso, R1 pode reportar obrigação vencida tanto para uma sanção suprimida quanto para uma linha SANCTION apagada. Sem informação sobre a geração do log, os eventos observáveis não estabelecem qual foi a causa. `cases.json` registra a origem e a intervenção de cada caso.

O runner distingue exit 0 (sucesso) de exit 2 acompanhado de `PObserve Spec Violation::` (violação). Erros de configuração, parser, ordem ou execução recebem `TOOL_ERROR`; não são contados como detecção de propriedade.

A revisão local reforçou essa distinção: as métricas precisam confirmar
eventos lidos, uma partição processada e ausência de erros de parser, ordem
ou execução, mesmo se o CLI também reportar uma assertiva. Para aprovação,
também são exigidos eventos e chaves efetivamente verificados. Uma violação
pode ocorrer no primeiro evento, sem que a chave seja contabilizada como
verificada com sucesso. O runner exige a
quantidade completa de schedules solicitada e lê a quantidade real de testes
Python. A calibração contém 28 adaptações ainda abertas ao fim dos 60 ticks;
essas observações não são tratadas como adaptações concluídas.

## O que entregar

- `D3_RELATORIO.md` e `D3_RELATORIO.html`: relatório dos resultados efetivamente executados.
- `ManufacturingCell/D3_PREMISSAS.md` (a partir da raiz do projeto): análise das dez premissas da seção 7.7, incorporada automaticamente ao relatório. Cada premissa é discutida quanto à validade interna, de construto e externa.
- `cases.json`, `logs/`: previsões, proveniência, contagem de eventos e SHA-256 de cada log.
- `calibration.json`: medições, histograma, seeds e adaptações pendentes no fim dos logs.
- `results.json`, `results.csv`, `results.md`: matriz de vereditos do CLI.
- `pobserve/`: console, métricas e replay de cada execução.
- `junit/`, `python_tests.txt`, `p_compile_*.txt`, `checker/`: saídas dos testes e compilação.
- `commands.json`, `versions.json`, `summary.json`: reprodução e estado verificável da entrega.

Antes de atualizar o GitHub, confira `summary.json` e `git diff`. As distribuições de ferramentas e caches são locais e não fazem parte da entrega. O histórico e as evidências D2 permanecem preservados.

## Limitações e questões abertas

O simulador com dois técnicos serializa pedidos e reserva holders antes da entrada. A instalação no guard é síncrona, enquanto o modelo P explora mensagens assíncronas. Não há prova de refinamento entre os dois. R1/R2 dependem dos ticks registrados e um prefixo finito pode terminar antes de revelar uma obrigação pendente. Os logs não contêm identidades dos técnicos; a verificação conta presenças por recurso.

**OPEN_QUESTION:** adequação do limite temporal e da instrumentação a uma implementação física. Nenhuma homologação de negócio ou de segurança física é atribuída automaticamente.
