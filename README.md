# Open Deep Research
 
Open Deep Research is an open source assistant that automates research and produces customizable reports on any topic. It allows you to customize the research and writing process with specific models, prompts, report structure, and search tools. 

Sure! Here's a complete and production-ready `README.md` for your project. It includes an overview, setup instructions, API documentation for `/stream_report` and `/human_feedback`, and local ingestion details.

---

```markdown
# 🧠 Open Deep Research — AI-Powered Report Generation with LangGraph

This project is an AI-driven research and report generation system built using **LangGraph**, **OpenAI**, **FAISS**, and **FastAPI**. It supports real-time research planning, local document ingestion, human feedback, and streaming report generation.

---

## 🚀 Features

- 📄 Local PDF/Excel document ingestion and semantic chunking
- 🔍 Hybrid RAG pipeline with FAISS + Web Search (Tavily)
- 🧠 Report generation using OpenAI + Claude + Groq models
- 🔁 LangGraph-powered streaming and state management
- ✅ Supports human feedback + resume functionality

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/ItachiSRD/open_deep_research.git
cd open_deep_research
```

### 2. Create a `.env` File

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
TAVILY_API_KEY=your_tavily_key
```

> ⚠️ Ensure this file is added to `.gitignore` to avoid committing secrets.

### 3. Install Dependencies
```bash
conda create -n langgraph python=3.10 -y
conda activate langgraph

pip install -e .

pip uninstall numpy
pip uninstall pandas
conda install pandas
conda install numpy
conda install faiss-gpu
```

---

## 🧪 API Endpoints

### 🔄 `/stream_report`

Generates an AI research report based on user-provided topic input.

#### Request
```http
POST /stream_report
Content-Type: application/json

{
  "topic": "Impact of AI in Education",
  "useLocalFile": true
}
```

#### Response (Streaming)
- `type: section` — Intermediate content from sections
- `type: completed` — Final compiled report

#### Example:
```json
{
  "type": "completed",
  "content": "Here is the full research report on AI in education..."
}
```

---

### 🙋 `/human_feedback`

Used to provide user feedback or resume interrupted sessions.

#### Request
```http
POST /human_feedback
Content-Type: application/json

{
  "resume": true
}
```

- If `resume = String`, the system will use this feedback to improve its report Structure.
- If `resume = true`, report structure is finalised.

#### Response (Streaming)
- `type: interrupt` — When human input is awaited
- `type: completed` — Final report output after resume

---

## 📂 Local Document Ingestion

### How it Works:
1. Place your PDFs/Excels in `src/open_deep_research/data/`.
2. Set `useLocalFile: true` in `/stream_report`.
3. The app:
   - Loads documents
   - Extracts structured text with metadata
   - Generates embeddings using `text-embedding-3-large`
   - Stores and caches them via FAISS

### Vector DB Caching
- Embeddings are saved to disk (in `.faiss` and `.pkl`).
- Reused on subsequent runs to avoid recomputation.

---

## 📸 Architecture

```plaintext
User → /stream_report → LangGraph → [Local FAISS + Web Search] → AI Planner/Writers → Streamed Report
                      → /human_feedback → Pause & Resume with state
```

---

## ✅ TODO / Improvements

- Add LangChainEval metrics
- UI for document upload
- Streamlit frontend (WIP)
- Local GPT support

---


![report-generation](https://github.com/user-attachments/assets/6595d5cd-c981-43ec-8e8b-209e4fefc596)

## 🚀 Quickstart

Ensure you have API keys set for your desired search tools and models.

Available search tools:

* [Tavily API](https://tavily.com/) - General web search
* [Perplexity API](https://www.perplexity.ai/hub/blog/introducing-the-sonar-pro-api) - General web search
* [Exa API](https://exa.ai/) - Powerful neural search for web content
* [ArXiv](https://arxiv.org/) - Academic papers in physics, mathematics, computer science, and more
* [PubMed](https://pubmed.ncbi.nlm.nih.gov/) - Biomedical literature from MEDLINE, life science journals, and online books
* [Linkup API](https://www.linkup.so/) - General web search
* [DuckDuckGo API](https://duckduckgo.com/) - General web search
* [Google Search API/Scrapper](https://google.com/) - Create custom search engine [here](https://programmablesearchengine.google.com/controlpanel/all) and get API key [here](https://developers.google.com/custom-search/v1/introduction)

Open Deep Research uses a planner LLM for report planning and a writer LLM for report writing: 

* You can select any model that is integrated [with the `init_chat_model()` API](https://python.langchain.com/docs/how_to/chat_models_universal_init/)
* See full list of supported integrations [here](https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html)

### Using the package

```bash
pip install open-deep-research
```

As mentioned above, ensure API keys for LLMs and search tools are set: 
```bash
export TAVILY_API_KEY=<your_tavily_api_key>
export ANTHROPIC_API_KEY=<your_anthropic_api_key>
```

See [src/open_deep_research/graph.ipynb](src/open_deep_research/graph.ipynb) for example usage in a Jupyter notebook:

Compile the graph:
```python
from langgraph.checkpoint.memory import MemorySaver
from open_deep_research.graph import builder
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
```

Run the graph with a desired topic and configuration:
```python
import uuid 
thread = {"configurable": {"thread_id": str(uuid.uuid4()),
                           "search_api": "tavily",
                           "planner_provider": "anthropic",
                           "planner_model": "claude-3-7-sonnet-latest",
                           "writer_provider": "anthropic",
                           "writer_model": "claude-3-5-sonnet-latest",
                           "max_search_depth": 1,
                           }}

topic = "Overview of the AI inference market with focus on Fireworks, Together.ai, Groq"
async for event in graph.astream({"topic":topic,}, thread, stream_mode="updates"):
    print(event)
```

The graph will stop when the report plan is generated, and you can pass feedback to update the report plan:
```python
from langgraph.types import Command
async for event in graph.astream(Command(resume="Include a revenue estimate (ARR) in the sections"), thread, stream_mode="updates"):
    print(event)
```

When you are satisfied with the report plan, you can pass `True` to proceed to report generation:
```python
async for event in graph.astream(Command(resume=True), thread, stream_mode="updates"):
    print(event)
```

### Running LangGraph Studio UI locally

Clone the repository:
```bash
git clone https://github.com/langchain-ai/open_deep_research.git
cd open_deep_research
```

Then edit the `.env` file to customize the environment variables according to your needs. These environment variables control the model selection, search tools, and other configuration settings. When you run the application, these values will be automatically loaded via `python-dotenv` (because `langgraph.json` point to the "env" file).
```bash
cp .env.example .env
```

Set whatever APIs needed for your model and search tools.

Here are examples for several of the model and tool integrations available:
```bash
export TAVILY_API_KEY=<your_tavily_api_key>
export ANTHROPIC_API_KEY=<your_anthropic_api_key>
export OPENAI_API_KEY=<your_openai_api_key>
export PERPLEXITY_API_KEY=<your_perplexity_api_key>
export EXA_API_KEY=<your_exa_api_key>
export PUBMED_API_KEY=<your_pubmed_api_key>
export PUBMED_EMAIL=<your_email@example.com>
export LINKUP_API_KEY=<your_linkup_api_key>
export GOOGLE_API_KEY=<your_google_api_key>
export GOOGLE_CX=<your_google_custom_search_engine_id>
```

Launch the assistant with the LangGraph server locally, which will open in your browser:

#### Mac

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and start the LangGraph server
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev
```

#### Windows / Linux

```powershell
# Install dependencies 
pip install -e .
pip install -U "langgraph-cli[inmem]" 

# Start the LangGraph server
langgraph dev
```

Use this to open the Studio UI:
```
- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs
```

(1) Provide a `Topic` and hit `Submit`:

<img width="1326" alt="input" src="https://github.com/user-attachments/assets/de264b1b-8ea5-4090-8e72-e1ef1230262f" />

(2) This will generate a report plan and present it to the user for review.

(3) We can pass a string (`"..."`) with feedback to regenerate the plan based on the feedback.

<img width="1326" alt="feedback" src="https://github.com/user-attachments/assets/c308e888-4642-4c74-bc78-76576a2da919" />

(4) Or, we can just pass `true` to accept the plan.

<img width="1480" alt="accept" src="https://github.com/user-attachments/assets/ddeeb33b-fdce-494f-af8b-bd2acc1cef06" />

(5) Once accepted, the report sections will be generated.

<img width="1326" alt="report_gen" src="https://github.com/user-attachments/assets/74ff01cc-e7ed-47b8-bd0c-4ef615253c46" />

The report is produced as markdown.

<img width="1326" alt="report" src="https://github.com/user-attachments/assets/92d9f7b7-3aea-4025-be99-7fb0d4b47289" />

## 📖 Customizing the report

You can customize the research assistant's behavior through several parameters:

- `report_structure`: Define a custom structure for your report (defaults to a standard research report format)
- `number_of_queries`: Number of search queries to generate per section (default: 2)
- `max_search_depth`: Maximum number of reflection and search iterations (default: 2)
- `planner_provider`: Model provider for planning phase (default: "anthropic", but can be any provider from supported integrations with `init_chat_model` as listed [here](https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html))
- `planner_model`: Specific model for planning (default: "claude-3-7-sonnet-latest")
- `writer_provider`: Model provider for writing phase (default: "anthropic", but can be any provider from supported integrations with `init_chat_model` as listed [here](https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html))
- `writer_model`: Model for writing the report (default: "claude-3-5-sonnet-latest")
- `search_api`: API to use for web searches (default: "tavily", options include "perplexity", "exa", "arxiv", "pubmed", "linkup")

These configurations allow you to fine-tune the research process based on your needs, from adjusting the depth of research to selecting specific AI models for different phases of report generation.

### Search API Configuration

Not all search APIs support additional configuration parameters. Here are the ones that do:

- **Exa**: `max_characters`, `num_results`, `include_domains`, `exclude_domains`, `subpages`
  - Note: `include_domains` and `exclude_domains` cannot be used together
  - Particularly useful when you need to narrow your research to specific trusted sources, ensure information accuracy, or when your research requires using specified domains (e.g., academic journals, government sites)
  - Provides AI-generated summaries tailored to your specific query, making it easier to extract relevant information from search results
- **ArXiv**: `load_max_docs`, `get_full_documents`, `load_all_available_meta`
- **PubMed**: `top_k_results`, `email`, `api_key`, `doc_content_chars_max`
- **Linkup**: `depth`

Example with Exa configuration:
```python
thread = {"configurable": {"thread_id": str(uuid.uuid4()),
                           "search_api": "exa",
                           "search_api_config": {
                               "num_results": 5,
                               "include_domains": ["nature.com", "sciencedirect.com"]
                           },
                           # Other configuration...
                           }}
```

### Model Considerations

(1) You can pass any planner and writer models that are integrated [with the `init_chat_model()` API](https://python.langchain.com/docs/how_to/chat_models_universal_init/). See full list of supported integrations [here](https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html).

(2) **The planner and writer models need to support structured outputs**: Check whether structured outputs are supported by the model you are using [here](https://python.langchain.com/docs/integrations/chat/).

(3) With Groq, there are token per minute (TPM) limits if you are on the `on_demand` service tier:
- The `on_demand` service tier has a limit of `6000 TPM`
- You will want a [paid plan](https://github.com/cline/cline/issues/47#issuecomment-2640992272) for section writing with Groq models

(4) `deepseek-R1` [is not strong at function calling](https://api-docs.deepseek.com/guides/reasoning_model), which the assistant uses to generate structured outputs for report sections and report section grading. See example traces [here](https://smith.langchain.com/public/07d53997-4a6d-4ea8-9a1f-064a85cd6072/r).  
- Consider providers that are strong at function calling such as OpenAI, Anthropic, and certain OSS models like Groq's `llama-3.3-70b-versatile`.
- If you see the following error, it is likely due to the model not being able to produce structured outputs (see [trace](https://smith.langchain.com/public/8a6da065-3b8b-4a92-8df7-5468da336cbe/r)):
```
groq.APIError: Failed to call a function. Please adjust your prompt. See 'failed_generation' for more details.
```

## How it works
   
1. `Plan and Execute` - Open Deep Research follows a [plan-and-execute workflow](https://github.com/assafelovic/gpt-researcher) that separates planning from research, allowing for human-in-the-loop approval of a report plan before the more time-consuming research phase. It uses, by default, a [reasoning model](https://www.youtube.com/watch?v=f0RbwrBcFmc) to plan the report sections. During this phase, it uses web search to gather general information about the report topic to help in planning the report sections. But, it also accepts a report structure from the user to help guide the report sections as well as human feedback on the report plan.
   
2. `Research and Write` - Each section of the report is written in parallel. The research assistant uses web search via [Tavily API](https://tavily.com/), [Perplexity](https://www.perplexity.ai/hub/blog/introducing-the-sonar-pro-api), [Exa](https://exa.ai/), [ArXiv](https://arxiv.org/), [PubMed](https://pubmed.ncbi.nlm.nih.gov/) or [Linkup](https://www.linkup.so/) to gather information about each section topic. It will reflect on each report section and suggest follow-up questions for web search. This "depth" of research will proceed for any many iterations as the user wants. Any final sections, such as introductions and conclusions, are written after the main body of the report is written, which helps ensure that the report is cohesive and coherent. The planner determines main body versus final sections during the planning phase.

3. `Managing different types` - Open Deep Research is built on LangGraph, which has native support for configuration management [using assistants](https://langchain-ai.github.io/langgraph/concepts/assistants/). The report `structure` is a field in the graph configuration, which allows users to create different assistants for different types of reports. 

## UX

### Local deployment

Follow the [quickstart](#-quickstart) to start LangGraph server locally.

### Hosted deployment
 
You can easily deploy to [LangGraph Platform](https://langchain-ai.github.io/langgraph/concepts/#deployment-options). 

```
open_deep_research
├─ .env
├─ examples
│  ├─ arxiv.md
│  ├─ inference-market-gpt45.md
│  ├─ inference-market.md
│  └─ pubmed.md
├─ langgraph.json
├─ LICENSE
├─ pyproject.toml
├─ README.md
└─ src
   └─ open_deep_research
      ├─ .ipynb_checkpoints
      │  └─ graph-checkpoint.ipynb
      ├─ api
      │  ├─ .env
      │  ├─ main.py
      │  ├─ routes.py
      │  └─ __pycache__
      │     ├─ main.cpython-310.pyc
      │     ├─ main.cpython-312.pyc
      │     ├─ routes.cpython-310.pyc
      │     ├─ routes.cpython-312.pyc
      │     └─ streaming.cpython-312.pyc
      ├─ configuration.py
      ├─ data
      ├─faiss_index
      │   ├─ index.faiss
      │   └─ index.pkl
      ├─ graph.ipynb
      ├─ graph.py
      ├─ prompts.py
      ├─ state.py
      ├─ utils.py
      ├─ __init__.py
```