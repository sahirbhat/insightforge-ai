from langchain_core.output_parsers import StrOutputParser

from app.rag.prompt import rag_prompt
from app.rag.llm import llm


rag_chain = (rag_prompt| llm| StrOutputParser())


async def generate_answer(
    question: str,
    context: str
):

    answer = await rag_chain.ainvoke({
        "question": question,
        "context": context
    })

    return answer