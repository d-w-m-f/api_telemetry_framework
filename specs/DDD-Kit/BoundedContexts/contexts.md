
## 2. Contextos Delimitados

Este repositório contém **dois** Contextos Delimitados que operam em níveis de importância e complexidade diferentes:

###  **Nível meta — o Laboratório.**

Principal nível. 

Engloba: Experimentos, implementações, execuções, observações, resultados. 

É o produto final. Aqui DDD se aplica no sentido clássico: o domínio é descoberto, modelado, refinado, e as regras de negócio são não triviais, mudam com o aprendizado e com a evolução do projeto. Também, gastamos mais recursos aqui com planejamento, escalabilidade e manutenibilidade.

###  **Nível objeto — o Domínio de Referência.** 

Nível secundário.

Engloba catálogo e pedidos. 

São domínios reais, mas exercem, papel de **fixture**: São implementados por toda API sob teste.

Domínios do nível objeto são fixos por decreto, não descoberto por modelagem. Seu objetivo é ser implementado de forma idêntica em todas as APIs, garantindo medições justas pros experimentos.


#### Modelagem dos dominios ora

A aplicação tem que ter:

Backend de banco de dados (cuja fronteira usa hexagonal, i.e, expoe metodos por interfaces). 1 dominio

Catálogo e pedidos: São os endpoints base de benchmark. Os dominios fixture 
