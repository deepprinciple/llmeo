from unittest.mock import MagicMock, patch

import pytest
from llmeo import GPT4, Claude3, GPTo1, LLMConfig, LLMError


# Test LLMConfig
def test_llm_config_initialization():
    """Test basic LLMConfig initialization"""
    config = LLMConfig(
        openai_api_key="test-key",
        anthropic_api_key="test-key-2",
        temperature=0.7,
        top_p=0.9,
        max_tokens=2048,
    )
    assert config.openai_api_key == "test-key"
    assert config.anthropic_api_key == "test-key-2"
    assert config.temperature == 0.7
    assert config.top_p == 0.9
    assert config.max_tokens == 2048


def test_llm_config_from_yaml(mock_llm_config_file):
    """Test loading LLMConfig from YAML file"""
    config = LLMConfig.from_yaml(mock_llm_config_file)
    assert config.openai_api_key == "test-key-openai"
    assert config.anthropic_api_key == "test-key-anthropic"
    assert config.temperature == 0.5
    assert config.max_tokens == 4096


def test_llm_config_missing_file():
    """Test error handling for missing config file"""
    with pytest.raises(FileNotFoundError):
        LLMConfig.from_yaml("nonexistent_config.yaml")


@patch("openai.OpenAI")
def test_gpt4_creation(mock_openai, test_config):
    """Test GPT4 model creation"""
    model = GPT4(test_config)
    model.create()
    mock_openai.assert_called_once_with(api_key=test_config.openai_api_key)


def test_gpt4_creation_without_api_key(test_config):
    """Test GPT4 creation failure without API key"""
    test_config.openai_api_key = None
    model = GPT4(test_config)
    with pytest.raises(LLMError, match="OpenAI API key not found"):
        model.create()


@patch("openai.OpenAI")
def test_gpt4_successful_call(mock_openai, test_config):
    """Test successful GPT4 API call"""
    # Mock OpenAI client response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test response"
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    model = GPT4(test_config)
    model.create()
    response = model.call("Test prompt")

    assert response == "Test response"
    mock_client.chat.completions.create.assert_called_once()


def test_claude3_creation_without_api_key(test_config):
    """Test Claude3 creation failure without API key"""
    test_config.anthropic_api_key = None
    model = Claude3(test_config)
    with pytest.raises(LLMError, match="Anthropic API key not found"):
        model.create()


@patch("anthropic.Anthropic")
def test_claude3_successful_call(mock_anthropic, test_config):
    """Test successful Claude3 API call"""
    # Mock Anthropic client response
    mock_response = MagicMock()
    mock_response.content[0].text = "Test response"
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    model = Claude3(test_config)
    model.create()
    response = model.call("Test prompt")

    assert response == "Test response"
    mock_client.messages.create.assert_called_once()


@patch("openai.OpenAI")
def test_gpto1_different_models(mock_openai, test_config):
    """Test GPTo1 with different model variants"""
    models = ["o1-preview", "o1-mini"]
    for model_name in models:
        model = GPTo1(test_config, name=model_name)
        model.create()
        assert model.name == model_name

        # Mock response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = f"Response from {model_name}"
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.return_value = mock_response

        response = model.call("Test prompt")
        assert response == f"Response from {model_name}"


@patch("openai.OpenAI")
def test_gpto1_with_system_prompt(mock_openai, test_config):
    """Test GPTo1 with system prompt"""
    model = GPTo1(test_config)
    model.create()

    # Mock response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test response"
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.return_value = mock_response

    system_prompt = "You are a helpful assistant."
    response = model.call("Test prompt", system=system_prompt)

    # Verify that system prompt was included in the content
    call_args = mock_client.chat.completions.create.call_args[1]
    assert system_prompt in call_args["messages"][0]["content"]
