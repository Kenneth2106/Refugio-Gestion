from fastapi import FastAPI

app = FastAPI(
    title="Bar Inventory API",
    version="1.0.0",
    description="Sistema de gestión de inventario para bar Refugio y sus diferentes sedes"
)


@app.get("/")
def root():
    return {
        "message": "Bar Inventory API funcionando"
    }