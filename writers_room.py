import os
import autogen
import json
from IPython.display import display
from PIL.Image import Image
from autogen import Agent
from dotenv import load_dotenv
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent

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
    "model": "gpt-4-vision-preview",
    "api_key": os.getenv("OPENAI_API_KEY"),
    "temperature": 0.5,
    "cache_seed": None,
}

with open(LIBRARY_PATH) as f:
    agent_config = json.loads(f.read())

agents = []
characters = ", ".join([agent for agent in agent_config.keys() if agent not in ["admin","moderator"]])

for agent, system_prompt in agent_config.items():
    if agent in ['lottery expert','mob expert']:
        continue
    if agent == "admin":
        agents.append(autogen.UserProxyAgent(
            name=agent,
            system_message=system_prompt,
            code_execution_config=False,
            human_input_mode="ALWAYS",
        ))
    elif agent == "illustrator":
        image_agent = MultimodalConversableAgent(
            name="illustrator",
            max_consecutive_auto_reply=10,
            llm_config=GPT_4O_CONFIG,
        )

        # Add image generation ability to the agent
        image_gen_capability = generate_images.ImageGeneration(
            image_generator=agent_instance, text_analyzer_llm_config=GPT_4O_CONFIG
        )

        image_gen_capability.add_to_agent(agent_instance)

    elif agent == "moderator":
        agents.append(autogen.AssistantAgent(
            name=agent,
            system_message=system_prompt.format(characters=characters),
            llm_config=CLAUDE_CONFIG,
            code_execution_config=False
        ))  
    else:
        agents.append(autogen.AssistantAgent(
            name=agent,
            system_message=system_prompt,
            llm_config=CLAUDE_CONFIG,
            code_execution_config=False
        ))

def extract_images(sender: autogen.ConversableAgent, recipient: autogen.ConversableAgent) -> Image:
    images = []
    all_messages = sender.chat_messages[recipient]

    for message in reversed(all_messages):
        # The GPT-4V format, where the content is an array of data
        contents = message.get("content", [])
        for content in contents:
            if isinstance(content, str):
                continue
            if content.get("type", "") == "image_url":
                img_data = content["image_url"]["url"]
                images.append(img_utils.get_pil_image(img_data))

    if not images:
        raise ValueError("No image data found in messages.")

    return images

def custom_speaker_selection_func(last_speaker: Agent, groupchat: autogen.GroupChat):
    """Define a customized speaker selection function.
    A recommended way is to define a transition for each speaker in the groupchat.

    Returns:
        Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
    """
    messages = groupchat.messages
    if len(messages) <= 1:
        for agent in groupchat.agents:
            if agent.name == "admin":
                return agent
            
    if len(messages) == 10 or ("image" in messages[-1]["content"]):
        for agent in groupchat.agents:
            if agent.name == "illustrator":
                images = extract_images(agent)
                for image in reversed(images):
                    display(image.resize((300, 300)))
                return agent
    
    if last_speaker.name == "admin":
        for agent in groupchat.agents:
            if agent.name == "moderator":
                return agent
        return "random"
    else:
        return "random"
    
if __name__ == "__main__":

    groupchat = autogen.GroupChat(
        admin_name="admin",
        agents=agents,
        messages=[],
        max_round=20,
        speaker_selection_method=custom_speaker_selection_func,
        send_introductions=False,
        allow_repeat_speaker=False
    )
    manager = autogen.GroupChatManager(groupchat=groupchat)
    for agent in agents:
        if agent.name == "moderator":
            agent.initiate_chat(manager, message="What would you like to do today?")
