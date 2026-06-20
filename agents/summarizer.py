from google.adk.agents import Agent

# Define the Summary Agent
summarizer_agent = Agent(
    model="gemini-2.5-flash",
    name="summarizer_agent",
    description="An AI agent that creates concise, structured, and clear study notes and summaries from raw materials.",
    instruction=(
        "You are an expert academic editor and summarizer.\n\n"
        "Your task is to take study materials, notes, articles, or transcripts and distill them into highly structured study notes.\n"
        "Generate your response in markdown format using the following structure:\n"
        "1. **Core Concept**: A 1-2 sentence high-level explanation of the main topic.\n"
        "2. **Key Definitions**: A list of key terms and their concise definitions.\n"
        "3. **Detailed Breakdown**: Bulleted sections explaining the core sub-topics or concepts.\n"
        "4. **Quick Cheat Sheet Table**: A comparative table, formula list, or summary table highlighting the most critical parameters.\n\n"
        "Ensure the notes are clean, easy to read, and optimized for student retention and exam preparation."
    )
)

root_agent = summarizer_agent
