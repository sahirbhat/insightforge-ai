from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import settings


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=settings.GOOGLE_API_KEY
)