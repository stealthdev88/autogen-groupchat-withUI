import autogen
import os
import json
from autogen.agentchat.contrib.agent_builder import AgentBuilder
from dotenv import load_dotenv

load_dotenv()

LIBRARY_PATH = os.path.join(os.path.dirname(__file__),"agent_library_test.json")
PROMPTS_PATH = os.path.join(os.path.dirname(__file__),"prompt_templates.json")

with open(PROMPTS_PATH) as f:
    prompts = json.loads(f.read())

build_manager = autogen.OpenAIWrapper(config_list = [{
        "api_type": "anthropic",
        "model": "claude-3-5-sonnet-20240620",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "cache_seed": None,
        "temperature": 0
    }]
    )

position_list = [
    ("script writing","up and comer"),
    ("script writing","veteran")
]

sys_msg_list = []

if __name__ == "__main__":
    for pos, personality in position_list:
        resp_agent_sys_msg = (
            build_manager.create(
                messages=[
                    {
                    "role": "user",
                    "content": f"Please complete and return the only below template filling in the field with {pos}\n" +
                    prompts[personality].format(
                        creative_field=pos,
                        ),
                    }
                ]
            )
            .choices[0]
            .message.content
        )
        sys_msg_list.append({"name": "{} {}".format(pos, personality), "system_message": resp_agent_sys_msg})

    json.dump(sys_msg_list, open(LIBRARY_PATH, "w"), indent=4)