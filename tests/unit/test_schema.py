import pytest
import yaml
from forge.model.testcase import TestCase

def test_parse_yaml_testcase():
    yaml_content = """
name: "Google Search Test"
description: "Verify that Google search works correctly"
version: "1.0"

test-env:
  base_url: "https://www.google.com"
  browser: "chromium"
  viewport: { width: 1280, height: 720 }
  headless: false
  timeout: 30000

steps:
  - id: 1
    type: action
    content: "打开首页"

  - id: 2
    type: verification
    content: "网站标题 = xxx"
    """
    
    data = yaml.safe_load(yaml_content)
    testcase = TestCase(**data)
    
    assert testcase.name == "Google Search Test"
    assert testcase.test_env.base_url == "https://www.google.com"
    assert testcase.test_env.browser == "chromium"
    assert len(testcase.steps) == 2
    
    step1 = testcase.steps[0]
    assert step1.id == 1
    assert step1.type == "action"
    assert step1.content == "打开首页"
    
    step2 = testcase.steps[1]
    assert step2.id == 2
    assert step2.type == "verification"
    assert step2.content == "网站标题 = xxx"
