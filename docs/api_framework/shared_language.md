## Termos e Definições

### 1. Nível Meta (O Laboratório)
*   **Experimento (Experiment):** Uma configuração testável que visa medir throughput, latência e telemetria de uma ou mais APIs.
*   **Telemetria (Telemetry):** O conjunto de métricas coletadas (ex: uso de CPU, RAM, Tempo de Resposta) durante a execução de um Experimento.
*   **Throughput:** A vazão de requisições que uma API alvo consegue processar por segundo.

### 2. Nível Objeto (O Fixture)
*   **Fixture API (API Alvo):** A aplicação real que está sendo testada pelo laboratório.
*   **Domínio de Referência (Reference Domain):** O conjunto de regras de negócio "fakes" (Catálogo e Pedidos) que toda Fixture API deve implementar de maneira idêntica para que a medição do experimento seja justa e comparável.
*   **Catálogo (Catalog):** O repositório de itens disponíveis para a realização de pedidos.
*   **Pedido (Order):** A intenção de compra de itens do catálogo submetida a uma Fixture API.
