# FastAPI Rules

When coding a Python API with FastAPI, adhere to the following specifications:

1. Utilize layered architecture as in:

```text
business/         # Layer for business rules
- services/

persistente/      # Layer for interacting with database
- models/         # ORMs/Connectors to database layer
- repositories/   # Functions/Classes to acesss database layer

presentation/     # 
- routes/
- schema/         # Pydantic data validation schemas

app.py  # Aggregation of routes
main.py # API Entrypoint
```


2. Don't consider test writing and unit test coverage as metrics for evaluating functional development. The correctness of the contracts should be evaluated by telemetry flux integration. 

3. Utilize main.py as the app entrypoint; utilize a factory pattern consuming an environment variable for stantiating the correct HTTP client (FastAPI, Starlette, etc...)