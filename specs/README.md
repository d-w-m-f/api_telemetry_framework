# Specs — taxonomia e regras de escrita

Este diretório é o artefato de engenharia central do repositório. O código das
APIs sob teste é **saída**: gerado por agentes que leem estas specs. Se uma
implementação está errada, a spec está errada primeiro.

Princípio único:

> Todo aspecto **fixo** é contrato e vive uma única vez.
> Todo aspecto **variante** é uma spec e é selecionável por nome.

Um aspecto que não é nem contrato nem spec é improviso — e improviso que afeta
medição produz número indefensável. Ver `specs/DDD/general.md §5`.

---

## Anatomia obrigatória de uma spec

Toda spec abre com frontmatter e contém as cinco seções abaixo, nesta ordem.
Agente que encontrar spec fora deste formato deve parar e reportar.

```yaml
---
id: strategies/join-unico
versao: 1
aplica_se_a: [go, typescript, java, python]   # ou "todas"
depende_de: [api/contract, api/data-port]
afeta_medicao: true
---
```

| Seção | Conteúdo |
|---|---|
| **Escopo** | O que esta spec decide, em uma frase. O que ela explicitamente não decide. |
| **Fixo** | O que a implementação é obrigada a fazer. Verificável, não aspiracional. |
| **Livre** | O que o agente decide sozinho e registra em `impl.yaml`. |
| **Fronteiras** | Como interage com as outras specs carregadas; onde poderia conflitar. |
| **Aceite** | Como se verifica que foi cumprida. Preferencialmente um comando. |

`afeta_medicao: true` marca specs cujas decisões entram no resultado. Mudança em
qualquer uma delas **invalida runs anteriores** dos sujeitos afetados: bump de
`versao` e nova rodada. É o mecanismo que impede comparar maçãs com laranjas
seis meses depois.

---

## Taxonomia

```
specs/
  README.md                    esta — como specs são escritas e escolhidas
  DDD/
    general.md                 modelo estratégico; precede todas as outras
    contexts/<contexto>.md     modelo tático de um contexto do laboratório
  reference-domain/
    domain.md                  entidades, invariantes de negócio, regras de estoque e idempotência
    contract.md                endpoints, shapes, códigos, envelope de erro (aponta para api/openapi.yaml)
    query-intents.md           catálogo de IntençõesDeQuery: semântica, params, shape, plano esperado
  api/                         o que TODA implementação deve honrar
    harness-contract.md        Dockerfile, env vars, /healthz /readyz /metrics /noop, sinais, shutdown
    data-port.md               protocolo de acesso a dados + factory por engine
    telemetry.md               nomes de métricas, atributos, spans, níveis, o que NÃO instrumentar
    knobs.md                   knobs obrigatórios e sua semântica exata (pool, timeouts, workers)
  languages/<linguagem>.md     idiomas: como se faz port/interface, injeção, erro, layout de pacote
  frameworks/<linguagem>/<framework>.md
                               particularidades do framework; onde ele já resolve algo do harness
  strategies/<estrategia>.md   a arquitetura interna sob teste — o eixo variável principal
  engines/<engine>.md          particularidades de um backend de dados
```

**Regra de alocação.** Antes de escrever, responda: isto varia por linguagem, por
framework, por estratégia ou por engine? A resposta é o diretório. Se varia por
mais de um eixo, a spec está grande demais e deve ser dividida.

**Regra de tamanho.** Se uma spec passa de ~150 linhas, ela provavelmente
descreve dois aspectos. Agente com contexto entupido segue spec pior.

---

## Os eixos variantes

O que hoje varia, e onde cada variação é definida:

| Eixo | Valores iniciais | Spec |
|---|---|---|
| Linguagem | `go`, `typescript`, `java`, `python` | `languages/` |
| Framework | `http`, `gin` / `fastify` / `spring` / `fastapi` | `frameworks/` |
| Estratégia | `minimal`, `ddd-layered`, `hexagonal`, `n-mais-1`, `cache-aside`, `optimistic-stock` | `strategies/` |
| Engine | `postgres` (+ futuros) | `engines/` |
| Nível de telemetria | `off`, `metrics`, `traces@1%`, `traces@100%` | knob do Experimento |
| Perfil de dataset | `small`, `large` | Backend de Dados |
| Perfil de carga | `read_point`, `read_heavy`, `mixed`, `write_contended`, `slow_tail`, `burst` | Geração de Carga |
| Orçamento | cpus, memória, cpuset | Experimentação |

Os quatro primeiros compõem a identidade de um sujeito e materializam-se em
disco como `src/subjects/<linguagem>/<framework>/<estrategia>/`. Os quatro
últimos são knobs do `Experimento` e **não** geram código novo — mesma
implementação, execução diferente.

Essa separação é o que impede a explosão combinatória: só o que exige código
diferente vira diretório.

**Exemplo que decide a dúvida.** O sweep de pool do PLAN §7.1 varre pool de 1 a
64. Como knob, são 64 `Experimentos` sobre **uma** implementação. Como diretório,
seriam 64 diretórios por implementação — 256 no total, com código idêntico em
todos e diferença de uma variável de ambiente.

A objeção legítima — "o valor padrão vira privilégio escondido" — está resolvida
em outro lugar: a identidade do `Experimento` é o hash do **setup completo**, com
todo knob explícito. Não existe padrão implícito; um `Experimento` sem valor de
pool declarado não é um `Experimento` válido. A visibilidade mora no manifesto do
run, não na árvore de diretórios.

---

## Nomes de estratégia compõem, mas não se multiplicam

`minimal`, `ddd-layered` e `hexagonal` descrevem **arquitetura interna**;
`n-mais-1`, `cache-aside` e `optimistic-stock` descrevem **acesso a dados**. São
eixos conceitualmente ortogonais, mas o produto cartesiano não é construído: o
nome da estratégia é uma string única e completa, e só as combinações que
respondem a uma pergunta escrita viram diretório.

Na prática: `n-mais-1` significa arquitetura mínima com acesso N+1, porque a
pergunta que ela responde é "N+1 em Python perde para join em Go?" — e essa
pergunta não precisa de camadas. Se um dia surgir a pergunta "quanto custa N+1
dentro de arquitetura hexagonal", aí nasce `hexagonal-n-mais-1`. Não antes.

Nota: não existe estratégia `join-unico`. O join único é o que `minimal` já faz —
`list_order_items_with_product` é a intenção padrão. `n-mais-1` é o desvio.

## Estratégias são transversais às linguagens

`strategies/join-unico.md` descreve a estratégia em termos de **comportamento
observável e estrutura**, jamais em termos de uma linguagem. É a mesma spec que
o agente de Go e o de Python leem.

Consequência prática: se você não consegue escrever a estratégia sem citar uma
linguagem, ela não é uma estratégia — é uma particularidade de framework, e
pertence a `frameworks/`.

Isso é o que torna `go/http/join-unico` vs `python/fastapi/join-unico` uma
comparação legítima.

---

## Adicionar um eixo novo — checklist

1. Existe uma pergunta escrita que só esse eixo responde? Sem pergunta, não
   entra na matriz (PLAN §11).
2. Ele exige código diferente, ou é um knob? Knob não vira diretório.
3. Qual diretório da taxonomia? Se mais de um, divida.
4. `afeta_medicao`? Se sim, quais runs existentes ele invalida?
5. Escreva a spec com as cinco seções e um critério de aceite executável.
6. Só então gere a primeira implementação.

---

## O que não é spec

- `docs/PLAN.md` — estratégia do projeto e metodologia. Contexto, não norma.
- `docs/adr/` — decisões tomadas e seu porquê, com data. Histórico imutável.
- `docs/findings/` — conclusões de experimentos. Saída, não entrada.
- `docs/Arquitetura.md`, `docs/Requisitos_arquiteturais.md` — razão de ser das
  escolhas; a formalização normativa delas está em `specs/DDD/general.md`.

Spec descreve o que construir. ADR registra por que se decidiu. Finding relata o
que se descobriu. Misturar os três é como as specs apodrecem.
