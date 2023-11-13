# from elasticapm.contrib.starlette import ElasticAPM
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from models.llm.llm_component import RAGLLM
from models.sa.sa_component import SAM
from qa_data import extractor

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    ServiceContext,
    LangchainEmbedding,
)

# from restapi.api import api_router
# from restapi.core import apm_client, logger, settings
# from restapi.core import  logger, settings
# from vectorstore.connector import monitor

# app = FastAPI(title=settings.PROJECT_NAME)
app = FastAPI()
# tz = settings.TIMEZONE
origins = ["*"]

# monitor.logger = logger
# client = monitor.client

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if apm_client is not None:
#     app.add_middleware(ElasticAPM, client=apm_client)

# app.include_router(api_router, prefix=settings.API_STR)


@app.on_event("startup")
async def startup_event():
    # monitor.start()
    return 0

# system_prompt (300 Tokens)
prompts_path = "./prompts/prompt_1.txt"

system_prompt = ""
with open(prompts_path, 'r') as file:
    system_prompt = file.read()

index = None
documents = SimpleDirectoryReader("./documents", filename_as_id=True).load_data()
embed_model = LangchainEmbedding(HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"))

# Create an instance of LLMInitializer
llm_initializer = RAGLLM(system_prompt)

# Initialize the LLM
llm = llm_initializer.initialize_llm()

# Create an instance of IndexManager
index_manager = IndexManager(documents, llm, embed_model)

# Define an endpoint for making queries
@app.post("/document-retrieval", tags=["Inference Endpoints"])
async def document_retrieval(query: str = Form(...)):
    try:
        response = index_manager.query_model(query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Error in retrieval-augmented generation:: {str(e)}")
    
@app.post("/auto-qa", tags=["Inference Endpoints"])
async def autoqa(
    recording_id: int = Form(...),
    query: str = Form(...),
):
    
    transcript = extractor.extract(recording_id, "./qa_data/transcriptions.csv")

    try:
        response = index_manager.query_model(query + "Transcription: " + transcript)
        return {
            "recording_id": 13660163,
            "transcript": transcript,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Error in retrieval-augmented generation:: {str(e)}")

from typing import List

@app.post("/auto-qa-batch", tags=["Inference Endpoints"])
async def autoqa_batch(
    recording_id: int = Form(...), 
    queries: List[str] = Form(...),
):

    transcript = extractor.extract(recording_id, "./qa_data/transcriptions.csv")

    responses = []
    for query in queries:
        try:
            response = index_manager.query_model(query + " Transcription: " + transcript)
            responses.append(response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in retrieval-augmented generation: {str(e)}")

    return {
        "recording_id": recording_id,
        "transcript": transcript,
        "responses": responses
    }

@app.get("/")
async def docs_redirect():
    # logger.info("Redirecting to docs")
    return RedirectResponse(url="/docs")
