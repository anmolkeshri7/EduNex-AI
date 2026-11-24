
import streamlit as st
from google import genai
import time

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="EduNex AI",
    page_icon="🎓",
    layout="wide"
)

# ==================================================
# GEMINI CONFIGURATION
# ==================================================

MODEL = "gemini-3.5-flash-lite"

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)

except Exception:
    client = None

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>
.stApp {
    background-color: #f7f8fc;
}

.hero {
    background: linear-gradient(120deg, #172554, #4338ca);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 36px;
}

.hero p {
    color: #e0e7ff;
    font-size: 17px;
}

.feature {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    min-height: 130px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("🎓 EduNex AI")
st.sidebar.caption("Your Learning. Your Intelligence.")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "AI Tutor",
        "Notes Generator",
        "Quiz Generator",
        "Study Planner",
        "Text Summarizer"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Powered by Google Gemini")

# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>Welcome to EduNex AI 🚀</h1>
        <p>
        Your personal AI-powered learning companion.
        Learn smarter, prepare faster, and achieve more.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Your Learning Toolkit")
    st.write("Select a tool from the sidebar to begin.")

    col1, col2, col3 = st.columns(3)

    features = [
        ("🤖 AI Tutor", "Ask questions and understand difficult concepts."),
        ("📝 Notes Generator", "Generate organized study notes."),
        ("❓ Quiz Generator", "Test your knowledge with quizzes."),
        ("📅 Study Planner", "Organize your study schedule."),
        ("📚 Text Summarizer", "Summarize lengthy study material.")
    ]

    columns = [col1, col2, col3, col1, col2]

    for (title, description), column in zip(features, columns):

        with column:
            st.markdown(
                f"""
                <div class="feature">
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("")

# ==================================================
# AI TUTOR
# ==================================================

elif page == "AI Tutor":

    st.title("🤖 AI Tutor")
    st.write("Your personal academic assistant powered by Gemini.")

    if client is None:
        st.error(
            "Gemini API key not found. "
            "Check your .streamlit/secrets.toml file."
        )
        st.stop()

    # Student preferences

    col1, col2 = st.columns(2)

    with col1:
        subject = st.selectbox(
            "Select Subject",
            [
                "General",
                "Computer Science",
                "Mathematics",
                "Physics",
                "Chemistry",
                "Data Structures",
                "Artificial Intelligence",
                "Software Engineering"
            ]
        )

    with col2:
        level = st.selectbox(
            "Explanation Level",
            [
                "Beginner",
                "Intermediate",
                "Advanced",
                "Exam Preparation"
            ]
        )

    st.divider()

    # Initialize chat history

    if "tutor_messages" not in st.session_state:
        st.session_state.tutor_messages = []

    # Clear chat

    if st.button("🗑️ Clear Chat"):
        st.session_state.tutor_messages = []
        st.rerun()

    # Display previous messages

    for message in st.session_state.tutor_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input

    question = st.chat_input(
        "Ask your academic question here..."
    )

    if question:

        st.session_state.tutor_messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        # Build conversation history

        history = st.session_state.tutor_messages[:-1]

        conversation = ""

        for message in history:
            role = (
                "Student"
                if message["role"] == "user"
                else "Tutor"
            )

            conversation += (
                f"\n{role}: {message['content']}"
            )

        # Build prompt

        prompt = f"""
You are EduNex AI, a friendly academic tutor.

Subject: {subject}
Student level: {level}

Previous conversation:
{conversation}

Latest question:
{question}

Instructions:
1. Answer directly and accurately.
2. Use simple language.
3. Give examples when necessary.
4. Show steps for numerical problems.
5. Explain programming logic and provide code when needed.
6. Keep answers concise, around 200-300 words.
7. Use headings and bullet points where useful.
"""

        # Generate answer

        with st.chat_message("assistant"):

            answer = None

            with st.spinner("EduNex AI is thinking..."):

                for attempt in range(3):

                    try:

                        response = client.models.generate_content(
                            model=MODEL,
                            contents=prompt,
                            config={
                                "max_output_tokens": 512
                            }
                        )

                        answer = response.text

                        if not answer:
                            answer = (
                                "No response was generated. "
                                "Please try again."
                            )

                        break

                    except Exception as e:

                        error_message = str(e).upper()

                        retryable = any(
                            code in error_message
                            for code in [
                                "503",
                                "429",
                                "UNAVAILABLE",
                                "RESOURCE_EXHAUSTED",
                                "SERVICE_UNAVAILABLE"
                            ]
                        )

                        if retryable and attempt < 2:

                            wait_time = 2 ** (attempt + 1)

                            st.warning(
                                f"Gemini is busy. "
                                f"Retrying in {wait_time} seconds..."
                            )

                            time.sleep(wait_time)

                        elif retryable:

                            st.error(
                                "Gemini is currently unavailable "
                                "or overloaded. Please try again later."
                            )

                        else:

                            st.error(
                                f"Gemini API error: {e}"
                            )

                            break

            # Display and save answer

            if answer:

                st.markdown(answer)

                st.session_state.tutor_messages.append({
                    "role": "assistant",
                    "content": answer
                })

# ==================================================
# NOTES GENERATOR
# ==================================================

elif page == "Notes Generator":

    st.title("📝 Notes Generator")
    st.info("Notes Generator is coming in the next development step.")

# ==================================================
# QUIZ GENERATOR
# ==================================================

elif page == "Quiz Generator":

    st.title("❓ Quiz Generator")
    st.info("Quiz Generator is coming in the next development step.")

# ==================================================
# STUDY PLANNER
# ==================================================

elif page == "Study Planner":

    st.title("📅 Study Planner")
    st.info("Study Planner is coming in the next development step.")

# ==================================================
# TEXT SUMMARIZER
# ==================================================

elif page == "Text Summarizer":

    st.title("📚 Text Summarizer")
    st.info("Text Summarizer is coming in the next development step.")
