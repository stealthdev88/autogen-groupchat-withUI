import os
import autogen
from dotenv import load_dotenv

load_dotenv()

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "groupchat",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    human_input_mode="TERMINATE",
)

coder = autogen.AssistantAgent(
    name="Coder",
    llm_config={
        "api_type": "openai",
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "cache_seed": None,
    },
)
pm = autogen.AssistantAgent(
    name="Product_manager",
    system_message="Creative in software product ideas.",
    llm_config={
        "api_type": "anthropic",
        "model": "claude-3-5-sonnet-20240620",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "cache_seed": None,
    },
)

if __name__ == "__main__":
    groupchat = autogen.GroupChat(agents=[user_proxy, coder, pm], messages=[], max_round=12)
    manager = autogen.GroupChatManager(groupchat=groupchat)
    user_proxy.initiate_chat(manager, message="Find a latest paper about gpt-4 on arxiv and find its potential applications in software.")