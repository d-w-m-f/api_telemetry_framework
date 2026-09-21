# Business Rules Documentation

PS: This is not a business rules documentation, but rather is a explanation of the core business domain

## Test/comparison criteria

1. Language Python, Java, Go, ...
2. HTTP client: FastAPI, GinGonic
   2.1 Specific client implementations: FastAPI async, FastAPI sync, GinGonic w/ channels
3. Test category: Read or Write
4. Test type: Sequential read, complex joins read, bulk write
   4.1 Test configurations: category size (small, medium, big, extreme), environment resources, repetitions, etc.
5. Load type
6. DB engine (PostgreSQL only for now, but it will become a knob)