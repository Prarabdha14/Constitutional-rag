import streamlit as st
from query_bot import answer_question
import os
from dotenv import load_dotenv

# --- SETUP AND STYLING ---
st.set_page_config(page_title="AI Constitution Bot", page_icon="🇮🇳", layout="wide")
load_dotenv()

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {file_name}. Create a 'style.css' file for custom styling.")

local_css("style.css")

# --- HELPER FUNCTION ---
def handle_question(question, sources):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Searching the constitution and generating an answer..."):
        answer, sources_found = answer_question(question, sources)
    assistant_message = {"role": "assistant", "content": answer}
    if sources_found:
        assistant_message["sources"] = sources_found
    st.session_state.messages.append(assistant_message)
    st.rerun()

# --- SIDEBAR (REORGANIZED) ---
with st.sidebar:
    st.title("🇮🇳 AI Constitution Bot")
    st.markdown("---")
    
    # "About" section is now at the top
    st.header("About This Project")
    st.info("This bot uses a Retrieval-Augmented Generation (RAG) system to answer questions based on the constitutional text of India.")
    
    st.subheader("How It Works")
    st.markdown("""
    1.  **Vector Embeddings:** The Constitution is broken into chunks and converted into numerical vectors.
    2.  **Vector Database:** These vectors are stored and indexed in a MongoDB Atlas collection.
    3.  **Retrieval:** Your question is used to find the most semantically similar chunks from the database.
    4.  **Generation:** The retrieved chunks and your question are sent to Google's Gemini model to generate an answer.
    """)
    
    st.markdown("---")

    # "Settings" and other controls are now below the "About" section
    st.header("Controls")
    with st.expander("Adjust Settings"):
        st.session_state.sources = st.slider(
            'Number of Sources to Retrieve', 1, 10, 5,
            help="Controls how many text chunks are used as context for the answer."
        )

    if st.button("Clear Conversation"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you understand the Indian Constitution today?"}]
        st.rerun()

# --- MAIN PAGE ---
st.title("Chat with the Constitution of India")
st.write("Ask any question, or try one of the suggestions below to get started.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you understand the Indian Constitution today?"}]

# --- EXPANDED: 2x3 GRID OF SUGGESTION BUTTONS ---
st.write("---")
st.subheader("Example Questions")
q_col1, q_col2, q_col3 = st.columns(3)
with q_col1:
    if st.button("What are the Fundamental Duties?"):
        handle_question("What are the fundamental duties of a citizen?", st.session_state.sources)
with q_col2:
    if st.button("What is the Right to Equality?"):
        handle_question("What does the constitution say about the right to equality?", st.session_state.sources)
with q_col3:
    if st.button("Who can declare a Financial Emergency?"):
        handle_question("Who can declare a financial emergency?", st.session_state.sources)

q_col4, q_col5, q_col6 = st.columns(3)
with q_col4:
    if st.button("What are Directive Principles?"):
        handle_question("What are the Directive Principles of State Policy?", st.session_state.sources)
with q_col5:
    if st.button("Explain the writ of Habeas Corpus."):
        handle_question("What is the writ of Habeas Corpus?", st.session_state.sources)
with q_col6:
    if st.button("How is the President of India elected?"):
        handle_question("How is the President of India elected?", st.session_state.sources)
# --- END OF GRID ---

st.write("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("View Sources Used"):
                for source in message["sources"]:
                    st.info(f"**Source:** {source.get('source_title', 'N/A')}\n\n**Text:** \"{source['text_chunk']}\"")

# Main chat input
if prompt := st.chat_input("What is your question?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    handle_question(prompt, st.session_state.sources)