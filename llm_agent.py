import os
from graph_database import db 
from scheduler import auto_schedule_tasks

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

@tool
def add_task_tool(title: str, duration_minutes: int, priority: str) -> str:
    """
    Use this tool to add a new task.
    Requires title, duration in minutes, and priority (High/Medium/Low).
    """
    query = f"""
    MERGE (t:Task {{title: '{title}'}})
    SET t.duration_minutes = {duration_minutes}, 
        t.priority = '{priority}',
        t.status = 'pending'
    """
    try:
        from graph_database import conn
        conn.execute(query)
        return f"تم إضافة المهمة '{title}' بنجاح."
    except Exception as e:
        return f"حدث خطأ: {e}"

@tool
def schedule_tasks_tool(date: str) -> str:
    """
    Use this tool to automatically schedule tasks.
    Requires date in format YYYY-MM-DD.
    """
    try:
        result = auto_schedule_tasks(date)
        return result
    except Exception as e:
        return f"خطأ في الجدولة: {e}"

tools = [add_task_tool, schedule_tasks_tool]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a strictly constrained AI scheduling assistant.
    RULES:
    1. If the user wants to add a task, use add_task_tool.
    2. If the user wants to schedule tasks, use schedule_tasks_tool. 
    3. DO NOT invent tools or try to query the database directly.
    Always reply in polite Arabic.
    """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def chat_with_data(user_query):
    try:
        response = agent_executor.invoke({"input": user_query})
        return response["output"]
    except Exception as e:
        return f"عذراً، واجهت مشكلة: {e}"