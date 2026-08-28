---
id: api/harness-contract
versao: 1
aplica_se_a: todas
depende_de: [api/knobs]
afeta_medicao: true
---

# Harness Contract

## Escopo

A única superfície pela qual o laboratório fala com um sujeito. Enquanto este
contrato for honrado, adicionar Rust ou Elixir custa um diretório e nenhuma
mudança no orquestrador.

Define: artefato de build, ciclo de vida, prontidão, encerramento, saída padrão.
Não define rotas de negócio (`reference-domain/contract.md`) nem nomes de
métricas (`api/telemetry.md`).

## Fixo

### Artefato

Cada implementação tem um `Dockerfile` na raiz do seu diretório
`src/subjects/<lang>/<framework>/<estrategia>/`. O contexto de build é aquele
diretório mais `db/queries/` e `api/`, montados pelo orquestrador.

- Imagem base com **tag imutável**, nunca `latest`. Versão de runtime é parte do
  resultado e vai gravada no manifesto do run.
- Build reprodutível: nenhuma resolução de dependência sem lockfile.
- A imagem não contém compilador nem ferramenta de build no estágio final.
- Um único processo em primeiro plano. Sem supervisor, sem shell wrapper que
  mascare sinais.

### Ciclo de vida

1. Todas as variáveis `LAB_*` são lidas **uma vez, na largada**. Nenhuma é
   consultada de novo em runtime — reconfiguração a quente é proibida, porque
   tornaria o setup do `Experimento` uma mentira.
2. O pool é aberto por completo (`LAB_POOL_SIZE` conexões) antes de qualquer
   endpoint aceitar tráfego.
3. As realizações SQL são carregadas de `db/queries/<engine>/` na largada.
4. Só então a porta passa a aceitar conexões e `/readyz` passa a retornar 200.

**A implementação nunca aplica migrations e nunca semeia dados.** Schema e
dataset são responsabilidade do Backend de Dados, aplicados pelo orquestrador
antes do container subir. Sujeito que mexe no schema contamina a réplica
seguinte.

### Prontidão e vivacidade

- `/healthz` — 200 enquanto o processo respira. Nunca toca o banco.
- `/readyz` — 200 apenas quando o pool está aberto e uma conexão responde a um
  `SELECT 1`. Enquanto não, 503 `urn:lab:not-ready`.

O orquestrador espera `/readyz` verde antes de iniciar o warmup. Uma
implementação que devolve 200 cedo demais empurra o custo de inicialização para
dentro da janela de medição — que é exatamente o que o warmup existe para
excluir.

### Encerramento

`SIGTERM` inicia encerramento gracioso: para de aceitar conexões novas, conclui
as em voo, fecha o pool, sai com código 0. Prazo máximo de 10 segundos; depois
disso o orquestrador manda `SIGKILL` e **marca o run como inválido**, porque
requisições abortadas na cauda distorcem os percentis finais.

### Saída padrão

- Log estruturado em JSON, uma linha por evento, em `stdout`. Nunca em arquivo.
- Nada além de `stdout` e `stderr` é escrito. Sem cache em disco, sem temporário,
  sem socket unix. Volume de escrita do container é sinal de IOPS do banco — um
  sujeito que escreve em disco polui essa medição.
- Códigos de saída: `0` graceful; `78` erro de configuração (ver `api/knobs.md`);
  qualquer outro é falha e invalida o run.

### O que a implementação não sabe

Ela não conhece `Experimento`, `Cenário`, `Run`, réplica ou qualquer conceito do
laboratório. Não lê `bench/`, não lê `results/`, não sabe que está sob medição.
A direção de dependência de `specs/DDD/general.md §3` é verificável: um `grep`
por esses termos dentro de `src/subjects/` deve não retornar nada.

## Livre

- Estágios do Dockerfile, gerenciador de dependências, layout de arquivos.
- Formato interno do log, desde que JSON por linha.
- Como o encerramento gracioso é implementado.

## Fronteiras

- `api/knobs.md` diz **quais** variáveis existem; este documento diz **quando**
  são lidas e o que acontece na falha.
- `api/telemetry.md` governa `/metrics`; aqui ele consta só para a superfície
  ficar completa.

## Aceite

`make conformance IMPL=<id>` — bloco `harness`. Verifica: `/readyz` só fica verde
depois do pool cheio; `SIGTERM` encerra em menos de 10s com código 0; nenhuma
escrita em disco durante uma execução de 60s (via `blkio` do container); ausência
de vocabulário do laboratório no código-fonte.
