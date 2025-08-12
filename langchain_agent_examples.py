#!/usr/bin/env python3
"""
Advanced LangChain Agent Examples for UI-TARS
Demonstrates various configurations and use cases
"""

import os
from typing import List, Dict, Any
from langchain.agents import Tool, AgentExecutor
from langchain.memory import ConversationSummaryBufferMemory
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.schema import SystemMessage, HumanMessage

# Import our UI automation components
from langchain_ui_agent import (
    UITARSTool, 
    ScreenCaptureTool, 
    GUIActionTool,
    create_ui_automation_agent,
    UIAutomationChain
)


class MultiModalAgent:
    """
    Advanced multi-modal agent that combines UI-TARS vision capabilities
    with LLM reasoning for complex automation tasks
    """
    
    def __init__(self, endpoint_name: str, llm_provider: str = "openai"):
        self.endpoint_name = endpoint_name
        self.llm = self._create_llm(llm_provider)
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        
    def _create_llm(self, provider: str):
        """Create LLM based on provider choice"""
        
        if provider == "openai":
            from langchain.llms import OpenAI
            return OpenAI(
                temperature=0,
                model_name="gpt-4",
                streaming=True,
                callbacks=[StreamingStdOutCallbackHandler()]
            )
            
        elif provider == "anthropic":
            from langchain.llms import Anthropic
            return Anthropic(
                temperature=0,
                model="claude-2",
                streaming=True,
                callbacks=[StreamingStdOutCallbackHandler()]
            )
            
        elif provider == "local":
            from langchain.llms import LlamaCpp
            return LlamaCpp(
                model_path="./models/llama-2-7b.gguf",
                temperature=0,
                max_tokens=2000,
                n_ctx=2048
            )
            
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _create_tools(self) -> List[Tool]:
        """Create enhanced tools for the agent"""
        
        # Basic tools
        tools = [
            UITARSTool(endpoint_name=self.endpoint_name),
            ScreenCaptureTool(),
            GUIActionTool()
        ]
        
        # Add custom tools
        tools.extend([
            Tool(
                name="wait",
                func=self._wait_tool,
                description="Wait for specified seconds before next action"
            ),
            Tool(
                name="check_element",
                func=self._check_element_tool,
                description="Check if a UI element exists on screen"
            ),
            Tool(
                name="extract_text",
                func=self._extract_text_tool,
                description="Extract text from a specific screen region"
            )
        ])
        
        return tools
    
    def _wait_tool(self, seconds: str) -> str:
        """Wait for specified seconds"""
        import time
        try:
            time.sleep(float(seconds))
            return f"Waited for {seconds} seconds"
        except Exception as e:
            return f"Error waiting: {str(e)}"
    
    def _check_element_tool(self, element_description: str) -> str:
        """Check if element exists using UI-TARS"""
        # This would use UI-TARS to analyze current screen
        return f"Checking for element: {element_description}"
    
    def _extract_text_tool(self, region: str) -> str:
        """Extract text from screen region"""
        # This would use OCR or UI-TARS text extraction
        return f"Extracting text from region: {region}"
    
    def _create_agent(self) -> AgentExecutor:
        """Create the enhanced agent"""
        from langchain.agents import create_structured_chat_agent
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert UI automation agent with computer vision capabilities.
            
Your goal is to help users automate GUI tasks by:
1. Analyzing screenshots to understand the current UI state
2. Planning sequences of actions to achieve goals
3. Executing actions like clicking, typing, and navigating
4. Verifying that actions were successful

Always think step-by-step and verify each action before proceeding to the next."""),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000
        )
        
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=memory,
            verbose=True,
            max_iterations=15,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def automate_workflow(self, workflow_description: str) -> Dict[str, Any]:
        """Execute a complete automation workflow"""
        
        result = self.agent.invoke({
            "input": workflow_description
        })
        
        return {
            "workflow": workflow_description,
            "output": result["output"],
            "intermediate_steps": result.get("intermediate_steps", []),
            "success": True
        }


class GameAutomationAgent:
    """Specialized agent for game automation using UI-TARS"""
    
    def __init__(self, endpoint_name: str, game_name: str):
        self.endpoint_name = endpoint_name
        self.game_name = game_name
        self.agent = self._create_game_agent()
        
    def _create_game_agent(self):
        """Create agent specialized for game automation"""
        from langchain.llms import OpenAI
        from langchain.prompts import PromptTemplate
        
        # Game-specific prompt
        prompt = PromptTemplate(
            input_variables=["game_name", "objective", "current_state"],
            template="""You are an AI game player for {game_name}.

Objective: {objective}
Current State: {current_state}

Analyze the game state and determine the best next move. Consider:
1. Current score/progress
2. Available actions
3. Optimal strategy
4. Risk vs reward

Provide your analysis and recommended action."""
        )
        
        llm = OpenAI(temperature=0.2)  # Slightly more creative for games
        
        return create_ui_automation_agent(
            endpoint_name=self.endpoint_name,
            base_llm=llm,
            verbose=True
        )
    
    def play_turn(self, screenshot_path: str, objective: str) -> Dict[str, Any]:
        """Play one turn of the game"""
        
        task = f"""Analyze the game screenshot at {screenshot_path} for {self.game_name}.
        The objective is: {objective}
        Determine and execute the best next move."""
        
        result = self.agent.run(task)
        
        return {
            "screenshot": screenshot_path,
            "objective": objective,
            "action_taken": result
        }


class WebAutomationAgent:
    """Agent specialized for web browser automation"""
    
    def __init__(self, endpoint_name: str, browser: str = "chrome"):
        self.endpoint_name = endpoint_name
        self.browser = browser
        self.agent = self._create_web_agent()
        
    def _create_web_agent(self):
        """Create agent for web automation with Selenium integration"""
        from langchain.llms import OpenAI
        from langchain.tools import Tool
        
        # Add web-specific tools
        web_tools = [
            Tool(
                name="navigate_url",
                func=self._navigate_to_url,
                description="Navigate to a specific URL"
            ),
            Tool(
                name="fill_form",
                func=self._fill_form_field,
                description="Fill a form field with specified text"
            ),
            Tool(
                name="click_button",
                func=self._click_button,
                description="Click a button by its text or ID"
            )
        ]
        
        # Combine with UI-TARS tools
        all_tools = [
            UITARSTool(endpoint_name=self.endpoint_name),
            ScreenCaptureTool(),
            GUIActionTool()
        ] + web_tools
        
        return create_ui_automation_agent(
            endpoint_name=self.endpoint_name,
            base_llm=OpenAI(temperature=0),
            verbose=True
        )
    
    def _navigate_to_url(self, url: str) -> str:
        """Navigate browser to URL"""
        # Implement with Selenium
        return f"Navigated to {url}"
    
    def _fill_form_field(self, field_info: str) -> str:
        """Fill form field"""
        # Parse field_info and use Selenium
        return f"Filled form field: {field_info}"
    
    def _click_button(self, button_info: str) -> str:
        """Click button"""
        # Use Selenium to click
        return f"Clicked button: {button_info}"
    
    def automate_web_task(self, task_description: str, starting_url: str) -> Dict[str, Any]:
        """Automate a complete web task"""
        
        full_task = f"""Starting at {starting_url}, complete this task: {task_description}
        
        Use UI-TARS to analyze the page, identify elements, and perform necessary actions."""
        
        result = self.agent.run(full_task)
        
        return {
            "task": task_description,
            "starting_url": starting_url,
            "result": result
        }


# Example usage functions
def example_multimodal_automation():
    """Example of advanced multi-modal automation"""
    
    agent = MultiModalAgent(
        endpoint_name="ui-tars-endpoint-123456",
        llm_provider="openai"
    )
    
    # Complex workflow example
    workflow = """
    1. Take a screenshot of the desktop
    2. Find and open the Settings application
    3. Navigate to Display settings
    4. Check current screen resolution
    5. If resolution is not 1920x1080, change it
    6. Apply the changes and close Settings
    """
    
    result = agent.automate_workflow(workflow)
    print(f"Workflow completed: {result}")


def example_game_automation():
    """Example of game automation"""
    
    game_agent = GameAutomationAgent(
        endpoint_name="ui-tars-endpoint-123456",
        game_name="2048"
    )
    
    # Play one turn
    result = game_agent.play_turn(
        screenshot_path="game_screenshot.png",
        objective="Reach 2048 tile"
    )
    print(f"Game move: {result}")


def example_web_automation():
    """Example of web automation"""
    
    web_agent = WebAutomationAgent(
        endpoint_name="ui-tars-endpoint-123456",
        browser="chrome"
    )
    
    # Automate web task
    result = web_agent.automate_web_task(
        task_description="Search for 'LangChain documentation' and open the first result",
        starting_url="https://www.google.com"
    )
    print(f"Web automation result: {result}")


if __name__ == "__main__":
    print("Advanced LangChain UI Automation Examples")
    print("========================================")
    print("\nAvailable Examples:")
    print("1. MultiModalAgent - Advanced automation with multiple LLM providers")
    print("2. GameAutomationAgent - Specialized for game playing")
    print("3. WebAutomationAgent - Web browser automation")
    print("\nRun the example functions to see them in action!")
