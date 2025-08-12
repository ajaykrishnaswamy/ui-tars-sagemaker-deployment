#!/usr/bin/env python3
"""
Test script for LangChain UI-TARS Agent
Demonstrates basic functionality without requiring actual deployment
"""

import os
from unittest.mock import Mock, patch
from langchain_ui_agent import (
    UITARSTool,
    ScreenCaptureTool,
    GUIActionTool,
    create_ui_automation_agent,
    UIAutomationChain
)


def test_ui_tars_tool():
    """Test UITARSTool functionality"""
    print("Testing UITARSTool...")
    
    # Mock the SageMaker runtime client
    with patch('boto3.client') as mock_client:
        mock_runtime = Mock()
        mock_runtime.invoke_endpoint.return_value = {
            'Body': Mock(read=lambda: b'{"generated_text": "I see a desktop with multiple application windows open."}')
        }
        mock_client.return_value = mock_runtime
        
        # Create tool
        tool = UITARSTool(endpoint_name="test-endpoint")
        
        # Test with mock image
        with patch.object(tool, '_encode_image', return_value="mock_base64_data"):
            result = tool.run(
                image_path="test_screenshot.png",
                question="What do you see on the screen?"
            )
            
        print(f"✅ UITARSTool Result: {result}")
        assert "desktop" in result.lower()


def test_screen_capture_tool():
    """Test ScreenCaptureTool functionality"""
    print("\nTesting ScreenCaptureTool...")
    
    tool = ScreenCaptureTool()
    
    # Mock pyautogui
    with patch('pyautogui.screenshot') as mock_screenshot:
        mock_img = Mock()
        mock_img.save = Mock()
        mock_screenshot.return_value = mock_img
        
        result = tool.run()
        print(f"✅ ScreenCaptureTool Result: {result}")
        assert "Screenshot saved" in result


def test_gui_action_tool():
    """Test GUIActionTool functionality"""
    print("\nTesting GUIActionTool...")
    
    tool = GUIActionTool()
    
    # Mock pyautogui actions
    with patch('pyautogui.click') as mock_click:
        result = tool.run(
            action="click",
            coordinates=(100, 200)
        )
        print(f"✅ GUIActionTool Click Result: {result}")
        assert "Clicked at" in result
        mock_click.assert_called_once_with(100, 200)
    
    with patch('pyautogui.typewrite') as mock_type:
        result = tool.run(
            action="type",
            text="Hello World"
        )
        print(f"✅ GUIActionTool Type Result: {result}")
        assert "Typed:" in result
        mock_type.assert_called_once_with("Hello World")


def test_create_agent():
    """Test agent creation"""
    print("\nTesting Agent Creation...")
    
    # Mock LLM
    from langchain.llms.fake import FakeListLLM
    
    responses = [
        "I need to take a screenshot first to see what's on the screen.",
        "I can see the desktop. Now I'll analyze what applications are available.",
        "I found the Settings application. I'll click on it now.",
        "The Settings window is now open."
    ]
    
    fake_llm = FakeListLLM(responses=responses)
    
    # Create agent with mocked tools
    with patch('boto3.client'):
        agent = create_ui_automation_agent(
            endpoint_name="test-endpoint",
            base_llm=fake_llm,
            verbose=False
        )
        
    print("✅ Agent created successfully")
    print(f"   - Tools: {[tool.name for tool in agent.tools]}")
    print(f"   - Max iterations: {agent.max_iterations}")


def test_automation_chain():
    """Test UIAutomationChain"""
    print("\nTesting UIAutomationChain...")
    
    from langchain.llms.fake import FakeListLLM
    
    fake_llm = FakeListLLM(responses=["Task completed successfully"])
    
    with patch('boto3.client'):
        chain = UIAutomationChain(
            endpoint_name="test-endpoint",
            base_llm=fake_llm
        )
        
        # Test analyze_and_act
        result = chain.analyze_and_act("Open Settings application")
        print(f"✅ Chain Result: {result}")
        assert result["success"] == True


def demonstrate_agent_workflow():
    """Demonstrate a complete agent workflow"""
    print("\n" + "="*50)
    print("DEMONSTRATING COMPLETE WORKFLOW")
    print("="*50)
    
    # This is a demonstration of how the agent would work
    workflow_steps = [
        "1. Agent receives task: 'Open Settings and change display resolution'",
        "2. Agent takes screenshot of current desktop",
        "3. UI-TARS analyzes screenshot and identifies Settings icon",
        "4. Agent clicks on Settings icon at coordinates (x, y)",
        "5. Agent waits for Settings to open",
        "6. Agent takes new screenshot",
        "7. UI-TARS identifies Display settings option",
        "8. Agent clicks on Display settings",
        "9. Agent analyzes resolution options",
        "10. Agent selects desired resolution and applies changes"
    ]
    
    for step in workflow_steps:
        print(f"\n{step}")
    
    print("\n✅ Workflow demonstration complete!")


def main():
    """Run all tests"""
    print("🧪 Testing LangChain UI-TARS Agent Components")
    print("=" * 50)
    
    # Run individual component tests
    test_ui_tars_tool()
    test_screen_capture_tool()
    test_gui_action_tool()
    test_create_agent()
    test_automation_chain()
    
    # Demonstrate workflow
    demonstrate_agent_workflow()
    
    print("\n" + "="*50)
    print("✅ All tests completed successfully!")
    print("\nNext steps:")
    print("1. Deploy UI-TARS model to SageMaker")
    print("2. Set up environment variables")
    print("3. Run actual automation tasks")
    print("\nSee LANGCHAIN_AGENT_GUIDE.md for detailed instructions")


if __name__ == "__main__":
    main()
