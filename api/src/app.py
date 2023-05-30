import json
import os
from urllib.parse import parse_qs
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import tools


def application(env, start_response):
    with open("prompts.json") as f:
        prompts = json.load(f)

    # parse the query string
    chat = {k: v[0] for k, v in parse_qs(env["QUERY_STRING"]).items()}
    chat["context"] = json.loads(chat.get("context", "{}"))

    # allow CORS for frontend requests
    headers = [("Access-Control-Allow-Origin", "*")]

    try:
        # execute the agent's chain of thought
        question = tools.contextualize(prompts["context"], chat)
        top_documents = tools.get_documents(question)
        answer = tools.answer(prompts["answer"], question, top_documents)

        # send events
        headers.append(("Content-Type", "text/event-stream"))
        start_response("200", headers)
        
        for chunk in answer:
            yield chunk
        yield bytes("data: [DONE]\n\n", "utf8")
    except tools.ToolError:
        headers.append(("Content-Type", "application/json"))
        start_response("502", headers)