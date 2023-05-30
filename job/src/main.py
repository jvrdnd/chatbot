import json
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import numpy as np
import openai


# return a list of formatted documents
def encode_documents(data, page_size=1000, stride=800):
    with open("schema.json") as f:
        schema = json.load(f)
    
    documents = []
    # the data has sections (e.g., portfolio) which have pages (e.g., companies)
    for section, pages in data.items():
        for page in pages:
            # the context is a section heading followed by data attributes
            context = [schema[section]["heading"]]
            context += [page[c] for c in schema[section]["context"]]
            
            # input: ["PORTFOLIO COMPANIES", "Company", ["Investor 1", "Investor 2"]]
            # output: PORTFOLIO COMPANIES // Company // Investor 1, Investor 2
            context = " // ".join(
                [", ".join(c) if isinstance(c, list) else c for c in context]
            )
            
            for k, v in page.items():
                # skip empty pages and attributes shown in the heading
                if not v or k in schema[section]["context"]:
                    continue
                
                # include a descriptor for the page if the schema specifies one
                has_descriptor = k in schema[section].get("descriptors", [])
                k = schema[section]["descriptors"][k] if has_descriptor else ""
                
                # create a document with a concatenated list
                if isinstance(v, list):
                    documents.append((context, k, ", ".join(v)))
                
                # paginate and append a list of pages
                if isinstance(v, str):
                    i = 0
                    while True:
                        documents.append((context, k, v[i:i+page_size]))
                        if i + page_size >= len(v):
                            break
                        i += stride
    
    # input: ("SECTION // context", "DESCRIPTOR", "page")
    # output: SECTION // context\n\nDESCRIPTOR\npage
    documents = [
        f"{context}\n\n{k}{chr(10) if k else ''}{v}"
    for context, k, v in documents]

    return documents


# overwrite the database
def put_documents(documents, batch_size=100):
    embeddings = []
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        embeddings += [
            record["embedding"]
                for record in openai.Embedding.create(
                    model="text-embedding-ada-002",
                    input=batch
                )["data"]
        ]

    path = os.getenv("INDEX_PATH", os.path.join(os.path.sep, "usr", "idx"))
    if not os.path.exists(path):
        os.makedirs(path)

    # save the documents as a list
    with open(os.path.join(path, "documents.json"), "w") as f:
        json.dump(documents, f, ensure_ascii=False)
    
    # save the embeddings as a numpy array
    with open(os.path.join(path, "embeddings.npy"), "wb") as f:
        np.save(f, np.array(embeddings))


if __name__ == "__main__":
    with open("data.json") as f:
        data = json.load(f)

    documents = encode_documents(data)
    
    put_documents(documents)