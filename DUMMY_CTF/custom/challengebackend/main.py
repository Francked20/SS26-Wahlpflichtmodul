from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from database import MongoDB
from endpoints.dh_export import router as dh_export_router
from endpoints import primes, ecbcbcwtf, ecb_oracle


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Beanie/Mongo initialisieren, damit DhExportVariant-Abfragen funktionieren.
    mongo = MongoDB()
    await mongo.connect_mapper()
    app.state.mongo = mongo
    try:
        yield
    finally:
        await mongo.disconnect()


app = FastAPI(title="Challenge Backend", lifespan=lifespan)


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
