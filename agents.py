import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url

load_dotenv()

# Model setup
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="models/gemini-nano-banana-2.1",
    google_api_key=api_key,
    temperature=0,
)

# 1st Agent: Search
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are a dedicated web research assistant. "
            "You MUST use the 'web_search' tool to gather recent information. "
            "In your final output, always include a designated section titled 'FOUND_URLS:' "
            "listing every raw URL returned by the search tool, followed by your summary."
        ),
    )

# 2nd Agent: Reader
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are an expert web reader. You must inspect the text provided to you, "
            "identify the most relevant URL, and execute the 'scrape_url' tool on it "
            "to retrieve the full article body."
        ),
    )

# 3rd Chain: Writer
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured, and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual, and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# 4th Chain: Critic
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()