# LangChain UI-TARS Agent Guide

This guide explains how to use the LangChain agents for UI automation with the UI-TARS model deployed on SageMaker.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_langchain.txt
```

### 2. Set Up Environment Variables

Create a `.env` file:

```env
# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# AWS Configuration
AWS_REGION=us-east-1
SAGEMAKER_ENDPOINT_NAME=ui-tars-endpoint-123456
```

### 3. Basic Usage

```python
from langchain_ui_agent import create_ui_automation_agent
from langchain.llms import OpenAI

# Create agent
agent = create_ui_automation_agent(
    endpoint_name="your-endpoint-name",
    base_llm=OpenAI(temperature=0),
    verbose=True
)

# Run automation task
result = agent.run("Take a screenshot and describe what you see")
print(result)
```

## 🛠️ Agent Components

### UITARSTool
Analyzes screenshots using the UI-TARS model on SageMaker.

```python
from langchain_ui_agent import UITARSTool

tool = UITARSTool(endpoint_name="your-endpoint")
result = tool.run(
    image_path="screenshot.png",
    question="What buttons are visible on this screen?"
)
```

### ScreenCaptureTool
Captures screenshots for analysis.

```python
from langchain_ui_agent import ScreenCaptureTool

tool = ScreenCaptureTool()
result = tool.run()  # Saves screenshot with timestamp
```

### GUIActionTool
Performs GUI actions based on coordinates.

```python
from langchain_ui_agent import GUIActionTool

tool = GUIActionTool()
result = tool.run(
    action="click",
    coordinates=(100, 200)
)
```

## 🎯 Advanced Usage

### Multi-Modal Agent

The MultiModalAgent combines vision and language capabilities:

```python
from langchain_agent_examples import MultiModalAgent

agent = MultiModalAgent(
    endpoint_name="your-endpoint",
    llm_provider="openai"  # or "anthropic", "local"
)

# Execute complex workflow
result = agent.automate_workflow("""
    1. Open Settings app
    2. Navigate to Display settings
    3. Change resolution to 1920x1080
    4. Apply changes
""")
```

### Game Automation

Specialized agent for playing games:

```python
from langchain_agent_examples import GameAutomationAgent

game_agent = GameAutomationAgent(
    endpoint_name="your-endpoint",
    game_name="2048"
)

# Play a turn
result = game_agent.play_turn(
    screenshot_path="game.png",
    objective="Reach 2048 tile"
)
```

### Web Automation

Automate web browser tasks:

```python
from langchain_agent_examples import WebAutomationAgent

web_agent = WebAutomationAgent(
    endpoint_name="your-endpoint",
    browser="chrome"
)

# Automate web task
result = web_agent.automate_web_task(
    task_description="Fill out the contact form",
    starting_url="https://example.com/contact"
)
```

## 📋 Common Workflows

### 1. Application Testing

```python
# Test login flow
agent.run("""
    1. Take screenshot of login screen
    2. Enter username 'testuser' in username field
    3. Enter password in password field
    4. Click login button
    5. Verify successful login by checking for dashboard
""")
```

### 2. Data Extraction

```python
# Extract data from UI
agent.run("""
    1. Open the reports application
    2. Navigate to monthly sales report
    3. Extract all values from the sales table
    4. Save the data to a CSV file
""")
```

### 3. Automated Form Filling

```python
# Fill complex forms
agent.run("""
    1. Open the registration form
    2. Fill in all required fields with test data
    3. Upload a profile picture
    4. Submit the form
    5. Verify confirmation message
""")
```

## 🔧 Customization

### Adding Custom Tools

```python
from langchain.tools import Tool

def custom_ocr_tool(image_path: str) -> str:
    """Custom OCR implementation"""
    # Your OCR logic here
    return "Extracted text"

# Add to agent
custom_tool = Tool(
    name="custom_ocr",
    func=custom_ocr_tool,
    description="Extract text using custom OCR"
)

agent.tools.append(custom_tool)
```

### Custom Prompts

```python
from langchain.prompts import PromptTemplate

custom_prompt = PromptTemplate(
    input_variables=["task", "context"],
    template="""You are a UI testing expert.
    
Task: {task}
Context: {context}

Analyze the UI and provide detailed test results."""
)
```

## 🚨 Error Handling

```python
try:
    result = agent.run("Complex automation task")
except Exception as e:
    print(f"Automation failed: {e}")
    # Fallback logic
```

## 💡 Best Practices

1. **Always verify actions**: Check if actions were successful before proceeding
2. **Use waits appropriately**: Add delays between actions for UI updates
3. **Handle dynamic content**: Account for loading times and animations
4. **Error recovery**: Implement retry logic for failed actions
5. **Logging**: Enable verbose mode for debugging

## 🔍 Debugging

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Create agent with verbose mode
agent = create_ui_automation_agent(
    endpoint_name="your-endpoint",
    base_llm=llm,
    verbose=True  # Shows all intermediate steps
)
```

## 📊 Performance Tips

1. **Batch operations**: Group related actions together
2. **Cache screenshots**: Reuse screenshots when possible
3. **Optimize prompts**: Keep prompts concise and specific
4. **Use appropriate LLM**: Choose model based on task complexity

## 🆘 Troubleshooting

### Common Issues

1. **"Endpoint not found"**: Verify endpoint name and region
2. **"Screenshot failed"**: Check pyautogui permissions
3. **"Action failed"**: Ensure coordinates are correct
4. **"Timeout"**: Increase max_iterations or timeout values

### Getting Help

- Check agent execution logs
- Verify UI-TARS endpoint is running
- Test individual tools separately
- Review intermediate steps in verbose mode

## 📚 Resources

- [LangChain Documentation](https://docs.langchain.com/)
- [UI-TARS Model Page](https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B)
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)
- [AWS SageMaker Guide](https://docs.aws.amazon.com/sagemaker/)

---

**Note**: Remember to handle sensitive information appropriately when automating applications that contain personal or confidential data.
