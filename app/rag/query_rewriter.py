from langchain_core.prompts import ChatPromptTemplate

from .llm import llm


rewrite_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a query rewriting assistant.

        Rewrite the user's question into a clear and searchable query.

        Rules:
        - Fix spelling mistakes.
        - Fix grammatical mistakes.
        - Preserve the user's original meaning.
        - Do not answer the question.
        - Return only the rewritten query.
        """
    ),
    (
        "human",
        "{question}"
    )
])

# async def rewrite_query(question: str) -> str:

#     chain = rewrite_prompt | llm

#     response = await chain.ainvoke({
#         "question": question
#     })
#     print("RESPONSE:", response)
#     print("CONTENT:", response.content)
#     print("CONTENT TYPE:", type(response.content))

#     return question

#     rewritten_query = response.content.strip()

#     print("\n========== QUERY REWRITING ==========")
#     print(f"Original Query:  {question}")
#     print(f"Rewritten Query: {rewritten_query}")

#     return rewritten_query


async def rewrite_query(question: str) -> str:

    chain = rewrite_prompt | llm

    response = await chain.ainvoke({
        "question": question
    })

    rewritten_query = response.content[0]["text"].strip()

    print("\n========== QUERY REWRITING ==========")
    print(f"Original Query:  {question}")
    print(f"Rewritten Query: {rewritten_query}")

    return rewritten_query