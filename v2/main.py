from fastapi import FastAPI

app = FastAPI(title="Dvorik Loyalty System")


@app.get("/")
async def root():
    return {"message": "Dvorik Loyalty System API"}
