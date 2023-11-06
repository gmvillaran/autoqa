from fastapi import APIRouter

from restapi.api import qa, vectorstore

api_router = APIRouter()
api_router.include_router(qa.router, prefix="/qa", tags=["qa"])
api_router.include_router(
    vectorstore.router, prefix="/vectorstore", tags=["vectorstore"]
)
