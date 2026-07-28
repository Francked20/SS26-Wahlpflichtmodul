from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from endpoints import primes, ecbcbcwtf, ecb_oracle, export_cipher
from endpoints.dh_export import router as dh_export_router
from lifespan import challenge_backend_lifespan

app = FastAPI(title="Challenge Backend", lifespan=challenge_backend_lifespan)

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
app.include_router(dh_export_router, prefix="/dh_export", tags=["dh_export"])
app.include_router(export_cipher.router, prefix="/export_cipher", tags=["export_cipher"])
