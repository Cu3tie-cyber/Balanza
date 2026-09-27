from fastapi import FastAPI

app = FastAPI(
    title="Balanza",
    description="A reliability-focused fintech backend API.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}