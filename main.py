from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from azure.storage.blob import BlobServiceClient
import requests
import os
import time

app = FastAPI()

origins = [
    "https://brave-meadow-08df98603.3.azurestaticapps.net",
]

# ---------------------------
# CORS – ezt kellett hozzáadni
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/translate")
async def translate_file(
    file: UploadFile = File(...),
    lang: str = Form(...)
):
    # Read text from uploaded file
    content = (await file.read()).decode("utf-8")

    # Translator API
    translator_key = os.environ["TRANSLATOR_KEY"]
    endpoint = os.environ["TRANSLATOR_ENDPOINT"]
    region = os.environ["TRANSLATOR_REGION"]

    url = f"{endpoint}/translate?api-version=3.0&to={lang}"

    response = requests.post(
        url,
        json=[{"Text": content}],
        headers={
            "Ocp-Apim-Subscription-Key": translator_key,
            "Ocp-Apim-Subscription-Region": region,
        }
    )

    translated = response.json()[0]["translations"][0]["text"]

    # Upload to Blob
    blob_conn = os.environ["BLOB_CONNECTION_STRING"]
    blob_service = BlobServiceClient.from_connection_string(blob_conn)
    container = blob_service.get_container_client("output-files")

    file_name = f"translated-{int(time.time())}.txt"
    container.upload_blob(file_name, translated, overwrite=True)

    return {"translated": translated, "blob": file_name}
