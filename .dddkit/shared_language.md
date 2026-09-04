---
id: META-UBIQUITOUS-01
filename: shared_language.md
version: 1.0.0
status: approved
---

# Linguagem Ubíqua Global (Shared Language)

Este documento define os termos globais usados em todo o projeto, transversais aos Bounded Contexts. Termos específicos de um Bounded Context devem ir no `vocabulary.md` daquele domínio.

### 3. Arquitetura SdSFC
*   **SdSFC (Spec-driven Single-File Components):** Padrão do projeto onde a documentação e especificação (`regra-de-negocio.md`) reside junto com o código-fonte (componente) que a implementa, eliminando o abismo entre documentação e código.
*   **Wildcard de Implementação:** Padrão de busca (ex: `src/**/catalog`) definido no header `implemented_in` das specs em `/specs`, usado por scripts determinísticos para validar se a spec possui uma contraparte no código-fonte.
