import streamlit as st
import uuid

from langchain_core.messages import HumanMessage, AIMessage

from langgraph_tool import chatbot


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# GENERATE NEW THREAD ID
# ============================================================

def generate_thread_id():
    return str(uuid.uuid4())


# ============================================================
# ADD THREAD
# ============================================================

def add_thread(thread_id):

    if thread_id not in st.session_state["chat_threads"]:

        st.session_state["chat_threads"].append(
            thread_id
        )


# ============================================================
# LOAD THREAD FROM MEMORYSAVER
# ============================================================

def load_thread(thread_id):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:

        state = chatbot.get_state(config)

        messages = state.values.get(
            "messages",
            []
        )

        temp_messages = []

        for msg in messages:

            # -------------------------------
            # Human message
            # -------------------------------

            if isinstance(msg, HumanMessage):

                temp_messages.append({
                    "role": "user",
                    "content": msg.content
                })

            # -------------------------------
            # AI message
            # -------------------------------

            elif isinstance(msg, AIMessage):

                # AIMessage content can sometimes
                # be a list/dict when tools are involved.
                if isinstance(msg.content, str):

                    content = msg.content

                else:

                    content = str(msg.content)

                # Don't display empty AI messages
                if content.strip():

                    temp_messages.append({
                        "role": "assistant",
                        "content": content
                    })

        return temp_messages

    except Exception as e:

        st.error(
            f"Error loading thread: {e}"
        )

        return []


# ============================================================
# CREATE NEW CHAT
# ============================================================

def create_new_chat():

    new_thread_id = generate_thread_id()

    st.session_state["thread_id"] = new_thread_id

    st.session_state["message_history"] = []

    add_thread(new_thread_id)


# ============================================================
# SESSION STATE
# ============================================================

if "message_history" not in st.session_state:

    st.session_state["message_history"] = []


if "thread_id" not in st.session_state:

    st.session_state["thread_id"] = generate_thread_id()


if "chat_threads" not in st.session_state:

    st.session_state["chat_threads"] = []


# Make sure current thread is registered
add_thread(
    st.session_state["thread_id"]
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🤖 LangGraph Chatbot")


# ============================================================
# NEW CHAT
# ============================================================

if st.sidebar.button(
    "➕ New Chat",
    width="stretch"
):

    create_new_chat()

    st.rerun()


# ============================================================
# PREVIOUS CONVERSATIONS
# ============================================================

st.sidebar.markdown(
    "### 💬 My Conversations"
)


for thread_id in st.session_state["chat_threads"]:

    short_thread_id = thread_id[:8]

    if st.sidebar.button(
        f"💬 {short_thread_id}",
        key=f"thread_{thread_id}",
        width="stretch"
    ):

        # --------------------------------------------
        # Change current thread
        # --------------------------------------------

        st.session_state["thread_id"] = thread_id

        # --------------------------------------------
        # Load messages from MemorySaver
        # --------------------------------------------

        st.session_state["message_history"] = (
            load_thread(thread_id)
        )

        st.rerun()


# ============================================================
# CURRENT THREAD ID
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Current Thread ID"
)

st.sidebar.code(
    st.session_state["thread_id"]
)


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state["message_history"]:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Type your message..."
)


if user_input:

    # ========================================================
    # CURRENT THREAD CONFIG
    # ========================================================

    CONFIG = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        },

        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },

        "run_name": "chat_name"
    }


    # ========================================================
    # SAVE USER MESSAGE IN STREAMLIT
    # ========================================================

    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })


    # ========================================================
    # DISPLAY USER MESSAGE
    # ========================================================

    with st.chat_message("user"):

        st.markdown(user_input)


    # ========================================================
    # AI RESPONSE
    # ========================================================

    with st.chat_message("assistant"):

        ai_message = st.write_stream(

            message_chunk.content

            for message_chunk, metadata

            in chatbot.stream(

                {
                    "messages": [
                        HumanMessage(
                            content=user_input
                        )
                    ]
                },

                config=CONFIG,

                stream_mode="messages"
            )
        )


    # ========================================================
    # SAVE AI RESPONSE
    # ========================================================

    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })