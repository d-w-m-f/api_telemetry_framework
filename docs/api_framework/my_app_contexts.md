
## 3. Mapa de contextos

| Nome | Descrição | Tipo | Onde vive |
|---|---|---|---|
| referencia | Domínio de Referência | Shared Kernel | `api/`, `db/schema/`, `db/queries/`, `specs/reference-domain/` |
| backend-database | Banco de Dados & Dados | Suporte | `db/`, `src/lab/data/` |
| stress | Geração de Carga | Suporte | `bench/scenarios/`, `bench/profiles/`, `src/lab/load/` |
| telemetry | Telemetria | Suporte (e objeto de estudo) | `observability/`, `src/lab/telemetry/` |
| experimentation | **Experimentação** | **Núcleo** | `src/lab/experiment/`, `bench/matrix.yaml` |
| analytics | **Resultados & Análise** | **Núcleo** | `src/lab/analysis/`, `results/` |
| view | Interface de apresentação | Apresentação | `src/portal/` |

### 2.1 Domínio de Referência (Shared Kernel)

O que toda API implementa: `Produto`, `Categoria`, `Cliente`, `Pedido`,
`ItemDePedido`, `Estoque`, `ChaveDeIdempotência`.

Invariantes de negócio — normativos, verificados pela suíte de conformidade,
não pela boa vontade da implementação:

- Estoque nunca fica negativo.
- Duas requisições com a mesma `ChaveDeIdempotência` retornam o mesmo `Pedido`,
  e o efeito colateral ocorre uma única vez.
- O total de um `Pedido` é exatamente a soma de seus itens.
- Toda resposta de erro é `application/problem+json` (RFC 9457).

**Este contexto é fechado para modelagem.** Mudança aqui invalida todo resultado
anterior, porque muda o sujeito medido. Por isso é versionado (`contract_version`)
e a versão vigente é gravada em cada execução. Evoluir o contrato é uma decisão
de projeto, registrada em `docs/adr/`, nunca um efeito colateral de implementar
uma linguagem nova.

**Aditivo não é compatível.** Acrescentar um campo é retrocompatível para um
*consumidor de API* e incompatível para um *benchmark*: o payload cresce, o custo
de serialização muda, os bytes no socket mudam, o p99 muda. As duas noções de
compatibilidade não são a mesma, e confundi-las é como se produz folclore. Toda
tabela comparativa é de uma única `contract_version` — não existe convergência
gradual em que resultados de duas versões coexistam.

### 2.3 Backend de Dados

Linguagem ubíqua: `Engine`, `IntençãoDeQuery`, `Realização`, `Dataset`,
`Snapshot`, `Migração`, `Pool`.

O fixo não é o SQL — é a **`IntençãoDeQuery`**: um nome, uma semântica,
parâmetros tipados, shape de retorno e o plano de acesso esperado. O SQL é a
*realização* daquela intenção em um `Engine` específico
(`db/queries/postgres/list_products_by_category.sql`).

Invariantes:

- Toda `IntençãoDeQuery` ativa tem realização em todo `Engine` ativo. Um Engine
  sem cobertura total não é elegível para a tabela comparativa.
- Dentro de um mesmo Engine, a realização é **byte a byte idêntica** para todas
  as linguagens. É aqui que a regra de justiça do PLAN §2.2 continua valendo.
- Um `Snapshot` é imutável e carrega o hash do `Dataset` que o gerou.

Para fora, este contexto publica um **DataPort**: um protocolo de métodos
nomeados pelas intenções, sem SQL na assinatura. Cada linguagem realiza esse
port via factory por engine (ver `specs/api/data-port.md`).

### 2.4 Geração de Carga

Linguagem ubíqua: `Cenário`, `PerfilDeCarga`, `Degrau`, `TaxaDeChegada`,
`Calibração`, `ObservaçãoDeCliente`.

O contexto é dono do **estímulo**. Invariante: modelo aberto sempre
(taxa de chegada constante). Modelo fechado é proibido — ele se auto-limita
quando o servidor engasga e produz omissão coordenada.

A aritmética que torna isso concreto: 100 VUs contra um servidor que leva 3s por
resposta emitem **33 req/s**, não os 800 que você pretendia testar. O relatório
mostra p99 de 3s — número verdadeiro sobre um sistema que jamais sofreu a carga
declarada. Uma população real chegando a 800 req/s acumula fila a 767 req/s: em
60 segundos são ~46.000 requisições enfileiradas, e o p99 real é de minutos ou
conexão recusada. O aparelho de medição conspira com o sistema medido para
omitir justamente as requisições que teriam sido lentas.

No modelo aberto a latência é medida desde o instante **pretendido** de envio,
não desde o instante em que o gerador conseguiu enviar. A fila entra na conta.

Publica `ObservaçãoDeCliente` para Resultados. Não interpreta o que publica.

### 2.5 Telemetria

Linguagem ubíqua: `Sinal`, `Instrumentação`, `NívelDeTelemetria`, `Sampling`,
`Exporter`, `ObservaçãoDeServidor`.

O contexto é dono da **observação**. É separado de Geração de Carga por duas
razões: são lados opostos do experimento (estímulo vs. observação) e variam
de forma independente — trocar Prometheus não toca em k6.

Papel duplo: telemetria é ferramenta *e* objeto de estudo. `NívelDeTelemetria`
(`off | metrics | traces@sampling`) é um knob do `Experimento`, o que permite
medir quanto custa enxergar. Carga nunca é sujeito medido — ela é o `Cenário`.
Essa assimetria é o motivo de um aparecer no agregado `Experimento` e o outro não.

O teste que decide a fronteira: trocar Prometheus por VictoriaMetrics toca apenas
Telemetria; trocar k6 por Vegeta toca apenas Geração de Carga. Contexto se
desenha por linguagem ubíqua e taxa de mudança, nunca por onde o código roda —
"externo vs. interno ao processo" é fato de implantação e não prevê nada.

### 2.6 Experimentação — núcleo

Linguagem ubíqua: `Experimento`, `Setup`, `Run`, `Réplica`, `Precondição`,
`Calibração`, `Warmup`, `Validade`, `Orçamento`, `ImpressãoDoHost`.

Agregado raiz: **`Experimento`** — o "setup completo" do produto web. Contém
`ImplementaçãoId`, `Cenário`, `PerfilDeCarga`, `PerfilDeDataset`,
`NívelDeTelemetria`, `Orçamento`, `NúmeroDeRéplicas`, `contract_version`.

- Invariante: um `Experimento` é **imutável**. Alterar qualquer knob produz um
  Experimento novo, com nova identidade (hash do setup). Sem isso, comparação
  não tem significado.

Entidade `Run`: uma execução de um `Experimento`. Máquina de estados:
`pendente → provisionando → aquecendo → calibrando → medindo → coletado → válido | inválido`.

- Invariante de validade — um `Run` só se torna `válido` se **todas** valerem:
  calibração contra `/noop` passou (throughput medido < 70% do teto do harness);
  precondições do host satisfeitas (RAM livre, governor em `performance`);
  warmup concluído e excluído da janela de medição; zero erros de infraestrutura.
- Invariante: a `ImpressãoDoHost` (kernel, frequência, temperatura, uptime) é
  gravada no `Run` e é imutável.

Entidade `ConjuntoDeRéplicas`: os N runs de um mesmo `Experimento`.

- Invariante: comparação entre Experimentos exige ≥5 runs **válidos** de cada lado.

Este é o contexto mais importante do repositório. As regras acima são código com
guarda e teste, nunca convenção em markdown.

### 2.7 Resultados & Análise — núcleo

Linguagem ubíqua: `Observação`, `SérieTemporal`, `Percentil`,
`ThroughputSustentávelMáximo`, `Joelhada`, `MétricaDerivada`, `Comparação`,
`Achado`.

`Observação` é imutável e carrega sua fonte (`cliente | servidor | banco | host`).

Invariantes:

- Nenhuma métrica derivada é calculada sobre `Run` inválido.
- Um `Resultado` nunca é editado. Reanálise cria uma nova `Análise` sobre as
  **mesmas** observações, versionada.
- **"Média" é palavra proibida neste contexto.** Distribuição de latência se
  reporta por percentis (p50/p95/p99/p99.9/max). Um campo `avg` em qualquer
  struct daqui é um bug.
- **Percentis não se promediam.** Não existe "p99 médio de 5 réplicas": a média
  de cinco p99 é uma grandeza sem interpretação estatística. Um percentil
  combinado exige fundir os histogramas, nunca os sumários. Agregação entre
  réplicas é mediana e IQR.
- **Latência sem carga declarada não é número.** p99 a 100 req/s e p99 a 5.000
  req/s são grandezas diferentes do mesmo sujeito. Qualquer latência exibida
  fora do par (cenário, taxa de chegada) é ruído. O único número autocontido é
  o `MaxSustainableThroughput`, que carrega o SLO dentro de si.

### 2.8 Portal

Casca sobre Experimentação e Resultados: montar um `Setup`, disparar, salvar,
listar, comparar. Não possui modelo próprio — se o Portal precisa de um conceito
que não existe em Experimentação ou Resultados, o conceito está faltando lá.

---

## 3. Direção das dependências

```
              Domínio de Referência  (shared kernel, versionado)
                          ▲
        ┌─────────────────┼──────────────────┬─────────────────┐
   Implementações   Backend de Dados   Geração de Carga    Conformidade
        ▲                 ▲                  ▲
        └─────────────────┴─────┬────────────┘
                                │  consome e orquestra
                        Experimentação  (núcleo)
                                │  publica RunManifest + Observações
                                ▼
                     Resultados & Análise  (núcleo)
                                ▼
                              Portal
```

Regras duras, verificáveis:

1. **Nada flui de volta.** Uma Implementação jamais importa código do laboratório.
2. **O laboratório jamais importa código de uma Implementação.** A única
   comunicação é HTTP mais o Harness Contract (Dockerfile, env vars, `/readyz`,
   `/metrics`). É isso que faz adicionar Rust ou Elixir custar um diretório.
3. Geração de Carga e Telemetria não se conhecem. Encontram-se apenas em
   Resultados, correlacionadas por `trace_id` e janela temporal.
4. Fábrica de Implementações não conhece Experimentação. Ela produz artefatos
   conformes; quem os agenda é outro contexto.

---

## 4. Vocabulário

Specs e documentação em português. Código e identificadores em inglês. A
tradução é 1:1 e fechada — termo que não estiver na tabela não deve aparecer em
nome de tipo, módulo, campo ou métrica.

| Português | Código |
|---|---|
| Experimento / Setup | `Experiment` |
| Execução | `Run` |
| Réplica / Conjunto de réplicas | `Replica` / `RunSet` |
| Implementação (sujeito) | `Implementation` |
| Estratégia | `Strategy` |
| Intenção de query | `QueryIntent` |
| Realização | `Realization` |
| Observação | `Observation` |
| Cenário | `Scenario` |
| Degrau | `Step` |
| Taxa de chegada | `ArrivalRate` |
| Calibração | `Calibration` |
| Aquecimento | `Warmup` |
| Orçamento | `Budget` |
| Impressão do host | `HostFingerprint` |
| Conformidade | `Conformance` |
| Nível de telemetria | `TelemetryLevel` |
| Joelhada | `Knee` |
| Throughput sustentável máximo | `MaxSustainableThroughput` (`MST`) |
| Achado | `Finding` |

Sinônimo é dívida. "Teste", "benchmark", "profile" e "medição" não são
intercambiáveis: um `Run` é uma execução, um `Experiment` é uma configuração, um
`Finding` é uma conclusão.

---

## 5. Regras para agentes construtores

A fábrica só funciona se o agente carregar pouca spec e a spec certa.

**Seleção.** Para construir `<linguagem>/<framework>/<estratégia>`, o agente
carrega exatamente:

```
specs/DDD/general.md                       (esta)
specs/api/contract.md                      o que a API expõe
specs/api/harness-contract.md              como o laboratório fala com ela
specs/api/data-port.md                     como ela fala com o banco
specs/api/telemetry.md                     o que instrumentar
specs/languages/<linguagem>.md             idiomas e estrutura de pacote
specs/frameworks/<linguagem>/<framework>.md
specs/strategies/<estratégia>.md           a arquitetura interna sob teste
```

Nada além disso. Ler o código de outra implementação para "se inspirar" é
proibido: é assim que viés de familiaridade contamina a comparação.

**Precedência.** Contrato > estratégia > framework > linguagem. Uma spec mais
específica pode detalhar a mais geral, jamais contradizê-la. Contradição
detectada é motivo de parada.

**Improviso.** O agente decide livremente o que **não afeta a medição** (nomes
internos, organização de arquivo, estilo) e registra a decisão no `impl.yaml`.
O agente **para e pergunta** quando a decisão afeta a medição e a spec não a
cobre — escolha de driver, implementação e tamanho de pool, política de timeout,
uso de cache, número de workers. Nesses casos, improvisar produz um número que
ninguém pode defender.

**Registrar não legitima.** O `impl.yaml` documenta *que* uma escolha foi feita,
não que ela era permitida. Registro serve à decisão livre; decisão que afeta
medição não se torna aceitável por estar anotada. A parada não é burocracia — ela
produz a spec faltante, e a spec torna determinísticas todas as implementações
seguintes. Um agente que escolhe o pool sozinho faz `java/spring/minimal` sair com
Hikari e `java/quarkus/minimal` com Agroal: a comparação entre frameworks passa a
estar confundida com a comparação entre pools, sem como separar depois.

**Aceite.** Uma implementação está pronta quando: a suíte de conformidade passa,
o Harness Contract é honrado, `impl.yaml` está completo e nenhuma decisão de
medição foi tomada fora de spec.