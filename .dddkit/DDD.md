---
id: META-DDD-CONST-01
filename: DDD.md
version: 1.1.0
status: approved
domain_type: meta
---

# Domain Driven Design (DDD) — Constituição e Orientação Geral

Esta especificação atua como a **Constituição** do projeto. Ela define as regras inquebráveis de separação estratégica de domínios da aplicação, estruturação de diretórios e o padrão de desenvolvimento DDD-Kit orientado por especificações (SdSFC).

Qualquer agente, LLM ou desenvolvedor humano **DEVE** validar suas alterações arquiteturais contra este documento.

## 1. Regras Principais de Diretórios

A pasta raiz destas especificações é `/specs/DDD-Kit/`.
Dentro dela, encontram-se os documentos ubíquos (como este e o `shared_language.md`), os templates de IA e o diretório `BoundedContexts/`.

### 1.1 Dirmap da Pasta do DDDKit

### 1.2 Dirmap da Pasta de Especificações

A estrutura hierárquica a partir da raiz deve seguir rigidamente o padrão:

PS: Dirmap antigo abaixo, pra servir de exemplo em como construir os dirmaps
```text
specs/DDD-Kit/
├── BoundedContexts/          # Entrypoint das specs dos domínios
│   ├── ContextA/             # PascalCase para Contextos
│   │   ├── modulo-um/        # kebab-case para Módulos
│   │   │   ├── domain.md
│   │   │   └── vocabulary.md
│   │   └── [pasta-logica]/   # [envolto em colchetes] para agrupar módulos
│   │       └── modulo-dois/
│   └── ContextB/
├── templates/                # Templates para os artefatos de IA
├── prompts/                  # Prompts estruturados do workflow da IA
├── scripts/                  # Código determinístico (validações)
├── DDD.md                    # ESTE ARQUIVO (A Constituição)
├── headers.md                # Metadados esperados nos .md
└── shared_language.md        # Linguagem Ubíqua Global
```

### 1.3 Regras de Nomenclatura e Níveis

- **Bounded Contexts:** Devem ser nomeados em `PascalCase` (ex: `LabExperiments`, `ReferenceDomain`). Ficam diretamente abaixo de `BoundedContexts/`.
- **Módulos:** Devem ser nomeados em `kebab-case` (ex: `catalog-service`, `order-processing`). Módulos englobam um subdomínio e contêm os arquivos `domain.md` e `vocabulary.md`.
- **Pastas Lógicas:** Envoltas por colchetes (ex: `[infrastructure]`, `[core]`). Devem existir **somente** dois ou mais níveis abaixo de `BoundedContexts/`. Não podem conter markdowns de domínio diretamente, apenas agrupam módulos.

## 2. A Estrutura dos Markdowns de Spec

Todos os markdowns de especificação neste repositório devem seguir a estrutura:

```markdown
---
(Metadados copiados de headers.md preenchidos)
---
# Conteúdo
```

## 3. Padrão SdSFC (Spec-driven Single-File Components) e Rastreabilidade

O coração do DDD-Kit é a sincronia entre a documentação de alto nível (aqui em `/specs`) e a implementação real no código-fonte.

1. **A Especificação em `/specs` não é o código.** Os diretórios dentro de `BoundedContexts` contêm o **design** (`domain.md` e `vocabulary.md`).
2. **O header `implemented_in`:** Todo `domain.md` de um módulo **DEVE** possuir o campo `implemented_in` no seu header, utilizando um *wildcard* (glob) que aponte para onde aquele módulo reside na base de código real.
   - *Exemplo:* `implemented_in: "src/**/catalog/"` ou `implemented_in: "apps/backend/orders/"`.
3. **A Regra de Negócio vive com o Código:** Dentro do diretório do código-fonte apontado pelo *wildcard*, DEVE existir um arquivo `regra-de-negocio.md`. É lá que os detalhes finos (fluxos de dados, validações específicas e edge cases) devem ser documentados. Isso garante que o desenvolvedor lendo o código tenha a spec ao seu lado.
4. **Validação Determinística:** O script `validate-ddd.py` (ou similar) varre as specs procurando o `implemented_in` e valida se o diretório de destino realmente existe e se possui um `regra-de-negocio.md`. Falhas nessa validação quebram a pipeline (ou impedem o commit).

## 4. Sobre Conflitos e Comportamentos da IA

- O LLM está proibido de inferir a criação de novos Bounded Contexts sem passar pelo fluxo de `02-architect.md` e aprovação humana explícita.
- Toda spec de construção que entrar em conflito com esta Constituição deve ser trazida para questionamento ao humano, explicando os termos do conflito. A Constituição tem autoridade máxima.
