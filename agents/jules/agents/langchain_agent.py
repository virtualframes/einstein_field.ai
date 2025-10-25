from typing import Dict
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.fake import FakeListLLM
from agents.jules.agents.tools import summarize_documents

def create_agent(config: Dict) -> AgentExecutor:
    """
    Creates a LangChain-compatible agent instance.
    """
    tools = [
        Tool(
            name="summarize_documents",
            func=summarize_documents,
            description="Summarizes a list of documents.",
        )
    ]

    llm = FakeListLLM(responses=["Action: summarize_documents\nAction Input: query, docs, provenance_hint"])

    # This is a dummy prompt
    prompt = ChatPromptTemplate.from_template("{input}")

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True
    )

    return agent_executor
