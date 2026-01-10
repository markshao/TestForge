from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum

class BrowserType(str, Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"

class TestEnv(BaseModel):
    base_url: str
    browser: BrowserType = BrowserType.CHROMIUM
    viewport: Dict[str, int] = Field(default_factory=lambda: {"width": 1280, "height": 720})
    headless: bool = False
    timeout: int = 30000

class StepType(str, Enum):
    ACTION = "action"
    VERIFICATION = "verification"

class Step(BaseModel):
    id: Union[int, str]
    type: StepType
    content: str

class TestCase(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    test_env: TestEnv = Field(alias="test-env")
    steps: List[Step]
