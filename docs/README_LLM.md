# LLM-Powered Banking Transaction Chat Client

This is an advanced version of the banking transaction chat client that uses a local LLM running on LM Studio with tool calling capabilities for superior natural language understanding.

## 🚀 Features

### **Advanced Natural Language Processing**
- **Tool Calling**: LLM automatically selects the right tools based on your query
- **Context Awareness**: Understands complex queries with multiple parameters
- **Intelligent Responses**: Provides conversational, helpful responses
- **Date Intelligence**: Automatically converts relative dates ("last month", "this year")

### **Supported Query Types**
- **Transaction Search**: Find specific transactions with complex criteria
- **Spending Analysis**: Get summaries and breakdowns of your spending
- **Natural Conversations**: Ask follow-up questions and get contextual responses

## 🔧 Setup Requirements

### **1. LM Studio Setup**
1. **Download and Install**: [LM Studio](https://lmstudio.ai/)
2. **Load a Model**: Choose a model that supports tool calling (recommended: Llama 3.1, Mistral, or similar)
3. **Start Server**: Run LM Studio server on `http://localhost:1234`
4. **Enable Tools**: Make sure tool calling is enabled in the model settings

### **2. Recommended Models**
- **Llama 3.1 8B Instruct** (good balance of speed and capability)
- **Mistral 7B Instruct** (fast and efficient)
- **CodeLlama 13B Instruct** (excellent for structured queries)
- **Qwen 2.5 7B Instruct** (great tool calling support)

### **3. LM Studio Configuration**
```json
{
  "temperature": 0.1,
  "max_tokens": 1000,
  "tools_enabled": true,
  "tool_choice": "auto"
}
```

## 🎯 Usage

### **Starting the LLM Client**
```bash
python run_llm_chat.py
```

Or directly:
```bash
streamlit run chat_client_llm.py --server.port 8502
```

### **Example Queries**

#### **Simple Searches**
- *"Show me all my Starbucks purchases from last month"*
- *"Find grocery transactions over $50"*
- *"What did I spend at Amazon this year?"*

#### **Complex Queries**
- *"Find all dining expenses in San Francisco between $20 and $100 from the last 3 months"*
- *"Show me gas station purchases on my credit card from last week"*
- *"What are my biggest entertainment expenses this year?"*

#### **Analysis Requests**
- *"Give me a spending summary for the last quarter"*
- *"How much did I spend on utilities this month?"*
- *"What's my average grocery spending per month?"*

#### **Conversational Follow-ups**
- *"Show me more details about those transactions"*
- *"What about the same period last year?"*
- *"Can you break that down by category?"*

## 🔍 How It Works

### **1. Query Processing**
```
User Query → LLM Analysis → Tool Selection → Function Execution → Response Generation
```

### **2. Tool Definitions**
The LLM has access to two main tools:

#### **search_transactions**
- Searches for specific transactions
- Supports all search parameters (merchant, category, amount, dates, etc.)
- Returns detailed transaction data

#### **get_transaction_summary**
- Provides spending analytics
- Generates category breakdowns
- Creates time-based summaries

### **3. Intelligent Parameter Extraction**
The LLM automatically:
- **Converts dates**: "last month" → actual date range
- **Maps categories**: "coffee" → "dining" category
- **Handles amounts**: "over $50" → amount_min: 50
- **Resolves locations**: "SF" → "San Francisco"

## 🎨 Interface Features

### **Sidebar Controls**
- **LM Studio URL Configuration**: Change the LLM server URL
- **Connection Testing**: Test LLM and Elasticsearch connections
- **Example Queries**: Click-to-try sample questions

### **Rich Visualizations**
- **Transaction Tables**: Sortable, filterable data tables
- **Spending Charts**: Pie charts for category breakdowns
- **Trend Analysis**: Line charts for spending over time
- **Interactive Plots**: Zoom, filter, and explore your data

### **Debug Information**
- **Tool Calls**: See which tools the LLM selected
- **Parameters**: View extracted search parameters
- **Response Times**: Monitor LLM and search performance

## 🔧 Troubleshooting

### **LLM Connection Issues**
```bash
# Check if LM Studio is running
curl http://localhost:1234/v1/models

# Test tool calling capability
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local-model","messages":[{"role":"user","content":"test"}],"tools":[]}'
```

### **Common Issues**

#### **"Cannot connect to LM Studio"**
- Ensure LM Studio is running on port 1234
- Check if a model is loaded
- Verify tool calling is enabled

#### **"No response from LLM"**
- Check model supports tool calling
- Increase timeout settings
- Try a different model

#### **"Tool execution failed"**
- Verify Elasticsearch connection
- Check transaction data exists
- Review parameter formats

### **Performance Optimization**
- **Use smaller models** for faster responses (7B vs 13B)
- **Adjust temperature** (0.1 for consistent results)
- **Limit max_tokens** to reduce response time
- **Enable GPU acceleration** in LM Studio

## 🆚 Comparison: LLM vs Regex Client

| Feature | Regex Client | LLM Client |
|---------|-------------|------------|
| **Query Understanding** | Pattern matching | Natural language |
| **Flexibility** | Limited patterns | Unlimited expressions |
| **Context Awareness** | None | Full conversation context |
| **Date Handling** | Basic keywords | Intelligent parsing |
| **Follow-up Questions** | No | Yes |
| **Complex Queries** | Limited | Excellent |
| **Response Quality** | Template-based | Conversational |
| **Setup Complexity** | Simple | Requires LLM |
| **Performance** | Fast | Depends on model |
| **Offline Capability** | Yes | Yes (local LLM) |

## 🎯 Best Practices

### **Query Tips**
- **Be specific**: "Show me Starbucks purchases last month" vs "coffee"
- **Use natural language**: Ask as you would ask a human
- **Provide context**: "Compare this month to last month"
- **Ask follow-ups**: "Show me more details" or "What about gas stations?"

### **Model Selection**
- **Speed priority**: Use 7B models (Mistral 7B, Llama 3.1 8B)
- **Accuracy priority**: Use 13B+ models (CodeLlama 13B, Llama 3.1 70B)
- **Balance**: Llama 3.1 8B Instruct is recommended

### **Performance Tuning**
- **Temperature**: 0.1-0.3 for consistent results
- **Max tokens**: 500-1000 for most queries
- **Tool choice**: "auto" for best tool selection
- **Context length**: Use models with 8K+ context for long conversations

## 🔮 Future Enhancements

- **Multi-turn conversations** with memory
- **Custom tool creation** for specific analysis
- **Voice input/output** integration
- **Automated insights** and recommendations
- **Integration with other financial tools**
- **Custom model fine-tuning** on your transaction patterns
