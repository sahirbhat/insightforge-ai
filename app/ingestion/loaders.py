import tempfile

from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader


async def load_pdf(file: UploadFile):

    content = await file.read()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        temp_file.write(content)

        temp_path = temp_file.name

    loader = PyPDFLoader(temp_path)

    documents = loader.load()

    return documents