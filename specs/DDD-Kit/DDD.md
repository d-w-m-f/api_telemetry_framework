---
todo-header
---

# Domain Driven Design (DDD) — Orientação geral

Esta especificação define as regras de separação estratégica de domínios da aplicação, e as orientações principais para desenvolvimento DDD orientado por especificações.

Esta documentação mapeia:
- quais domínios existem.
- ...

## 1. Regras principais

Este documento fica na raiz da pasta '/specs/DDD'. Assumimos essa como a raíz de todas as especificações de domínio.

Dentro dessa raiz, ficam documentos ubíquos e o diretorio BoundedContexts/.

BoundedContexts/ é o entrypoint de todas as specs geradas por este framework.

## 1.1 Dirmap

A estrutura hieráquica a partir da raiz specs é:

```bash
BoundedContexts/
  contextA/
    /modulo1
    /modulo2
    [pasta-logica]
      /modulo3
  contextB/
  /moduloN
  ...
DDD.md
headers.md
...
```

### 1.2 Diretorios de BoundedContext
Diretórios de domínio devem ter o nome do domínio em .

Exemplo: `LabExperiments`

E a esturutra hierárquica a seguir:
```bash
specs/
  BoundedContexts
```

### 1.3 Diretorios de modulos
Diretórios de modulos devem ter o nome do domínio em kebab-case.

Exemplo: `reference-domain`

E a esturutra a seguir:

```bash
specs/BoundedContext/nome-do-dominio/
├── domain.md
└── vocabulary.md
```


### 1.4 Pastas lógicas
Pastas lógicas - envoltas por [] - 

Pastas lógicas devem existir somente dois ou mais níveis abaixo de BoundedContexts/

Exemplo certo:


Exemplo errado:



## 1.2 Estrutura geral dos Markdowns de spec

```markdown
---
header-topics
---

body-specs

```

Onde header-topics referencia headers.md

body-specs define regras especificas pro tipo de markdown.

### 1.2.1 Markdowns Ubíquos

#### domain.md
Descrição:
header-topics referencia headers.md
body-specs define:
-
-

#### vocabulary.md
Descrição:
header-topics referencia headers.md
body-specs define:
-
-

#### shared_language.md
Descrição:
header-topics referencia headers.md
body-specs define:
-
-


#### contexts.md
Descrição
header-topics referencia headers.md
body-specs define:
-
-


#### regra-de-negocio.md
Descrição
header-topics referencia headers.md
body-specs define:
-
-
formato especial do body:

```body-specs
---
spec regra de negocios

---
spec fronteiras
```

## 1.3 Specs de regra de negócio

As specs de regra de negócio ficam junto dos módulos da aplicação, e NÃO DENTRO do diretório de specs. Essa ideia se chama **SdSFC** (Spec-driven Single-File Components).

Cada pasta da aplicação é tratada como um módulo, e cada módulo engloba em sí sua propria regra de negócio dentro do markdown 'regra-de-negocio.md'.


---

## 2. Sobre conflitos e comportamentos

Toda spec de construção que estiver conflitante com essa deve ser trazida para questionamento de um humano, explicando os termos do conflito.
