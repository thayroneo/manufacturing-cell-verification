# D3 — Verificação de logs com PObserve

Estado: **D3_LOCALLY_VERIFIED_SYNTHETIC**.
Maturidade: **TECHNICALLY_VERIFIED**, restrita ao ambiente e corpus registrados.

## Resultados executados

- 16 cenários; 41/41 vereditos CLI coincidiram com a previsão.
- JUnit: 19 testes, 0 falhas, 0 erros.
- Python: 9 testes de consistência, reprodução dos exemplos e validação das evidências.
- Modelo base e implementação D2 compilados. Regressão D2: 1000 schedules, seed 42, zero bugs.
Os 41 vereditos incluem aprovações e violações intencionais previstas; não são 41 execuções sem violações.

## Calibração de R2

FACT: 500 seeds com um técnico e 500 com dois, 60 ticks por execução, 6680 adaptações concluídas.
FACT: 11 durações excederam cinco ticks; máximo observado: 8 ticks.
FACT: 28 adaptações ainda estavam abertas ao fim dos 60 ticks e não entram na distribuição de durações concluídas. Elas permanecem registradas em calibration.json.
ANALYTICAL_DECISION: B=8 para este corpus, configurado pelo evento RUNTIME_CONFIG. Sem configuração, o monitor conserva o padrão B=5.
A medição usa ADAPT_START até COMMIT/ADAPT_ABORT, incluindo o atraso do protocolo. Seed 64 excede cinco ticks; seed 299 atinge oito.

## Dois técnicos e S4

O corpus contém presença simultânea dos dois técnicos. A versão pré-correção reabre com uma pessoa dentro e S4 reporta a violação.
A versão corrigida mantém os holders desde o pedido até a saída, cobrindo autorizações pendentes. Os sete monitores aceitam o log corrigido.

## Falha do sistema e defeito do log

SYSTEM_FAULT: a organização deixa de aplicar sanções; o logger registra fielmente os fatos. R1 detecta obrigação vencida.
SYSTEM_FAULT: o controlador adia o commit efetivo, mantendo o bloqueio. R2 detecta atraso.
LOG_DEFECT: removemos LEAVE ou SANCTION, ou duplicamos COMMIT/outcome depois da simulação correta. O comportamento real continua sendo o do log original.
R1 pode produzir o mesmo alarme para sanção realmente suprimida e registro de sanção apagado. Esse alarme sozinho não identifica a causa; a proveniência das mutações está em cases.json.

## Evidências e reprodução

Comandos e versões: commands.json e versions.json. Corpus/hashes: cases.json e logs/. Calibração: calibration.json.
Saídas reais do CLI, métricas e replay: pobserve/. Resultados tabulares: results.md, results.csv e results.json. JUnit: junit/.
Consulte D3_GUIA.md para repetir a campanha.

## Limitações

- Os logs são sintéticos; nenhuma célula física ou implantação real foi avaliada.
- O máximo da calibração é empírico e não limita todas as execuções futuras.
- Logs finitos não demonstram vivacidade ilimitada; adaptações abertas ao final são registradas.
- A instalação no controlador do simulador de dois técnicos é síncrona; não há prova de refinamento em relação ao modelo P.

## Premissas e ameaças à validade

Este anexo completa a análise das dez premissas de SPECIFICATION.md, seção 7.7. A tabela distingue o escopo do modelo do que foi efetivamente observado no D3. As três subseções seguintes discutem cada premissa quanto à validade interna, de construto e externa.

FACT / TECHNICALLY_VERIFIED: as evidências sustentam os resultados do corpus sintético registrado em summary.json e results.json. INFERENCE / TECHNICAL_REVIEWED_SYNTHETIC: a interpretação abaixo delimita o alcance desses resultados. Uma premissa não passa a estar validada no mundo real porque um teste sintético foi aprovado.

| Premissa e situação no D3 | Contraparte em uma célula real | Aproximação | Propriedades afetadas |
| --- | --- | --- | --- |
| P01 — Agentes usam pedido, autorização, saída e relatório. Os logs base seguem esse protocolo; não há ensaio de movimento robótico sem autorização. | Um robô pode se mover sem permissão após uma falha de software ou hardware. | Subaproximação. | S1, S2; um resultado seguro não cobre movimento fora do protocolo. |
| P02 — O modelo pressupõe mensagens sem perda ou duplicação, ordenadas por par remetente/destinatário. No simulador com dois técnicos, a instalação no guard é síncrona. | A rede pode perder, atrasar, duplicar e reordenar mensagens entre fontes. | Subaproximação; a equivalência entre simulador e modelo assíncrono não foi demonstrada. | S2, L2, R2; também S4 quando depende da instalação da regulação. |
| P03 — A saída é um evento instantâneo; a geometria e a trajetória do movimento não são representadas. | Um braço precisa de espaço e tempo para sair da zona. | Abstração da movimentação para ocupação. | S1; o instante físico da saída não foi validado. |
| P04 — Escopo da especificação: um guard, um recurso de capacidade 1 e dois agentes. O D3 acrescenta logs com um ou dois técnicos. | Há células com várias zonas, capacidades e agentes. | Restrição de escopo. | Todas; os resultados se referem às configurações registradas. |
| P05 — Prazos e durações são contados em ticks lógicos. R2 usa o intervalo completo entre início e commit ou abort da mesma versão. | O tempo de relógio tem jitter e atrasos de execução. | Abstração temporal; B é uma escolha empírica do corpus. | L1, R1, R2. |
| P06 — O técnico aguarda o commit nos cenários regulares. Um caso negativo registra entrada sem bloqueio e exercita R3. | Uma pessoa pode contornar o procedimento. | Subaproximação nos cenários regulares; um desvio específico é exercitado. | R3; S1 também depende da entrada efetivamente registrada. |
| P07 — A presença humana é registrada sem erro nos logs base; não há modelo de falha do sensor. | Cortinas de luz e sensores podem falhar ou ser desativados. | Subaproximação. | S1, R3, S4; os monitores dependem da presença observada. |
| P08 — O modelo base é limitado por maxTicks, denials e tick final. A calibração D3 usa logs de 60 ticks e registra adaptações abertas no fim. | A operação é contínua e pode terminar um recorte com trabalho pendente. | Exploração e observação limitadas. | L1, L2, L3; R1 e R2 precisam de ticks posteriores para revelar atrasos. |
| P09 — As escolhas não determinísticas do modelo P representam decisões dentro do protocolo. O simulador Python usa seeds e escolhas pseudoaleatórias. | Agentes de fornecedores ou com aprendizagem podem agir de maneiras não representadas. | Sobreaproximação pretendida apenas das decisões internas ao protocolo P; amostragem finita no simulador. | Propriedades de sanção e cobertura comportamental; não há equivalência provada entre as duas escolhas. |
| P10 — Timestamps dos logs D3 são estritamente crescentes por site; Site identifica a partição. Não foi injetado desvio entre relógios de fontes distintas. | Relógios de PLC, organização e sensores podem apresentar skew. | A correspondência entre timestamp e causalidade depende da sincronização. | S1 e R3 em runtime; ordenação de commits também afeta a interpretação de S2 e S4. |

### Validade interna

- **P01.** Erros na geração de ENTER/LEAVE poderiam tornar a ocupação artificialmente segura. A reprodução dos exemplos originais, seus hashes e os casos negativos S1/S2 reduzem esse risco; não conferem movimentos físicos.
- **P02.** A instalação síncrona do simulador pode omitir interleavings presentes no P assíncrono. A regressão D2 e o teste S4 pré-correção são evidências separadas; nenhuma prova que os dois modelos têm o mesmo conjunto de comportamentos. Duplicar COMMIT no arquivo exercita um defeito de log, não uma duplicação de mensagem da rede.
- **P03.** A atualização incorreta da ocupação no simulador ou parser mudaria o veredito. O caso de LEAVE removido mostra o efeito dessa dependência; o log original preservado fornece a referência da simulação, sem confirmar o instante real de saída.
- **P04.** CONFIG ou Res incorretos poderiam alterar capacidades e misturar recursos. Os testes reproduzem o recurso configurado e verificam presença simultânea de dois técnicos; não foram executados testes de partições com múltiplos sites nem de várias zonas.
- **P05.** Erros na contagem de TICK ou na associação de versões afetariam as durações. A medição usa ADAPT_START até COMMIT/ADAPT_ABORT, incluindo o protocolo; os casos seeds 64/299 e abort de versão incorreta exercitam essas fronteiras. O máximo só considera adaptações concluídas.
- **P06.** R3 poderia passar sem receber HUMAN_ENTER. A contagem de eventos, o cenário regular e o caso human_bypasses_lockout exercitam o monitor, que rejeita a entrada sem commit. Isso reduz o risco de aprovação vazia para esse caso.
- **P07.** O parser pode interpretar corretamente um dado incorreto emitido pelo sensor. Os testes de parser e as métricas sem erros conferem a transformação dos registros; não verificam a origem física dos sinais.
- **P08.** Um prefixo vazio ou uma execução parcial poderia aparentar sucesso. O verificador exige eventos e métricas válidas, e o runner confirma a quantidade explorada de schedules. As adaptações abertas ao fim da calibração são registradas separadamente, sem serem tratadas como concluídas.
- **P09.** Um gerador e um verificador com o mesmo erro poderiam concordar. Os vereditos usados no relatório vêm dos monitores P compilados para Java e do CLI real; a prévia Python não é usada como comprovação. Hashes e seeds permitem repetir os dados, mas não garantem independência de toda a implementação.
- **P10.** Reordenação e timestamps empatados poderiam alterar os estados observados. Os testes verificam crescimento estrito dos timestamps do corpus e o classificador rejeita erros de ordenação do CLI. Isso não mede sincronização entre relógios reais.

### Validade de construto

- **P01.** S1 e S2 expressam ocupação e admissão sob a regulação registrada. A norma física de segurança é mais ampla que a conformidade desse protocolo; não se conclui que qualquer movimento do robô esteja seguro.
- **P02.** A ordem dos registros não representa automaticamente a ordem de entrega de todas as mensagens. O atraso real do commit e a duplicação de sua linha têm causas distintas, mesmo quando um monitor acusa violação; essa distinção é mantida em cases.json.
- **P03.** LEAVE significa que o agente deixou a zona no modelo. Não significa apenas que começou a sair. Se uma implementação física registrar a intenção de sair em vez da saída concluída, o evento deixará de corresponder ao construto de ocupação usado por S1.
- **P04.** Capacidade 1 limita a ocupação dos agentes modelados; não é uma afirmação sobre toda configuração industrial nem uma proibição de coexistência dos dois técnicos. S4 exige que a zona permaneça fechada enquanto houver presença humana registrada.
- **P05.** R1 é resposta ao prazo da obrigação, com a tolerância definida pelo monitor. R2 é duração da adaptação inteira, não apenas do drain. B=8 é calibrado empiricamente; o suporte a abort correlacionado encerra a adaptação monitorada, sem afirmar que um commit ocorreu nem alterar a interpretação de L2.
- **P06.** R3 verifica a sequência normativa de bloqueio antes da entrada, enquanto S1 verifica coexistência perigosa. Detectar um bypass em R3 não demonstra a existência de uma barreira física capaz de impedir a pessoa de entrar.
- **P07.** HUMAN_ENTER/HUMAN_LEAVE representam a presença detectada. Ausência de registro não significa ausência de pessoa. Um defeito de log ou sensor pode produzir falso alarme ou ocultar uma violação; PObserve sozinho não identifica a causa.
- **P08.** PASS em um log finito significa ausência de violação detectada naquele prefixo. Não demonstra vivacidade ilimitada nem a resolução de tudo que ficou pendente. Os testes negativos e a rejeição de entrada vazia reduzem vacuidade, sem eliminarem o limite temporal da observação.
- **P09.** Uma sanção é uma ação da organização, distinta de sua linha no log. A supressão da ação e a exclusão posterior da linha foram separadas para não interpretar todo alarme R1 como falha efetiva do sistema.
- **P10.** Um timestamp crescente é ordem documental, não prova de causalidade entre fontes. Ver ajuda a identificar versões, mas S2 continua sendo uma propriedade de fechamento do recurso; não foi redefinida como igualdade estrita entre versão de admissão e versão atual.

### Validade externa

- **P01.** Nenhum ensaio cobriu movimento robótico sem grant ou falha de atuador. A extrapolação para esses comportamentos permanece OPEN_QUESTION; os resultados abrangem as ações representadas no corpus.
- **P02.** Não foram avaliadas perdas, duplicações e reordenações de mensagens em rede industrial. Um resultado do simulador síncrono não é transferido para uma implementação distribuída sem analisar seus canais e interleavings.
- **P03.** Distância de parada, velocidade e tempo de retirada não foram medidos. Os resultados sobre ocupação abstrata não constituem validação de segurança da movimentação física.
- **P04.** Não se generaliza a aprovação para mais agentes, zonas, guards ou capacidades. Outra configuração requer seus próprios cenários, instrumentação e resultados de verificação.
- **P05.** Oito ticks não são oito segundos físicos garantidos. O período dos ticks, jitter e tempos de reação precisam ser definidos e medidos na implantação; o máximo amostral não limita execuções futuras.
- **P06.** O bypass sintético cobre uma sequência específica, não todos os comportamentos humanos possíveis. Adesão ao procedimento e eficácia de intertravamentos físicos permanecem fora da validação D3.
- **P07.** Não houve avaliação de cobertura, diagnóstico ou confiabilidade de sensores. Um veredito limpo não permite concluir que uma pessoa não detectada estaria protegida.
- **P08.** Seeds, schedules e logs têm horizontes finitos. As adaptações ainda abertas podem terminar ou violar o limite depois do recorte; nenhuma dessas alternativas é inferida. Operação prolongada e reinícios exigem observação própria e segmentação adequada dos logs.
- **P09.** Os seeds não representam uma distribuição conhecida do comportamento de agentes reais. Não se estimam frequências de falha, probabilidades de segurança ou comportamento de agentes com aprendizagem a partir dessa amostra.
- **P10.** Não foi medida a acurácia de relógios NTP/PTP nem executado teste com fontes físicas independentes. Skew pode criar ou ocultar alarmes; a adequação temporal da instrumentação real permanece OPEN_QUESTION.

### Decisões e questões abertas

ANALYTICAL_DECISION / TECHNICAL_REVIEWED_SYNTHETIC: manter separados resultados do checker, medições do simulador e vereditos PObserve. Os sete monitores de runtime cobrem S1–S4 e R1–R3; L1–L3 pertencem ao checker e não são declarados provados pelos logs. A campanha de calibração mede durações e não equivale à verificação integral de suas mil execuções por PObserve.

HYPOTHESIS / NOT_VALIDATED: uma instrumentação que preserve os significados dos eventos, a completude e a ordem causal poderá permitir a aplicação dos mesmos monitores a uma célula real. Essa hipótese não foi testada no D3. A instrumentação JaCaMo é uma extensão opcional da especificação, não uma execução realizada nesta entrega.

OPEN_QUESTION / NOT_VALIDATED: equivalência entre simulador e modelo assíncrono, seleção de B para operação real, falhas de sensores e rede, relógios de múltiplas fontes e generalização para outras escalas. Nenhuma dessas questões é convertida em conclusão de segurança física.
