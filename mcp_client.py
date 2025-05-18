import os
import json
from pprint import pprint
import asyncio
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from IPython.display import Image, display
import re
import base64


async def main():
    with open("./settings.json", "r") as settings_file:
        settings = json.load(settings_file)

    os.environ["ANTHROPIC_API_KEY"] = settings["anthropic_api_key"]
    model = init_chat_model("claude-3-5-sonnet-latest", model_provider="anthropic")

    client = await MultiServerMCPClient(
        {
            "stock": {
                "command": "python",
                "args": ["/Users/teson/ai_agent/mcp_server.py"],
                "transport": "stdio",
            }
        }
    ).__aenter__()

    tools = client.get_tools()
    agent = create_react_agent(model, tools)

    agent_response = await agent.ainvoke({
        "messages": [HumanMessage("2025年4月1から2025年4月5日までのOracleの株の終値を取得し、その値を使ってmatplotlibのチャートを作成してください。")]
    })

    pprint(agent_response)

    match = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', str(agent_response))
    if match:
        image_data = match.group(1)
        display(Image(data=base64.b64decode(image_data)))
    else:
        print(agent_response)

    await client.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(main())
