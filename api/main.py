from fastapi import FastAPI

app = FastAPI(
    title="London Air Quality API",
    description="API serving air quality data in London",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "service": "London Air Quality API",
        "status": "running",
        "version": "1.0.0"
    }