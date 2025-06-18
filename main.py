import os
from chainlit.user import Provider
from dotenv import load_dotenv
import chainlit as cl
from agents import Agent,Runner,AsyncOpenAI,OpenAIChatCompletionsModel,function_tool
import requests
from typing import Dict,Optional
load_dotenv()
api_key=os.getenv("GEMINI_API_KEY")
provider=AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)
model_name=OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)
@function_tool
def get_shaheer_info():
    response=requests.get("https://mocki.io/v1/92db5441-8216-4a92-9a36-908d5faff5da").json()
    return response

greeting_agent=Agent(
    name="Greeting_Agent",
    instructions="""You are a Greeting Agent designed to provide friendly interactions and information about Shaheer Naeem.

Your responsibilities:
1. Greet users warmly when they say hello (respond with 'Salam from Shaheer Naeem')
3. you can also provide the what the user asked previously and also what you answer from the  history
2. Say goodbye appropriately when users leave (respond with 'Allah Hafiz from Shaheer Naeem')
3. When users request information about Shaheer Naeem, use the get_shaheer_info function to retrieve and share his profile information and you also have to share his picture from the link provided in the response.
4. For any questions not related to greetings or Shaheer Naeem, politely explain: 'I'm only able to provide greetings and information about Shaheer Naeem. I can't answer other questions at this time.'

Always maintain a friendly, professional tone and ensure responses are helpful within your defined scope.""",
model=model_name,
tools=[get_shaheer_info]
)
@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User
) -> Optional[cl.User]:
    print("🔐 OAuth Callback Triggered")
    print(f"Provider: {provider_id}")
    print(f"Token: {token}")
    print(f"User Data: {raw_user_data}")
    return default_user


@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history",[])
    await cl.Message(
        content="""
        Welcome to the Greeting Agent!
        1. You can ask me about Shaheer Naeem.
        2. You can say hello to greet me.
        3. You can say goodbye to end the conversation.
        """,
        author="Greeting_Agent"
    ).send()
@cl.on_message
async def handle_message(message: cl.Message):
  history=cl.user_session.get("history")
  history.append(
    {"role":"user","content":message.content}
  )
  result=await cl.make_async(Runner.run_sync)(greeting_agent,input=history)
  response_text=result.final_output
  await cl.Message(content=response_text).send()
  history.append(
    {"role":"assistant","content":response_text}
  )
  cl.user_session.set("history",history)