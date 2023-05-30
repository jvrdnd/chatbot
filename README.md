# Simple Chatbot

A chatbot with minimal dependencies.


## Objectives

- This project demonstrates how to build a chatbot for small datasets with minimal dependencies.
- It is released with the dataset and web UI that power [the chat](https://chat.scalevp.com) for Scale Venture Partners.
- It can be easily (and freely) customized for any organization.


## How it works

The chatbot implements a basic agent that integrates with a local vector database and OpenAI models.

<img src="https://chat.scalevp.com/img/architecture.png" alt="Chatbot architecture">

Read more about the background, architecture and learnings in [the release announcement](https://www.scalevp.com/blog/open-sourcing-the-scale-chatbot) on our blog.


## How to use it

### Docker (recommended)

1. Set your OpenAI API key in the `OPENAI_API_KEY` environment variable: `export OPENAI_API_KEY=your_openai_api_key`
2. Clone the repository: `git clone https://github.com/jvrdnd/chatbot.git`
3. Navigate to the repository: `cd chatbot`
4. Start the chatbot: `docker compose up --build`
5. Go to [127.0.0.1](http://127.0.0.1) in your browser
6. Start asking questions!

### Local

1. Set the `OPENAI_API_KEY` environment variable to your OpenAI API key: `export OPENAI_API_KEY=your_openai_api_key`
2. Clone the repository: `git clone https://github.com/jvrdnd/chatbot.git`
3. Navigate to the repository: `cd chatbot`
4. Set the `INDEX_PATH` environment variable to a directory in which you have write permissions: `export INDEX_PATH=your_path`
5. Install the dependencies: `pip install -r api/src/requirements.txt`
6. Run the job that populates the vector database: `python job/src/main.py`
7. Start the API: `uwsgi --http :9090 --wsgi-file api/src/app.py --gevent 100`
8. Open the file `ui/src/index.html` in your browser
9. Start asking questions!


## How to customize it

### Data

The documents that go into the vector database are generated from `job/src/data.json` following the `job/src/schema.json` specification. Customizing these files will enable the chatbot to answer questions about your data.

`data.json` and `schema.json` have matching top-level attributes which define document sections. For example, in the case of the Scale chatbot, the sections mirror those on our website because that is the source of our data.

Each section contains a list of documents, each of which is represented by a series of attributes captured in `data.json`. Using `schema.json`, this structured data is encoded into plain text documents that can be turned into embeddings. Each document is encoded as follows:
- The first line shows the name of the current section (specified in the `heading` attribute of the schema), as well as the values of select attributes of the data (whose key is specified in the `context` attribute of the schema).
- For every attribute that is not part of the context, a page is created. An optional descriptor for the page contents can be shown on the second line of the document if it is specifed in the `descriptors` attribute of the schema.

`data.json` and `schema.json` in this repository provide a comprehensive example of how to construct your own data files.

### Web UI

The web UI implements server-sent events (SSE) to support streaming responses from the LLM. It can be fully customized by making changes to the files in `ui/src/`.