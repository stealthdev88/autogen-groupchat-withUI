import autogen
from user_proxy_webagent import UserProxyWebAgent
from groupchatweb import GroupChatManagerWeb
import asyncio
import os
import autogen
import json
from autogen import Agent
from dotenv import load_dotenv

load_dotenv()

LIBRARY_PATH = os.path.join(os.path.dirname(__file__),"agent_library.json")


CLAUDE_CONFIG = {
        "api_type": "anthropic",
        "model": "claude-3-5-sonnet-20240620",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "cache_seed": None,
        "temperature": 0
    }

LLAMA_CONFIG = {
        "api_type": "together",
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "api_key": os.getenv("TOGETHER_API_KEY"),
        "cache_seed": None,
        "temperature": 0
    }

GPT_4O_CONFIG = {
    "api_type": "openai",
    "model": "gpt-4o-mini",
    "api_key": os.getenv("OPENAI_API_KEY"),
    "temperature": 0.5,
    "cache_seed": None,
}

with open(LIBRARY_PATH) as f:
    agent_config = json.loads(f.read())


def custom_speaker_selection_func(last_speaker: Agent, groupchat: autogen.GroupChat):
    """Define a customized speaker selection function.
    A recommended way is to define a transition for each speaker in the groupchat.

    Returns:
        Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
    """
    messages = groupchat.messages
    if len(messages) <= 1:
        for agent in groupchat.agents:
            if agent.name == "user_proxy":
                return agent
    else:
        return "auto"

#############################################################################################
# this is where you put your Autogen logic, here I have a simple 2 agents with a function call
class AutogenChat():
    def __init__(self, chat_id=None, websocket=None):
        self.websocket = websocket
        self.chat_id = chat_id
        self.client_sent_queue = asyncio.Queue()
        self.client_receive_queue = asyncio.Queue()

        self.agents = []
        self.characters = ", ".join([agent for agent in agent_config.keys() if agent not in ["moderator"]])

        for agent, system_prompt in agent_config.items():
            if agent in ['lottery expert','mob expert']:
                continue
            if agent == "moderator":
                manager_config = {"llm_config" : CLAUDE_CONFIG,
                                  "human_input_mode":"NEVER",
                                    "system_message":system_prompt.format(characters=self.characters),
                                    "code_execution_config":False
                                  } 
            else:
                self.agents.append(autogen.AssistantAgent(
                    name=agent,
                    system_message=system_prompt,
                    llm_config=CLAUDE_CONFIG,
                    code_execution_config=False
                ))

        self.user_proxy = UserProxyWebAgent( 
            name="user_proxy",
            human_input_mode="ALWAYS", 
            system_message="""A human admin. Interact with the team to discuss the writing process.""",
            max_consecutive_auto_reply=5,
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
        )

        self.agents.extend([self.user_proxy])

        self.groupchat = autogen.GroupChat(agents=self.agents, 
            messages=[], 
            max_round=20,
            send_introductions=False,
            allow_repeat_speaker=False)

        self.manager = GroupChatManagerWeb(groupchat=self.groupchat, 
            **manager_config)
        self.manager.set_queues(self.client_sent_queue, self.client_receive_queue)
          
    async def start(self, message):
        await self.user_proxy.a_initiate_chat(
            self.manager,
            clear_history=True,
            message=message
        )