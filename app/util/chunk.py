def translate_context_chunk(chunks: list[dict]) -> str:
    context = ""
    for c in chunks:
        context += f"""
            \t- Professional: {c['professional_context']}
            \t- Relevance: {c['relevance_score']:.3f}
            \t- [{c['technology']}]: {c['content']}...
        """
    return context