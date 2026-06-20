from google.adk.agents import Agent

# Global variable to store PDF text content at runtime.
# Streamlit will write the parsed PDF text here, and the tool will fetch it.
pdf_content = ""

def get_document_content() -> str:
    """Retrieves the full text content of the uploaded PDF document to answer questions.
    
    Returns:
        str: The raw text content of the uploaded PDF.
    """
    global pdf_content
    if not pdf_content:
        return "No document has been uploaded yet. Please ask the user to upload a document."
    return pdf_content

# Define the Research Agent
researcher_agent = Agent(
    model="gemini-2.5-flash",
    name="researcher_agent",
    description="An AI agent that answers questions based on the text contents of an uploaded PDF document.",
    instruction=(
        "You are an expert academic research assistant.\n\n"
        "Your goal is to answer the user's questions based strictly on the uploaded PDF document.\n"
        "You have access to a tool called `get_document_content` which retrieves the entire text of the document.\n"
        "You MUST call this tool to read the document content before answering the user's question.\n"
        "Do not answer questions from memory if they are related to the document; use the tool's output as your sole source of truth.\n"
        "If the document does not contain the answer, clearly state that the information is not found in the uploaded document.\n"
        "Keep your answers concise, accurate, and directly cited from the document context where possible."
    ),
    tools=[get_document_content]
)

root_agent = researcher_agent
