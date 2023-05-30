import json
import numpy as np
import os
from operator import itemgetter
from time import time
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import llm


# custom exceptions
class ToolError(Exception):
    pass
class ContextualizeError(ToolError):
    pass
class GetDocumentsError(ToolError):
    pass
class AnswerError(ToolError):
    pass


# return a question that incorporates any relevant context from the chat history
def contextualize(prompt, chat):
    if not chat["context"]:
        return chat["question"]

    # encode the chat history
    # input: {"question": "q2", "context": [{"question": "q1", "answer": "a1"}]}
    # output: A: q1\nB: a1\nA: q2
    history = "\n".join([
        "\n".join([
            f"{prompt['speakers'][s]}: {c[s]}"
        for s in ["question", "answer"] if s in c])
    for c in (chat["context"] + [{"question": chat["question"]}])])

    # prompt.system\n---\nhistory\n---\nprompt.instruction
    sections = [
        ("", prompt["system"]),
        ("", history),
        ("", prompt["instruction"])
    ]
    try:
        return llm.blocking_completion(sections)
    except llm.CompletionError:
        raise ContextualizeError


# return the top k matching documents for the query
index = {"ttl": 3600}
def get_documents(query, k=5):
    global index

    # reload the cached index if it has expired
    if time() - index.get("updated_at", 0) > index["ttl"]:
        path = os.getenv("INDEX_PATH", os.path.join(os.path.sep, "usr", "idx"))
        with open(os.path.join(path, "documents.json")) as f:
            index["documents"] = json.load(f)
        with open(os.path.join(path, "embeddings.npy"), "rb") as f:
            index["embeddings"] = np.load(f)
        index["updated_at"] = time()

    try:
        r = llm.embedding(query)
    except llm.EmbeddingError:
        raise GetDocumentsError
    query_embedding = np.array(r)

    # calculate the cosine distance to every item in the index
    distance = lambda a, b: (a @ b.T) / (np.linalg.norm(a) * np.linalg.norm(b))
    norms = distance(index["embeddings"], query_embedding)
    
    # pick the top k documents
    top_k = np.argpartition(norms, -k)[-k:]
    documents = list(itemgetter(*top_k)(index["documents"]))

    return documents

# return the answer stream for the question based on the top documents
def answer(prompt, question, top_documents):
    # RECORDS:\ndoc1\ndoc2\n---\nINSTRUCTIONS:\ninstr1\ninstr2\n---\nquestion
    sections = [
        ("RECORDS", top_documents),
        ("INSTRUCTIONS", prompt["instructions"]),
        ("", question)
    ]
    try:
        for chunk in llm.streaming_completion(sections):
            yield chunk
    except llm.CompletionError:
        raise AnswerError