from langchain_core.prompts import ChatPromptTemplate


rag_prompt = ChatPromptTemplate.from_template(
    """
    You are a helpful AI assistant.

    Answer the user's question using only the provided context.

    If the answer is not available in the context,
    say "The information was not found in the document."

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
)