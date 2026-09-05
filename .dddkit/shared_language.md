---
id: META-UBIQUITOUS-01
filename: shared_language.md
version: 1.0.1
status: approved
---

# Linguagem Ubíqua Global (Shared Language)

Este documento define os termos globais usados em todo o projeto, transversais aos Bounded Contexts. Termos específicos de um Bounded Context devem ir no `vocabulary.md` daquele domínio.

### 3. Arquitetura SdSFC
*   **SdSFC (Spec-driven Single-File Components):** Padrão do projeto onde a documentação e especificação (`business-rules.md`) reside junto com o código-fonte (componente) que a implementa, eliminando o abismo entre documentação e código.
*   **Wildcard de Implementação:** Padrão de busca (ex: `src/**/catalog`) definido no header `code_glob` do `repomap.md` de cada módulo, usado por scripts determinísticos para validar se a spec possui uma contraparte no código-fonte. Resolvido por `.dddkit/scripts/build-index.py` para dentro de `.dddkit/index.json`, que é a fonte de verdade consultada por agentes e scripts — não o glob relido em tempo de leitura.
