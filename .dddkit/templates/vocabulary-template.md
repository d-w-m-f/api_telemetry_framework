---
implements_uuid: [SAME_UUID_AS_DOMAIN_MD]
filename: vocabulary.md
version: 1.0.0
status: draft
---

# Vocabulary: [MODULE_NAME]

<!--
  ACTION REQUIRED: This is the ubiquitous language local to this module.
  Terms that are global to the whole project belong in
  .dddkit/shared_language.md instead - do not duplicate them here unless
  this module gives a term a more specific meaning, in which case say so
  explicitly.
-->

## Terms

| Term | Definition | Usage Context |
|------|------------|----------------|
| [Term1] | [Precise, unambiguous definition as used by domain experts] | [Where/when this term is used] |
| [Term2] | [Definition] | [Context] |

## Terms Inherited from Shared Language

<!--
  ACTION REQUIRED: List terms from .dddkit/shared_language.md that this
  module actively uses, so a reader knows which global vocabulary applies
  here without re-reading the whole shared_language.md file.
-->

- [Term] — see `.dddkit/shared_language.md`

## Notes

- If a term here conflicts with the same word used in another Bounded Context, that is expected — ubiquitous language is local to its context. Do not "fix" the conflict; document it in the relationship section of `domain.md` instead.
