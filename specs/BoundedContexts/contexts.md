---
id: META-CONTEXTS-01
filename: contexts.md
version: 1.0.0
status: approved
domain_type: meta
---

# Mapa de Contextos Delimitados (Context Map)

Este repositório contém **dois** Contextos Delimitados principais, operando em níveis arquiteturais e conceituais completamente diferentes. Eles servem aos propósitos da aplicação de benchmark e telemetria:

## 1. Nível Meta — O Laboratório (`LabExperiments`)

Este é o domínio primário e real da aplicação. Aqui o DDD se aplica no sentido clássico: o domínio precisa ser descoberto, modelado e refinado através de iterações.

- **Foco:** Orquestrar execuções de testes, registrar resultados de throughput (vazão) e armazenar métricas de telemetria.
- **Complexidade:** Alta. Regras de negócio envolvem processamento assíncrono, cálculo de percentis, limpeza de dados sujos e análise comparativa de arquiteturas de software.
- **Mutações:** As regras mudam conforme a necessidade de aprendizado e a evolução do projeto exigem novas formas de medição.
- **Implementação Típica:** Motores de carga (load generators), agregadores de métricas (crawlers de logs e traces) e orquestradores de containers.

## 2. Nível Objeto — O Domínio de Referência (`ReferenceDomain`)

Este é um domínio de nível secundário (suporte/fixture). Ele simula um e-commerce tradicional (Catálogo e Pedidos), mas com um propósito puramente instrumental.

- **Foco:** Fornecer um domínio "realista", porém padronizado, para que diferentes arquiteturas de API (Hexagonal, CQRS, MVC, etc) possam ser implementadas e comparadas de forma justa.
- **Complexidade:** Moderada, porém **FIXA**. É um domínio definido "por decreto". Suas regras não são descobertas ou refatoradas; elas existem para serem seguidas à risca.
- **Mutações:** Congelado. Qualquer alteração nesse domínio invalidaria o histórico comparativo de performance entre as diferentes APIs testadas.
- **Implementação Típica:**
  - Backends implementando os endpoints de ler o catálogo e disparar pedidos.
  - Dependências clássicas (Postgres, Redis, Kafka) operadas através dessas APIs.

## Como Mapear Novas Funcionalidades
- Se a funcionalidade for para *medir* algo, orquestrar um teste, plotar um gráfico ou processar logs, ela vai para `LabExperiments`.
- Se a funcionalidade for um endpoint que as APIs devem disponibilizar para receber requisições de carga, ela vai para `ReferenceDomain`.
