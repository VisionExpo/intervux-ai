import yaml
from pathlib import Path

PROMPT_PATH = Path(__file__).parent / "prompts.yaml"

class PromptManager:
    def __init__(self):
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            self.prompts = yaml.safe_load(f)["system_prompts"]

    def get(self, prompt_name: str, **kwargs) -> str;
        """
        Fetch and format a prompt safely.
        """
        if prompt_name not in self.prompts:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        
        return self.prompts[prompt_name].format(**kwargs)