# LangGraph Tool-Calling AI Assistant

A production-oriented conversational AI application built with LangGraph, Groq, and Streamlit.

This project explores how modern LLM applications can move beyond simple prompt and response interactions by introducing tool calling, graph-based orchestration, conversation state, and multi-threaded chat sessions.

The application can decide when it needs external tools, execute the appropriate tool, process the result, and continue the conversation with the user.

## Live Demo

[Open the deployed application](https://langgraphmemorychatbot.streamlit.app/)

## What Makes This Project Different?

Most beginner LLM applications follow a simple flow:

```text
User -> LLM -> Response
```

This project uses an agentic workflow:

```text
                 +----------------+
                 |     User       |
                 +-------+--------+
                         |
                         v
                +----------------+
                |   LangGraph    |
                |  Chat Node     |
                +-------+--------+
                        |
                 Tool required?
                   /         \
                 No           Yes
                 |             |
                 v             v
          +-----------+   +-----------+
          |  Response  |   | Tool Node |
          +-----------+   +-----+-----+
                               |
                    +----------+----------+
                    |                     |
                    v                     v
              Web Search             Calculator
                    |                     |
                    +----------+----------+
                               |
                               v
                         +-----------+
                         |    LLM    |
                         +-----+-----+
                               |
                               v
                           Response
```

Instead of manually deciding which function to call, the LLM can determine when a tool is required and LangGraph controls the execution flow.

## Core Features

### Tool Calling

The assistant has access to multiple tools:

* Web search using DuckDuckGo
* Custom calculator tool for arithmetic operations

For example:

```text
User:
What is 1547 * 83?

Assistant:
Uses the calculator tool and returns the result.
```

For information that requires external knowledge:

```text
User:
What are the latest developments in artificial intelligence?

Assistant:
Invokes the web search tool, processes the results, and generates a response.
```

### Graph-Based Agent Workflow

The application is built around a LangGraph state machine.

The graph contains:

```text
START
  |
  v
Chat Node
  |
  +---- No tool call ----> END
  |
  +---- Tool call -------> Tool Node
                              |
                              v
                          Chat Node
```

This makes the execution flow explicit instead of hiding the orchestration inside a single function.

### Conversation Memory

The application uses LangGraph's `MemorySaver` checkpointer to maintain conversation state for individual thread IDs.

Each conversation receives a unique thread ID:

```text
thread_id
    |
    +-- conversation messages
    +-- tool calls
    +-- tool results
    +-- assistant responses
```

This allows multiple conversations to exist independently within the running application.

### Multiple Chat Threads

The Streamlit interface provides separate conversation threads.

Users can:

* Start a new conversation
* Switch between existing threads
* Continue previous conversations within the running application
* Maintain independent conversation state

### Streaming Responses

Assistant responses are streamed to the interface rather than waiting for the entire response to be generated.

This provides a more interactive experience and makes the application behave more like a modern AI assistant.

## Tech Stack

| Technology      | Purpose                                |
| --------------- | -------------------------------------- |
| Python          | Core programming language              |
| LangGraph       | Agent workflow and state orchestration |
| LangChain       | LLM and tool abstractions              |
| Groq            | LLM inference                          |
| DuckDuckGo DDGS | Web search                             |
| Streamlit       | Frontend and deployment                |
| Pydantic        | Data validation                        |
| python-dotenv   | Environment configuration              |

## Architecture

The backend is responsible for defining the agent workflow.

### 1. LLM

The application uses Groq for fast LLM inference.

```python
llm = ChatGroq(
    model="openai/gpt-oss-20b"
)
```

### 2. Tools

The model is provided with a set of tools:

```python
tools = [
    search_tool,
    calculator
]
```

The LLM is then bound to these tools:

```python
t = llm.bind_tools(tools)
```

### 3. Chat Node

The chat node receives the current conversation state and invokes the model.

```python
response = t.invoke(messages)
```

The model can either return a normal response or request a tool call.

### 4. Tool Node

LangGraph's `ToolNode` executes the requested tool.

```python
tool_node = ToolNode(tools)
```

### 5. Conditional Routing

LangGraph determines whether the conversation should continue directly or execute a tool.

```python
graph.add_conditional_edges(
    "chat",
    tools_condition
)
```

After a tool executes, the result is sent back to the chat node:

```python
graph.add_edge("tools", "chat")
```

This creates the agent loop:

```text
LLM
 |
 | tool call
 v
Tool
 |
 | tool result
 v
LLM
 |
 v
Final response
```

## Project Structure

```text
langgraph-memory-chatbot/
|
├── langgraph_tool.py
├── streamlit_frontend_db.py
├── requirements.txt
├── .gitignore
└── README.md
```

### `langgraph_tool.py`

Contains the core LangGraph application:

* LLM configuration
* Tool definitions
* Graph state
* Chat node
* Tool node
* Conditional routing
* Memory/checkpoint configuration

### `streamlit_frontend_db.py`

Contains the Streamlit interface:

* Chat interface
* Thread management
* Conversation history
* Thread switching
* Streaming responses

### `requirements.txt`

Contains the Python dependencies required for local development and Streamlit Cloud deployment.

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/langgraph-memory-chatbot.git
cd langgraph-memory-chatbot
```

### 2. Create a virtual environment

```bash
python -m venv myvenv
```

Activate it on Windows:

```powershell
myvenv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit your `.env` file to GitHub.

### 5. Run the application

```bash
streamlit run streamlit_frontend_db.py
```

The application will open in your browser.

## Deployment

The application is deployed using Streamlit Community Cloud.

Deployment flow:

```text
GitHub Repository
       |
       v
Streamlit Cloud
       |
       v
Install requirements
       |
       v
Load Streamlit Secrets
       |
       v
Run Streamlit Application
```

The deployed application is available here:

https://langgraphmemorychatbot.streamlit.app/

## Environment Variables

The application requires:

```text
GROQ_API_KEY
```

For Streamlit Cloud, the key should be configured through the application's Secrets settings.

The API key should never be hardcoded into the source code or committed to GitHub.

## Example Interactions

### General Conversation

```text
User:
Explain what a transformer model is.

Assistant:
Provides an explanation using the LLM.
```

### Mathematical Reasoning

```text
User:
Calculate 9876 / 24.

Assistant:
Invokes the calculator tool and returns the result.
```

### Web Search

```text
User:
Search for the latest developments in quantum computing.

Assistant:
Invokes the web search tool and uses the retrieved information
to formulate the response.
```

### Multi-Turn Conversation

```text
User:
What is RAG?

Assistant:
Explains Retrieval-Augmented Generation.

User:
What are its main components?

Assistant:
Uses the existing conversation context to answer the follow-up.
```

## Engineering Concepts Demonstrated

This project was built to understand and implement several concepts used in modern AI applications:

* LLM tool calling
* Agentic workflows
* Graph-based orchestration
* Stateful conversations
* Conditional routing
* Tool execution
* Checkpoint-based state management
* Streaming LLM responses
* Multi-threaded conversations
* API-based LLM inference
* Environment and secret management
* Cloud deployment

## Limitations

The current version intentionally keeps the architecture lightweight.

`MemorySaver` stores conversation state in memory. This means conversation state is not designed to survive a complete application restart or deployment restart.

For a production system, the next step would be replacing the in-memory checkpointer with persistent infrastructure such as PostgreSQL or another durable storage system.

## Future Improvements

Planned improvements include:

* Persistent conversation storage
* PostgreSQL-backed LangGraph checkpointing
* User authentication
* Persistent chat history
* More specialized tools
* Tool execution tracing
* Better error handling
* Rate limiting
* Evaluation of tool selection accuracy
* Observability and LangSmith integration
* Containerized deployment
* Production-grade session management

## Why I Built This

The goal of this project was not simply to build another chatbot.

I wanted to understand what happens when an LLM becomes part of a larger software system.

That meant working with:

```text
LLM
 +
Tools
 +
State
 +
Graph orchestration
 +
Frontend
 +
Deployment
```

The project therefore focuses on the engineering layer around LLMs, particularly how models can interact with tools and operate inside a controlled workflow.

## Author

**Rehan Azad**

Computer Science Engineering Student
Machine Learning | Deep Learning | Generative AI | AI Systems

GitHub: https://github.com/Ratty-02

LinkedIn: https://linkedin.com/in/rehanazad

## License

This project is available for educational and personal use.
