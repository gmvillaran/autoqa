from fastapi import APIRouter, UploadFile, status

from restapi.core import logger
from vectorstore.connector import ChromaCRUD, monitor

router = APIRouter()
monitor.logger = logger
client = monitor.client


# TODO Update/Remove for sample only
@router.post("/", status_code=status.HTTP_200_OK)
def insert_knowledgebase(file: UploadFile, data: dict):
    crud = ChromaCRUD(client=client)
    collections = client.list_collections()
    print(collections)
    test = crud.create_item(
        embeddings=[1.5, 2.9, 3.4],
        metadatas={"uri": "img9.png", "style": "style1"},
        documents="doc1000101",
        collection_name="test_collection",
        ids="uri9",
    )
    return test
