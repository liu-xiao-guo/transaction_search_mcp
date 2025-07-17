# Transaction Search MCP Server

A Model Context Protocol (MCP) server for searching personal banking transactions using Elasticsearch, with both basic and LLM-powered chat clients.

## 📁 Project Structure

```
transaction_search_mcp/
├── src/                          # Source code
│   ├── server/                   # MCP server implementation
│   │   └── server.py            # Main MCP server with transaction search tools
│   └── clients/                 # Client applications
│       ├── chat_client.py       # Basic Streamlit chat interface
│       └── chat_client_llm.py   # Enhanced LLM-powered chat client
├── scripts/                     # Setup and utility scripts
│   ├── setup_elasticsearch.py   # Basic Elasticsearch setup with test data
│   ├── setup_elasticsearch_llm.py # Enhanced setup with realistic test data
│   ├── run_chat.py             # Launch basic chat client
│   └── run_llm_chat.py         # Launch LLM-powered chat client
├── tests/                       # Test files
│   └── test_server.py          # Comprehensive server tests
├── docs/                        # Documentation
│   ├── README.md               # Basic implementation docs
│   └── README_LLM.md           # LLM-enhanced version docs
├── requirements/                # Dependencies
│   ├── requirements.txt        # Server dependencies
│   └── client_requirements.txt # Client dependencies
├── .env                        # Environment variables (not in git)
├── .env.example               # Environment template
└── .gitignore                 # Git ignore rules
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# - Elasticsearch URL and credentials
# - OpenAI API key (for LLM client)
```

### 2. Install Dependencies
```bash
# Server dependencies
pip install -r requirements/requirements.txt

# Client dependencies (for chat interfaces)
pip install -r requirements/client_requirements.txt
```

### 3. Setup Elasticsearch
```bash
# Basic setup with 500 test transactions
python scripts/setup_elasticsearch.py

# OR enhanced setup with more realistic data
python scripts/setup_elasticsearch_llm.py
```

### 4. Run the Server
```bash
# Start MCP server
python src/server/server.py
```

### 5. Launch Chat Client
```bash
# Basic chat interface
python scripts/run_chat.py

# OR LLM-powered interface (recommended)
python scripts/run_llm_chat.py
```

## 🔧 Components

### MCP Server (`src/server/`)
- **server.py**: Main MCP server with three tools:
  - `search_transactions`: Flexible transaction search
  - `get_transaction_summary`: Spending analytics
  - `health_check`: Server status

### Chat Clients (`src/clients/`)
- **chat_client.py**: Basic Streamlit interface for transaction queries
- **chat_client_llm.py**: Enhanced interface with:
  - LLM-powered natural language processing
  - Categorized example queries
  - Advanced loading indicators
  - Improved UX and responsiveness

### Setup Scripts (`scripts/`)
- **setup_elasticsearch.py**: Creates index and generates basic test data
- **setup_elasticsearch_llm.py**: Enhanced setup with realistic transactions
- **run_chat.py**: Launches basic chat client
- **run_llm_chat.py**: Launches LLM-powered client

## 🧪 Testing

```bash
# Run comprehensive tests
python tests/test_server.py
```

## 📖 Documentation

- **docs/README.md**: Basic implementation details
- **docs/README_LLM.md**: LLM-enhanced version documentation

## 🔑 Features

- **Natural Language Queries**: "Show me coffee purchases from last month"
- **Flexible Search**: Filter by merchant, category, amount, location, dates
- **Spending Analytics**: Category breakdowns and summaries
- **Realistic Test Data**: 500+ transactions with merchants, locations, tags
- **Multiple Interfaces**: Choose between basic or LLM-powered chat
- **Comprehensive Testing**: Full test suite for all functionality

## 🛠️ Development

The project follows a clean architecture with separated concerns:
- Server logic in `src/server/`
- Client interfaces in `src/clients/`
- Utility scripts in `scripts/`
- Tests in `tests/`
- Documentation in `docs/`

This structure makes it easy to:
- Add new client interfaces
- Extend server functionality
- Maintain and test components independently
- Deploy different parts separately
