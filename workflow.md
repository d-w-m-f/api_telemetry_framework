# Qual é o workflow do DDDKit.

## Skills do workflow do framework

Estas são inegociaveis, e são a SDK oferecida.

/interview:
É uma skill pra entrevistar o usuario sobre o que ele quer construir. Isso vai servir para construir um documento chamado interview.md que fica em specs/brainstorm/interview.md

/map-requirements
É mais uma skill de entrevista. Esta é pra mapear requisitos funcionais especificamente. Tecnicamente, é a mesma coisa que a anterior. Mas de um ponto de vista de UX e comportamental, nao é. É uma separação clara que te obriga a pensar e a separar dois conceitos 'O que voce quer construir' e 'O que voce tem como necessidades/metas/objetivos que esse software produza'.

/map-contexts:
É uma skill para gerar os contextos, com base na entrevista e nos requerimentos mapeados, vai pensar em construir os BoundedContexts. Vai produzir o context-map.md e as pastas dos subdominios dentro de BoundedContexts. Isso só pode rodar depois de, pelo menos, 1 interview E 1 map requirements. 

/model-context:
É uma skill pra poder especificar o subdominio, gerando os modulos. Aqui vamos ter que definir:
- domain.md
- vocabulary.md


/plan-context:
É uma skill pra planejar um contexto, gerando o plano tecnico arquitetural. Analogo a speckit-plan. Vai gerar os
plan.md
que ficam dentro dos modulos 

/generate-tasks:
É uma skill pra gerar as tasks em si. Analogo a speckit-tasks. Vai gerar os
tasks.md
que ficam dentro dos modulos

PS: Eu quero pensar em mudar esse nome de generate-tasks pra outra coisa, pensar em sugestoes

/implement
É uma skill pra enfim implementar as tasks. Pode criar um roadmap.md para quebrar em partes, ou seja, talvez tenha que rodar varios /implements

/implement-progress
É uma skill pra ir ver no roadmap.md qual é o progresso das implementações


PS: Preciso de sugestões em qual parte do processo de dev que deveria ser criados:
- repomap.md
- regra-de-negocio.md


## Skills de funcionamento interno do framework

Estas são para traduzir comportamentos complexos que o agente pode ter que tomar, pra ele saber como agir. Estas vão garantir coisas como o bom seguimento do SdSFC

/discover-bounded-context
É uma skill pra orientar o Claude entender como achar um modulo dentro do um bounded context; Se eu quiser um contexto nomeado X, eu vou precisar:

1. ler specs/BoundedContexts/[logical_folders]/X: Precisa de um script python pra achar o endereço do contexto!
output do passo 1: Endereço da pasta do contexto

2. ler domain.md, vocabulary.md, pra entender sobre o bounded context

3. let repomap.md, que conterá onde ficam as regras de negocio do modulo, a estrutura dele no repo, como sao os modulos (se são arquivos, pasta, etc), nomenclatura dos markdowns a buscar (regra-de-negocio.md pra modulos pasta, mesmo nome do arquivo pra modulos file)

4. Output deve ser o caminho dos arquivos que devem ser lidos, assim o agente vai saber consumir (eu espero). 

PS: Lembre que vamos achar os arquivos por uuid.

## passo a passo idealizado de desenvolvimento

1. /interview
2. /map-requirements
3. /map-contexts, mapeando todos os contextos
4. /model-context, modelando todos os contextos
5. /plan-context, planejando tecnicamente todos os contextos
6. /generate-tasks
7. /implement


## Memorando: Coisas importantes:
Precisa mexer na /integrations do dddkit; mapear os arquivos da .dddkit/; gerar script pra escrever a md5sum deles

Um linter da estrutura do DDDkit. Isto é, um comando que eu vou rodar no terminal e que vai rodar scripts pra conferir:
- Se todos os boundedcontexts do context-map estão criando em BoundedContexts com nome corrto
- Se todos os repomap de bounded contexts encontram arquivos de regra-de-negocio e outros markdowns do Spec-driven Single File Components
- Se a estrutura de diretorios descrita nos headers do repomap dos BoundedContexts esta correta.
- Se as md5sums da /integrations e etc batem
PS: O linter tem que ser em Rust.


## Templates e arquivos

Aqui nessa seção ficam o que devem ser os arquivos do framework.  Todos arquivos listados aqui tem que existir tanto como um template dentro da .dddkit, como vao existir pelo projeto, dentro da /specs e pelo repositorio.

### Lista

Constitution.md: A constituição do projeto (vai pro contexto todo prompt do user)
DDD.md: A constituição de como fazer DDD (vai pro contexto todo prompt do user)
context-map.md: Um mapa com todos os nomes dos contextos.
domain.md: Descrição do dominio de um BoundedContext
vocabulary.md: Descrição da linguagem ubíqua do modulo
repomap.md: Mapeamento dos arquivos no (precisa ser por uma chave/ID/uuid, não por um PATH. Assim, se o user troca um dir de lugar, ainda da pra achar)
headers.yaml: Os headers aceitos
shared_vocabulary.md
interview.md: Artefato construido pelas interviews.
plan.md: Analogo ao papel no speckit
tasks.md: Analogo ao papel no speckit
checklist.md: Analogo ao papel no speckit
spec.md: Analogo ao papel no speckit


## Lembretes: Comportamentos importantes

. ground language
. versionamento de docs/specs (versionar é ter um doc com um atributo numerico de versao)