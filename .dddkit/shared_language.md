<!--
Sync Impact Report
Version: 1.0.1 -> 2.0.0 (MAJOR: a term's definition changed in a way that
invalidates prior usage, per DDD.md section 5.)
Modified terms:
  - "Wildcard de Implementacao" (`code_glob`) -> demoted from authority to
    hint. It previously read as the mechanism deterministic scripts use to
    validate that a spec has a counterpart in the source tree. It is now
    explicitly a first-pass lookup optimization: the `uuid` is the sole source
    of truth for module identity, and a glob that disagrees with where the
    uuid actually is is the thing that is wrong. Any prior reading in which a
    glob miss constituted an architectural failure is invalidated.
Added sections:
  - "4. O Grafo Spec-Codigo" -> names the reference chain the linter proves,
    and fixes uuid-as-source-of-truth, Module Anchor, and Index-as-cache.
  - "5. Verificacoes Deterministicas" -> names the three concerns the linter
    enforces, and the Fixable Finding vs. Failure distinction.
Removed sections: none
Known inconsistency (NOT resolved here, needs an owner decision):
  `.dddkit/DDD.md` section 3 item 4 still calls `.dddkit/index.json` "the
  source of truth agents and scripts consult". Under this revision the index
  is a cache and the uuid is the source of truth. DDD.md is the higher
  authority and amending it is a constitution change, so it is flagged rather
  than edited here. Until it is amended, DDD.md section 3 and this document
  disagree.
Deferred TODOs:
  - Sections 1 and 2 have never existed in this file (it has always started at
    "3. Arquitetura SdSFC"). Numbering continues from 3 rather than renumbering
    existing content; resolve the gap when the missing sections are written.
-->

---
id: META-UBIQUITOUS-01
filename: shared_language.md
version: 2.0.0
status: approved
---

# Linguagem Ubíqua Global (Shared Language)

Este documento define os termos globais usados em todo o projeto, transversais aos Bounded Contexts. Termos específicos de um Bounded Context devem ir no `vocabulary.md` daquele domínio.

### 3. Arquitetura SdSFC
*   **SdSFC (Spec-driven Single-File Components):** Padrão do projeto onde a documentação e especificação (`business-rules.md`) reside junto com o código-fonte (componente) que a implementa, eliminando o abismo entre documentação e código.
*   **Wildcard de Implementação (`code_glob`):** **Pista, não autoridade.** Padrão de busca (ex: `src/**/catalog`) declarado no `repomap.md` de cada módulo, usado como primeira tentativa — rápida — de localizar a Âncora de Módulo. Se o glob não resolver, ou resolver para um lugar diferente de onde o `uuid` realmente está, quem está errado é o glob, não o módulo. Um glob desatualizado é um Achado Corrigível, nunca uma falha de arquitetura.

### 4. O Grafo Spec-Código (Spec-Code Graph)

*   **Grafo Spec-Código (Spec-Code Graph):** A cadeia de referências que liga uma especificação ao código que a implementa: `uuid` (em `domain.md`) → pasta de spec do módulo → Âncora de Módulo no código-fonte → arquivo de regras de negócio e forma esperada do módulo. O linter existe para provar que **todo salto dessa cadeia resolve**. Um salto quebrado é Deriva, não uma questão de estilo.

*   **Fonte de Verdade do Módulo (Module Source of Truth):** O `uuid` — e somente ele. Gerado uma única vez por `scaffold-context.py` e nunca reatribuído. Nenhum caminho, glob ou nome de pasta tem autoridade sobre a identidade de um módulo. Se o `uuid` é encontrado no projeto, o módulo existe; se não é encontrado, o módulo está perdido — independentemente do que qualquer caminho aponte.

*   **Âncora de Módulo (Module Anchor):** O arquivo markdown no código-fonte que carrega o `implements_uuid` do módulo (`business-rules.md` para módulos `folder`; `<nome-do-arquivo>.md` para módulos `file`). É por essa âncora que o módulo é localizado dentro do projeto: ela é a **presença do módulo no lado do código**, não apenas documentação sobre ele. Buscar a âncora é buscar o módulo.

*   **Índice (`.dddkit/index.json`):** Cache de resoluções (`uuid` → `spec_path`/`code_path`), gerado por `build-index.py`. É conveniência de performance, não fonte de verdade: um índice obsoleto ou apagado é sempre reconstruível varrendo o projeto atrás dos `uuid`. Consultar o índice é o caminho rápido; varrer por `uuid` é o caminho correto.

### 5. Verificações Determinísticas (Deterministic Checks)

*   **Correspondência Arquitetural (Architectural Match):** A exigência de que a arquitetura declarada e a arquitetura real coincidam nas duas direções — todo Bounded Context nomeado em `contexts.md` tem pasta, e toda pasta é nomeada em `contexts.md`. Nenhum órfão de nenhum lado.

*   **Integridade de Framework (Framework Integrity):** A verificação de que os arquivos do próprio dddkit (templates, scripts, skills) continuam idênticos aos hashes sha256 registrados nos manifestos de `.dddkit/integrations/`. Diferente das demais verificações, esta protege o **framework**, não o domínio do usuário.

*   **Deriva (Drift):** Qualquer divergência entre o que as specs afirmam e o que o repositório realmente contém. Deriva é sempre detectável de forma determinística — é precisamente o que o linter existe para tornar impossível de ignorar.

*   **Achado Corrigível vs. Falha (Fixable Finding vs. Failure):** Distinção central do linter. Um **Achado Corrigível** é uma divergência em dado *derivado* (glob desatualizado, índice obsoleto), reconstruível a partir da Fonte de Verdade sem decisão humana. Uma **Falha** é a ausência do que não pode ser derivado: o `uuid` não existe em lugar nenhum do projeto, ou a forma declarada em `module_kind` não corresponde ao que está em disco. Achados podem ser corrigidos automaticamente; Falhas exigem alguém escrever código ou tomar uma decisão.
