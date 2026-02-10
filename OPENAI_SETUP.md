# OpenAI Setup Guide

The chat client has been successfully converted to use OpenAI's API instead of LM Studio.

## Changes Made

1. **Import Changes**: Replaced `requests` with `openai` library
2. **Class Initialization**: Now accepts `openai_api_key` and `openai_model` parameters instead of `lm_studio_url`
3. **LLM Call Method**: Uses OpenAI's Python SDK (`openai.OpenAI().chat.completions.create()`)
4. **UI Updates**: Sidebar now has OpenAI API key input and model selection

## Setup Instructions

### 1. Install Dependencies

The `openai` package is already in `requirements/client_requirements.txt`. Install it:

```bash
source .venv/bin/activate
pip install -r requirements/client_requirements.txt
```

### 2. Set Your OpenAI API Key

You have two options:

**Option A: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Option B: Through the UI**
- Enter your API key in the sidebar "OpenAI API Key" field
- Click "Update OpenAI Settings"

### 3. Run the Application

```bash
streamlit run src/clients/chat_client_llm_openai.py
```

## Supported Models

The application supports these OpenAI models:
- `gpt-4-turbo-preview` (default) - Best for complex queries
- `gpt-4` - High quality responses
- `gpt-3.5-turbo` - Faster and more cost-effective

You can select the model in the sidebar dropdown.

## Features

✅ Natural language transaction search using OpenAI function calling
✅ Spending summaries and analytics
✅ Interactive visualizations (charts, tables)
✅ Support for date ranges, categories, merchants, locations, amounts, etc.

## Testing the Connection

Use the "Test OpenAI Connection" button in the sidebar to verify your API key is working.

## Cost Considerations

- OpenAI charges per token used
- GPT-4 models are more expensive than GPT-3.5
- Consider using `gpt-3.5-turbo` for development/testing
- The application uses `temperature=0.1` and `max_tokens=1000` to control costs

## Example Queries

Try these examples:
- "Show me all my Starbucks purchases from last month"
- "What did I spend on groceries this year?"
- "Find all transactions over $100 in San Francisco"
- "Give me a spending summary for the last 3 months"
