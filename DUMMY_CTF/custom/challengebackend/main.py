from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from endpoints import primes, ecbcbcwtf, ecb_oracle

app = FastAPI(title="Challenge Backend")

# Redirect / to /docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# Healthcheck
@app.get("/ping/")
async def ping():
    return {"status": "ok"}

# Challenge-Routen einbinden
app.include_router(primes.router, prefix="/primes", tags=["primes"])
app.include_router(ecbcbcwtf.router, prefix="/ecbcbcwtf", tags=["ecbcbcwtf"])
app.include_router(ecb_oracle.router, prefix="/ecb_oracle", tags=["ecb_oracle"])
