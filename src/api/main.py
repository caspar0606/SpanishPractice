from fastapi import FastAPI

#from src.api.routers import drills, writing, reading  # your routers

app = FastAPI(title="Spanish Practice API")

# include routers
#app.include_router(drills.router, prefix="/drills", tags=["drills"])
#app.include_router(writing.router, prefix="/writing", tags=["writing"])
#app.include_router(reading.router, prefix="/reading", tags=["reading"])


@app.get("/")
def root():
    return {"status": "running"}