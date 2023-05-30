import openai


# custom exceptions
class LLMError(Exception):
    pass
class EmbeddingError(LLMError):
    pass
class CompletionError(LLMError):
    pass


# wrapper for embedding
def embedding(query, model="text-embedding-ada-002"):
    try:
        r = openai.Embedding.create(model=model, input=query)
    except openai.error.OpenAIError:
        raise EmbeddingError
    return r["data"][0]["embedding"]


# wrapper for completion
def completion(
    sections,
    stream=False,
    model="gpt-3.5-turbo",
    temperature=.2,
    max_tokens=256
):
    # encode the prompt
    # input: {"section1": "str", "section2": ["str1", "str2"]}
    # output: "section1: str\n---\nsection2:\nstr1\nstr2"
    prompt = "\n---\n".join([
        f"{k}: {v}" if isinstance(v, str) else f"{k}:\n{chr(10).join(v)}"
    for k, v in sections])

    try:
        return openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            stream=stream,
            max_tokens=max_tokens
        )
    except openai.error.OpenAIError:
        raise CompletionError


# return message(s) from a completion
def blocking_completion(sections, **kwargs):
    return completion(sections, **kwargs)[0].message.content
def streaming_completion(sections, **kwargs):
    for r in completion(sections, True, **kwargs):
        chunk = r["choices"][0].get("delta", {}).get("content", "")
        if chunk:
            yield bytes(f"data: {chunk}\n\n", "utf8")