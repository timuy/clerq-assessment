from fastapi import FastAPI


from src.routers import settlement_router

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(

    title="Clerq Assessment",
    version = "1.0",
    description = "Clreq Assessment"
)

app.include_router(settlement_router.router)
