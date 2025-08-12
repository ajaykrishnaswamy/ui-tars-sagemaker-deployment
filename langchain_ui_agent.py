#!/usr/bin/env python3
"""
LangChain Agent for UI-TARS Model Interaction
This agent can analyze screenshots, automate GUI tasks, and provide intelligent responses
"""

import os
import base64
from typing import List, Dict, Any, Optional
from PIL import Image
import io

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.callbacks import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# For SageMaker endpoint interaction
import boto3
import json


class ScreenshotInput(BaseModel):
    """Input schema for screenshot analysis"""
    image_path: str = Field(description="Path to the screenshot image")
    question: str = Field(description="Question about the screenshot")


class UITARSTool(BaseTool):
    """Tool for interacting with UI-TARS model on SageMaker"""
    
    name = "ui_tars_analyzer"
    description = """
    Analyze screenshots and provide GUI automation guidance using UI-TARS model.
    Use this tool when you need to:
    - Understand what's on a screen
    - Get instructions for GUI automation
    - Analyze UI elements
    - Plan automated actions on interfaces
    """
    args_schema: type[BaseModel] = ScreenshotInput
    return_direct: bool = False
    
    def __init__(self, endpoint_name: str, region: str = "us-east-1"):
        super().__init__()
        self.endpoint_name = endpoint_name
        self.runtime_client = boto3.client('sagemaker-runtime', region_name=region)
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _run(
        self, 
        image_path: str, 
        question: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Run UI-TARS analysis on screenshot"""
        try:
            # Encode image
            image_data = self._encode_image(image_path)
            
            # Prepare payload for UI-TARS
            payload = {
                "inputs": {
                    "image": image_data,
                    "text": question
                },
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.1,
                    "do_sample": False
                }
            }
            
            # Call SageMaker endpoint
            response = self.runtime_client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )
            
            result = json.loads(response['Body'].read().decode())
            return result.get('generated_text', result)
            
        except Exception as e:
            return f"Error analyzing screenshot: {str(e)}"


class ScreenCaptureTool(BaseTool):
    """Tool for capturing screenshots"""
    
    name = "capture_screenshot"
    description = "Capture a screenshot of the current screen or a specific window"
    return_direct: bool = False
    
    def _run(
        self,
        window_name: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Capture screenshot using appropriate method for the OS"""
        try:
            import pyautogui
            
            # Generate unique filename
            import time
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            
            # Capture screenshot
            if window_name:
                # TODO: Implement window-specific capture
                screenshot = pyautogui.screenshot()
            else:
                screenshot = pyautogui.screenshot()
            
            # Save screenshot
            screenshot.save(filename)
            
            return f"Screenshot saved as {filename}"
            
        except ImportError:
            return "Error: pyautogui not installed. Run: pip install pyautogui"
        except Exception as e:
            return f"Error capturing screenshot: {str(e)}"


class GUIActionTool(BaseTool):
    """Tool for performing GUI actions based on UI-TARS guidance"""
    
    name = "perform_gui_action"
    description = """
    Perform GUI actions like clicking, typing, or navigating.
    Actions: click, double_click, right_click, type, key_press, move_to
    """
    return_direct: bool = False
    
    def _run(
        self,
        action: str,
        coordinates: Optional[tuple] = None,
        text: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute GUI action"""
        try:
            import pyautogui
            
            if action == "click" and coordinates:
                pyautogui.click(coordinates[0], coordinates[1])
                return f"Clicked at {coordinates}"
            
            elif action == "type" and text:
                pyautogui.typewrite(text)
                return f"Typed: {text}"
            
            elif action == "key_press" and text:
                pyautogui.press(text)
                return f"Pressed key: {text}"
            
            elif action == "move_to" and coordinates:
                pyautogui.moveTo(coordinates[0], coordinates[1])
                return f"Moved to {coordinates}"
            
            else:
                return f"Unknown action or missing parameters: {action}"
                
        except Exception as e:
            return f"Error performing action: {str(e)}"


def create_ui_automation_agent(
    endpoint_name: str,
    base_llm: Any,  # Your base LLM (OpenAI, Claude, etc.)
    verbose: bool = True
) -> AgentExecutor:
    """
    Create a LangChain agent for UI automation using UI-TARS
    
    Args:
        endpoint_name: SageMaker endpoint name for UI-TARS model
        base_llm: Base language model for the agent
        verbose: Whether to show detailed execution logs
    
    Returns:
        AgentExecutor ready for UI automation tasks
    """
    
    # Initialize tools
    tools = [
        UITARSTool(endpoint_name=endpoint_name),
        ScreenCaptureTool(),
        GUIActionTool()
    ]
    
    # Create agent prompt
    prompt = PromptTemplate(
        input_variables=["input", "tool_names", "tools", "agent_scratchpad"],
        template="""You are an AI assistant specialized in GUI automation using computer vision.

You have access to the following tools:
{tools}

Tool Names: {tool_names}

To use a tool, please use the following format:
Thought: I need to [describe what you want to do]
Action: [tool_name]
Action Input: [input for the tool]
Observation: [tool output]

You can repeat this Thought/Action/Action Input/Observation cycle as needed.

When you have completed the task or have a final answer, respond with:
Thought: I have completed the task/found the answer
Final Answer: [your final response]

Current task: {input}

Begin!

Thought: {agent_scratchpad}"""
    )
    
    # Create memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create the agent
    agent = create_react_agent(
        llm=base_llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=verbose,
        max_iterations=10,
        handle_parsing_errors=True
    )
    
    return agent_executor


class UIAutomationChain:
    """High-level chain for UI automation workflows"""
    
    def __init__(self, endpoint_name: str, base_llm: Any):
        self.endpoint_name = endpoint_name
        self.base_llm = base_llm
        self.agent = create_ui_automation_agent(endpoint_name, base_llm)
        
    def analyze_and_act(self, task: str) -> Dict[str, Any]:
        """
        Analyze the screen and perform automated actions
        
        Args:
            task: Description of what to accomplish
            
        Returns:
            Dictionary with results and actions taken
        """
        result = self.agent.run(task)
        return {
            "task": task,
            "result": result,
            "success": True
        }
    
    def guided_automation(self, screenshots: List[str], goal: str) -> List[Dict]:
        """
        Perform guided automation across multiple screenshots
        
        Args:
            screenshots: List of screenshot paths
            goal: Overall automation goal
            
        Returns:
            List of actions and results
        """
        results = []
        
        for i, screenshot in enumerate(screenshots):
            step_task = f"Analyze screenshot {screenshot} and determine the next action to achieve: {goal}"
            result = self.agent.run(step_task)
            results.append({
                "step": i + 1,
                "screenshot": screenshot,
                "analysis": result
            })
            
        return results


# Example usage functions
def create_automation_agent_example():
    """Example of creating and using the UI automation agent"""
    
    # Example with OpenAI
    from langchain.llms import OpenAI
    
    # Initialize base LLM
    llm = OpenAI(temperature=0)
    
    # Create UI automation agent
    agent = create_ui_automation_agent(
        endpoint_name="ui-tars-endpoint-123456",  # Your endpoint name
        base_llm=llm,
        verbose=True
    )
    
    # Example task
    result = agent.run(
        "Take a screenshot of the current screen and tell me what application is open"
    )
    print(result)
    
    return agent


def create_automation_chain_example():
    """Example of using the high-level automation chain"""
    
    from langchain.llms import OpenAI
    
    # Initialize chain
    chain = UIAutomationChain(
        endpoint_name="ui-tars-endpoint-123456",
        base_llm=OpenAI(temperature=0)
    )
    
    # Perform automation task
    result = chain.analyze_and_act(
        "Find and click on the Settings button in the current application"
    )
    print(result)
    
    return chain


if __name__ == "__main__":
    print("UI-TARS LangChain Agent")
    print("======================")
    print("This module provides LangChain tools and agents for UI automation")
    print("\nKey Components:")
    print("- UITARSTool: Analyze screenshots with UI-TARS model")
    print("- ScreenCaptureTool: Capture screenshots")
    print("- GUIActionTool: Perform GUI actions")
    print("- UIAutomationChain: High-level automation workflows")
    print("\nSee example functions for usage patterns")
