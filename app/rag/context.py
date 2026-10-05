from langsmith import traceable


@traceable(name="Build Context")
def build_context(chunks):
    context = "\n\n".join(
        chunk.content
        for chunk in chunks
    )
    return context