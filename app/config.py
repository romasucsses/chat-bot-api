import getpass
import os
import datetime
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = getpass.getpass()

model = ChatOpenAI(model="gpt-3.5-turbo")
memory = MemorySaver()
search = TavilySearchResults(max_results=2)
tools = [search]
agent_executor = create_react_agent(model, tools, checkpointer=memory)

PRIVATE_KEY = os.getenv('SECRET_KEY')
ALGORITHM_JWT = "HS256"

DATABASE_URL = os.getenv('DATABASE_URL')


EXPIRATION_ACCESS_TOKEN = datetime.timedelta(minutes=int(os.getenv('EXPIRATION_ACCESS_TOKEN')))
EXPIRATION_REFRESH_TOKEN = datetime.timedelta(days=int(os.getenv('EXPIRATION_REFRESH_TOKEN')))