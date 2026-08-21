## Arquitetura escolhida

### Primaria

DDD - Domain Driven Design.
Porque: Aplicação se espalha por muitos módulos, cada um de regra de negócio e fronteiras não triviais. Adoção de DDD e modelagem precisa de domínios e fornteiras vai garantir maior robustez e escalabilidade ao código.

### Secundária

SDD - Spec Driven Development
Porque: O artefato principal da aplicação é a API. Utilização do SDD serve para criar specs que consigam guiar subagentes a comportarem-se como uma factory de APIs modulares por propriedades como:
- Linguagem
- Framework
- Dependências

Integração de todo restante do ambiente é entorno das APIs. Definição de fronteiras fixas para SQL/endpoints/domínio garante . Pensando em escalabilidade, implementação de SQL e endpoints novos é trivialmente escalável; implementação de novos dominios pode ser resolvida encapsulando regra de negócio em services.

Idealmente, todo aspecto variante é definido por uma spec. Subagente faz pescar as specs corretas pra carregar no contexto e codar o que precisar.



## Domínios

### 1. APIs

- Variavel em Linguagem, em framework dentro de linguagem, em recursos de linguagem testados.
- Cada API tem um 'nome' pra profilar/referenciar
- mais coisas referenciadas em requisitos_arquiteturais.

### 2. Banco de Dados

- Atual somente Postgres, mas ira expandir.
- Precisa implementar um contrato pra comunicar pra fora. Nas linguagens, tem que ser um protocolo de métodos para conversar com o banco. PS: A nivel de aplicação, isso exige um pattern de factory.
- Vive como domínio mais isolado, única comunicação é a fronteira.

### 3. Telemetria e K6

- Aqui, não compreendo bem, voce modela pensando no que estamos fazendo aqui. Separa se isso é 1 ou 2 dominios, escopo e etc. Tambem avalia se ve mais dominios.