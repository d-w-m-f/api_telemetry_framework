# Traçagem de requisitos

## O que é fixo?

Com isso quero dizer

- Domínio da API [PLAN.md 3] 
- SQL [PLAN.md 2] 
- Knobs [PLAN.md 2] 
- Estado inicial idêntico [PLAN.md 2] 
- Endpoints [PLAN.md 3] 

## O que é proporcional/variavel?

Com isso quero dizer, o que é imprescindivelmente implementado pensando em easy-switch (como ports/adapters, interface, etc...)

- "Orçamento" de hardware da máquina [PLAN.md 2] 
- Estrategia de teste/Metodologia de carga (Joelhada, etc...) [PLAN.md 3] [PLAN.md 5] 
- Num execuções [PLAN.md 2] 
- Dataset de teste [PLAN.md 3] 
- Banco de dados
- Métricas

## Requisitos arquiteturais:

Escolha de arquitetura: DDD.

Como criar uma API pra profilar? Eu acho melhor criar uma skill + setup de specs que definem:
- Como se cria uma API.
- Como se cria pra uma linguagem (Define particularidades do que usar pra fazer interfaces, etc...)


Add: E deixando aberto possibilidade do agente perguntar.

# O final product;

Produto web que pode:
- selecionar um setup pra testes para executar, config completa.
- Exibir extensos profiles de teste.
- guardar profiles de testes.
- fazer comparações