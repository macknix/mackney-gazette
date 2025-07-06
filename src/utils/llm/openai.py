"""
Module for interacting with the OpenAI API.
"""
import os
import json
from openai import OpenAI
from pathlib import Path
from typing import List, Dict, Any, Optional

print("Initializing OpenAI module...")

def load_api_key(credentials_file: str = None) -> str:
    """
    Load the OpenAI API key from a credentials file or environment variable.
    
    Args:
        credentials_file: Optional path to a credentials file. If None, will try to use the
                          default credentials file or environment variable.
                          
    Returns:
        The API key as a string
        
    Raises:
        FileNotFoundError: If the credentials file doesn't exist
        KeyError: If the API key is not found in the credentials file or environment
    """
    # Try to get from environment variable first
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        print("Found API key in environment variable")
        return api_key
    
    # If no environment variable, try to load from credentials file
    if credentials_file is None:
        # Default to project root credentials file
        root_dir = Path(__file__).parent.parent.parent.parent
        credentials_file = root_dir / 'credentials'
    
    print(f"Looking for credentials file at: {credentials_file}")
    
    # Read credentials file
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(f"Credentials file not found: {credentials_file}")
    
    try:
        with open(credentials_file, 'r') as file:
            creds = json.load(file)
        
        if 'openai_api_key' not in creds:
            raise KeyError("OpenAI API key not found in credentials file")
        
        print("Found API key in credentials file")
        return creds['openai_api_key']
    except json.JSONDecodeError:
        # The file might be in env var format instead of JSON
        with open(credentials_file, 'r') as file:
            for line in file:
                if line.startswith('export OPENAI_API_KEY='):
                    # Extract the key from the export statement
                    api_key = line.strip().split('=')[1].strip('"\'')
                    print("Found API key in credentials file (env format)")
                    return api_key
        
        raise KeyError("OpenAI API key not found in credentials file")

def initialize_openai_client(api_key: str = None) -> OpenAI:
    """
    Initialize the OpenAI client with the provided API key.
    
    Args:
        api_key: The OpenAI API key. If None, will attempt to load it.
        
    Returns:
        An OpenAI client instance
    """
    if api_key is None:
        api_key = load_api_key()
    
    return OpenAI(api_key=api_key)

def call_openai_api(
    system_prompt: str,
    messages: List[Dict[str, str]],
    model_args: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> str:
    """
    Call the OpenAI API with the given system prompt, messages, and model arguments.
    
    Args:
        system_prompt: The system prompt to set the behavior of the model
        messages: A list of message dictionaries with 'role' and 'content' keys.
                  Each dictionary should have format {'role': 'user' or 'assistant', 'content': 'message text'}
        model_args: Optional dictionary of model arguments like temperature, max_tokens, etc.
        api_key: Optional API key to use for this call. If None, will attempt to load from
                 environment variables or credentials file.
                   
    Returns:
        The generated response text
        
    Raises:
        Exception: If there's an error with the API call
    """
    try:
        # Initialize the API client with the provided API key or load it from credentials
        client = initialize_openai_client(api_key)
        
        # Set default model arguments if not provided
        if model_args is None:
            model_args = {
                'model': 'gpt-4o-mini',
                'temperature': 0.7,
                'max_tokens': 1024,
                'top_p': 0.95
            }
        
        # Get the model name and remove it from model_args
        model_name = model_args.pop('model', 'gpt-4o-mini')
        
        # Extract message parameters
        temperature = model_args.pop('temperature', 0.7)
        max_tokens = model_args.pop('max_tokens', 1024)  # Different name in OpenAI API
        top_p = model_args.pop('top_p', 0.95)
        
        # Prepare the conversation messages
        chat_messages = []
        
        # Add the system message if provided
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
            print(f"Using system prompt: {system_prompt}")
        
        # Process messages - they should already be in the right format
        for message in messages:
            role = message.get('role', '').lower()
            content = message.get('content', '')
            
            # Validate role
            if role not in ['user', 'assistant', 'system']:
                print(f"Warning: Invalid role '{role}', defaulting to 'user'")
                role = 'user'
                
            chat_messages.append({"role": role, "content": content})
        
        # If no messages were provided, add a default user message
        if not chat_messages or (len(chat_messages) == 1 and chat_messages[0]["role"] == "system"):
            chat_messages.append({"role": "user", "content": "Hello"})
        
        # Send the chat completion request
        response = client.chat.completions.create(
            model=model_name,
            messages=chat_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            **model_args  # Include any remaining model arguments
        )
        
        # Return the text response
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        raise

def simple_openai_prompt(
    prompt: str,
    system_instruction: str = "You are a helpful AI assistant.",
    model_args: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> str:
    """
    A simplified interface for sending a single prompt to OpenAI.
    
    Args:
        prompt: The user prompt to send
        system_instruction: The system prompt that defines the AI's behavior
        model_args: Optional dictionary of model arguments
        api_key: Optional API key to use for this call. If None, will attempt to load from
                 environment variables or credentials file.
        
    Returns:
        The generated response text
    """
    messages = [{'role': 'user', 'content': prompt}]  # Single user message in dictionary format
    print(f"Sending prompt: '{prompt[:50]}...' with system instruction")
    return call_openai_api(system_instruction, messages, model_args, api_key)

if __name__ == "__main__":
    # Example usage
    print("\n=== TESTING OPENAI API ===")
    
    # Set up a test prompt
    system = "You are a skilled news journalist for the Mackney Gazette newspaper."
    prompt = "Write a short headline for a story about local weather."
    
    print(f"System prompt: {system}")
    print(f"User prompt: {prompt}")
    print("\nSending request to OpenAI API...")
    
    try:
        # Set some model arguments for testing
        test_args = {
            'model': 'gpt-4o-mini',  # Using gpt-4o-mini model as specified
            'temperature': 0.7
        }
        
        # Load API key for demonstration
        api_key = load_api_key()
        print(f"Using API key: {api_key[:8]}..." if api_key else "No API key provided, will load from environment/credentials")
        
        # Test simple_openai_prompt with explicit API key
        print("\nTesting simple_openai_prompt with explicit API key:")
        response1 = simple_openai_prompt(prompt, system, test_args, api_key)
        print("\nOpenAI response:")
        print("=" * 50)
        print(response1)
        print("=" * 50)
        
        # Test call_openai_api with multiple messages, letting it load the API key
        print("\nTesting call_openai_api with conversation (loading API key automatically):")
        messages = [
            {'role': 'user', 'content': 'Write a headline for a story about local weather'},
            {'role': 'assistant', 'content': 'Storm Clouds Gather as Weekend Approaches'},
            {'role': 'user', 'content': 'Now write a headline about a community festival'}
        ]
        response2 = call_openai_api(system, messages, test_args)  # No API key provided
        print("\nOpenAI response to conversation:")
        print("=" * 50)
        print(response2)
        print("=" * 50)
        
        print("\nAPI calls successful!")
    except Exception as e:
        print(f"Failed to get response: {e}")
