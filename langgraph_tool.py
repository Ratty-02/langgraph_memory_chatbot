from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from typing import TypedDict, Annotated

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

from langgraph.checkpoint.memory import MemorySaver


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)


# ============================================================
# TOOLS
# ============================================================

search_tool = DuckDuckGoSearchRun(
    region="us-en"
)


@tool
def calculator(
    num_1: int,
    num_2: int,
    operation: str,
) -> dict:
    """
    Perform basic arithmetic:
    add, sub, mul, div.
    """

    try:

        if operation == "add":
            result = num_1 + num_2

        elif operation == "sub":
            result = num_1 - num_2

        elif operation == "mul":
            result = num_1 * num_2

        elif operation == "div":

            if num_2 == 0:
                return {
                    "error": "Cannot divide by zero"
                }

            result = num_1 / num_2

        else:
            return {
                "error": "Invalid operation"
            }

        return {
            "first_num": num_1,
            "second_num": num_2,
            "operation": operation,
            "result": result,
        }

    except Exception as e:

        return {
            "error": str(e)
        }


tools = [
    search_tool,
    calculator,
]


# ============================================================
# BIND TOOLS
# ============================================================

t = llm.bind_tools(tools)


# ============================================================
# STATE
# ============================================================

class ChatMessage(TypedDict):
    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]


# ============================================================
# CHAT NODE
# ============================================================

def chat_node(state: ChatMessage):

    messages = state["messages"]

    response = t.invoke(messages)

    return {
        "messages": [response]
    }


# ============================================================
# TOOL NODE
# ============================================================

tool_node = ToolNode(tools)


# ============================================================
# GRAPH
# ============================================================

graph = StateGraph(ChatMessage)


graph.add_node(
    "chat",
    chat_node
)

graph.add_node(
    "tools",
    tool_node
)


# ============================================================
# EDGES
# ============================================================

graph.add_edge(
    START,
    "chat"
)


graph.add_conditional_edges(
    "chat",
    tools_condition
)


graph.add_edge(
    "tools",
    "chat"
)


# ============================================================
# MEMORY CHECKPOINTER
# ============================================================

memory = MemorySaver()


# ============================================================
# COMPILE GRAPH
# ============================================================

chatbot = graph.compile(
    checkpointer=memory
)