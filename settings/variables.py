import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()

class Variables:
    LANGSMITH_API_KEY: Final[str] = os.getenv("LANGSMITH_API_KEY")