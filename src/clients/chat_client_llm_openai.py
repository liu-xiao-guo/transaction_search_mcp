#!/usr/bin/env python3
"""
LLM-Powered Chat Client for Banking Transaction Search MCP Server
Uses OpenAI API with function calling capabilities for natural language processing.
"""

import streamlit as st
import asyncio
import json
import openai
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path so we can import from src
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import the MCP server module to access the tools
import src.server.server as server_module
from src.server.server import TransactionSearchParams

# Access the underlying functions from the MCP tools
def search_transactions(params):
    """Wrapper to call the MCP tool function"""
    return server_module.search_transactions.fn(params)

def get_transaction_summary(**kwargs):
    """Wrapper to call the MCP tool function"""
    return server_module.get_transaction_summary.fn(**kwargs)

def health_check():
    """Wrapper to call the MCP tool function"""
    return server_module.health_check.fn()

# Configure Streamlit page
st.set_page_config(
    page_title="Banking Transaction Chat (LLM)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class LLMTransactionChatBot:
    """LLM-powered natural language interface for transaction search (OpenAI)"""
    
    def __init__(self, openai_api_key: Optional[str] = None, openai_model: str = "gpt-4-turbo-preview"):
        self.openai_api_key = openai_api_key or os.environ.get("OPEN_AI_KEY")
        self.openai_model = openai_model
        self.conversation_history = []
        
        # Define tools for the LLM
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_transactions",
                    "description": "Search for banking transactions with flexible criteria. All parameters are optional.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Search in transaction description/memo"
                            },
                            "merchant": {
                                "type": "string", 
                                "description": "Merchant or payee name (e.g., 'Starbucks', 'Amazon')"
                            },
                            "category": {
                                "type": "string",
                                "description": "Transaction category (e.g., 'groceries', 'gas', 'dining', 'entertainment', 'utilities')"
                            },
                            "location": {
                                "type": "string",
                                "description": "Transaction location (city, state, or address)"
                            },
                            "amount_min": {
                                "type": "number",
                                "description": "Minimum transaction amount"
                            },
                            "amount_max": {
                                "type": "number", 
                                "description": "Maximum transaction amount"
                            },
                            "date_from": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format"
                            },
                            "date_to": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format"
                            },
                            "account_type": {
                                "type": "string",
                                "description": "Account type: 'checking', 'savings', or 'credit'"
                            },
                            "transaction_type": {
                                "type": "string",
                                "description": "Transaction type: 'debit', 'credit', 'transfer', 'fee', or 'interest'"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Transaction tags to filter by"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 10)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_transaction_summary",
                    "description": "Get summary statistics and spending analytics for transactions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date_from": {
                                "type": "string",
                                "description": "Start date for summary in YYYY-MM-DD format"
                            },
                            "date_to": {
                                "type": "string", 
                                "description": "End date for summary in YYYY-MM-DD format"
                            },
                            "category": {
                                "type": "string",
                                "description": "Filter summary by category"
                            },
                            "account_type": {
                                "type": "string",
                                "description": "Filter summary by account type"
                            }
                        }
                    }
                }
            }
        ]
    
    def call_llm(self, user_message: str) -> Dict[str, Any]:
        """Call OpenAI LLM with function calling support"""
        
        if not self.openai_api_key:
            return {"error": "OpenAI API key not set. Please set OPEN_AI_KEY in your .env file."}
        
        system_prompt = """You are a helpful banking transaction assistant. You help users search and analyze their banking transactions.

Current date: {current_date}

When users ask about transactions, use the appropriate tools:
- Use search_transactions for finding specific transactions
- Use get_transaction_summary for spending analysis and summaries

For date references:
- "last month" = past 30 days from today
- "this month" = current month from 1st to today
- "last week" = past 7 days
- "this year" = January 1st of current year to today

Common categories: groceries, dining, gas, shopping, entertainment, utilities, healthcare, transportation, travel, subscriptions, insurance, phone, internet

Always provide helpful, conversational responses about the transaction data.""".format(
            current_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            # Create OpenAI client with explicit configuration
            import httpx
            client = openai.OpenAI(
                api_key=self.openai_api_key,
                http_client=httpx.Client(
                    timeout=30.0,
                    limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
                )
            )
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=1000
            )
            
            # Convert response to dict format
            return {
                "choices": [{
                    "message": {
                        "content": response.choices[0].message.content,
                        "tool_calls": [
                            {
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                            for tool_call in (response.choices[0].message.tool_calls or [])
                        ] if response.choices[0].message.tool_calls else []
                    }
                }]
            }
                
        except Exception as e:
            return {
                "error": f"OpenAI API error: {str(e)}"
            }
    
    def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return results"""
        
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        try:
            if function_name == "search_transactions":
                # Convert arguments to TransactionSearchParams
                search_params = TransactionSearchParams(**arguments)
                return search_transactions(search_params)
                
            elif function_name == "get_transaction_summary":
                return get_transaction_summary(**arguments)
                
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            return {"error": f"Error executing {function_name}: {str(e)}"}
    
    def process_query(self, user_message: str) -> Dict[str, Any]:
        """Process user query using LLM and execute any tool calls"""
        
        # Call LLM
        llm_response = self.call_llm(user_message)
        
        if "error" in llm_response:
            return {
                "type": "error",
                "content": llm_response["error"],
                "data": None
            }
        
        # Extract the response
        choice = llm_response.get("choices", [{}])[0]
        message = choice.get("message", {})
        
        # Check if LLM wants to use tools
        tool_calls = message.get("tool_calls", [])
        
        if tool_calls:
            # Execute tool calls
            results = []
            for tool_call in tool_calls:
                result = self.execute_tool_call(tool_call)
                results.append({
                    "function": tool_call["function"]["name"],
                    "arguments": json.loads(tool_call["function"]["arguments"]),
                    "result": result
                })
            
            return {
                "type": "tool_results",
                "content": message.get("content", ""),
                "data": results
            }
        else:
            # Regular text response
            return {
                "type": "text",
                "content": message.get("content", "No response from LLM"),
                "data": None
            }
    
    def format_tool_results(self, results: List[Dict[str, Any]]) -> str:
        """Format tool execution results for display"""
        
        formatted_response = ""
        
        for result in results:
            function_name = result["function"]
            function_result = result["result"]
            
            if function_name == "search_transactions":
                formatted_response += self.format_search_results(function_result)
            elif function_name == "get_transaction_summary":
                formatted_response += self.format_summary_results(function_result)
            
            formatted_response += "\n\n"
        
        return formatted_response.strip()
    
    def format_search_results(self, results: Dict[str, Any]) -> str:
        """Format search results for display"""
        if not results.get("success"):
            return f"❌ Search Error: {results.get('error', 'Unknown error')}"
        
        transactions = results.get("transactions", [])
        total_hits = results.get("total_hits", 0)
        
        if not transactions:
            return "No transactions found matching your criteria."
        
        response = f"🔍 **Found {total_hits} transactions** (showing top {len(transactions)}):\n\n"
        
        for i, txn in enumerate(transactions, 1):
            amount = txn.get("amount", 0)
            amount_str = f"${abs(amount):.2f}" if amount < 0 else f"+${amount:.2f}"
            
            location = txn.get("location", {})
            location_str = f"{location.get('city', '')}, {location.get('state', '')}" if location else ""
            
            response += f"**{i}. {txn.get('merchant', 'Unknown')}**\n"
            response += f"   • Amount: {amount_str}\n"
            response += f"   • Date: {txn.get('transaction_date', 'Unknown')}\n"
            response += f"   • Category: {txn.get('category', 'Unknown')}\n"
            if location_str.strip(", "):
                response += f"   • Location: {location_str}\n"
            response += f"   • Description: {txn.get('description', 'N/A')}\n\n"
        
        return response
    
    def format_summary_results(self, results: Dict[str, Any]) -> str:
        """Format summary results for display"""
        if not results.get("success"):
            return f"❌ Summary Error: {results.get('error', 'Unknown error')}"
        
        summary = results.get("summary", {})
        
        response = "📊 **Transaction Summary**\n\n"
        response += f"• **Total Transactions:** {summary.get('transaction_count', 0):,}\n"
        response += f"• **Total Amount:** ${abs(summary.get('total_amount', 0)):,.2f}\n"
        response += f"• **Average Amount:** ${abs(summary.get('average_amount', 0)):,.2f}\n\n"
        
        # Category breakdown
        categories = summary.get("spending_by_category", [])
        if categories:
            response += "**Top Spending Categories:**\n"
            for cat in categories[:5]:
                response += f"• {cat['category'].title()}: ${abs(cat['total_spent']):,.2f} ({cat['transaction_count']} transactions)\n"
            response += "\n"
        
        # Account breakdown
        accounts = summary.get("spending_by_account", [])
        if accounts:
            response += "**Spending by Account:**\n"
            for acc in accounts:
                response += f"• {acc['account_type'].title()}: ${abs(acc['total_amount']):,.2f}\n"
        
        return response

def process_and_display_query(prompt: str, chatbot):
    """Process a query and display the results"""
    
    # Process query using LLM
    result = chatbot.process_query(prompt)
    
    if result["type"] == "error":
        response = f"❌ {result['content']}"
        st.error(response)
        return response
        
    elif result["type"] == "tool_results":
        # Format and display tool results
        response = chatbot.format_tool_results(result["data"])
        st.markdown(response)
        
        # Create visualizations for tool results
        for tool_result in result["data"]:
            if tool_result["function"] == "search_transactions":
                results = tool_result["result"]
                if results.get("success") and results.get("transactions"):
                    transactions = results.get("transactions", [])
                    
                    # Convert to DataFrame for better display
                    df_data = []
                    for txn in transactions:
                        location = txn.get("location", {})
                        df_data.append({
                            "Date": txn.get("transaction_date", ""),
                            "Merchant": txn.get("merchant", ""),
                            "Amount": f"${abs(txn.get('amount', 0)):.2f}",
                            "Category": txn.get("category", ""),
                            "Location": f"{location.get('city', '')}, {location.get('state', '')}" if location else "",
                            "Description": txn.get("description", "")
                        })
                    
                    if df_data:
                        df = pd.DataFrame(df_data)
                        st.dataframe(df, use_container_width=True)
            
            elif tool_result["function"] == "get_transaction_summary":
                results = tool_result["result"]
                if results.get("success"):
                    summary = results.get("summary", {})
                    
                    # Category spending chart
                    categories = summary.get("spending_by_category", [])
                    if categories:
                        df_cat = pd.DataFrame(categories)
                        df_cat['total_spent'] = df_cat['total_spent'].abs()
                        
                        fig = px.pie(
                            df_cat.head(8), 
                            values='total_spent', 
                            names='category',
                            title="Spending by Category"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Monthly spending trend
                    monthly = summary.get("monthly_spending", [])
                    if monthly:
                        df_monthly = pd.DataFrame(monthly)
                        df_monthly['total_spent'] = df_monthly['total_spent'].abs()
                        
                        fig = px.line(
                            df_monthly, 
                            x='month', 
                            y='total_spent',
                            title="Monthly Spending Trend",
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        return response
    
    elif result["type"] == "text":
        response = result["content"]
        st.markdown(response)
        return response
    
    else:
        response = "🤔 I'm not sure how to help with that. Try asking about your transactions!"
        st.markdown(response)
        return response

def main():
    st.title("🤖 Banking Transaction Chat Assistant (OpenAI)")
    st.markdown("Ask me about your banking transactions - powered by OpenAI!")
    
    # Initialize chat bot
    if "llm_chatbot" not in st.session_state:
        st.session_state.llm_chatbot = LLMTransactionChatBot()
    
    if "llm_messages" not in st.session_state:
        st.session_state.llm_messages = []
    
    # Sidebar with settings and examples
    with st.sidebar:
        st.header("🔧 OpenAI Settings")
        
        # Display API key status
        if st.session_state.llm_chatbot.openai_api_key:
            st.success("✅ API key loaded from .env file")
        else:
            st.error("❌ API key not found. Please set OPEN_AI_KEY in .env file")
        
        # OpenAI Model selection
        openai_model = st.selectbox(
            "OpenAI Model",
            options=["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
            index=0,
            help="Select the OpenAI model to use"
        )
        
        if st.button("Update Model"):
            st.session_state.llm_chatbot.openai_model = openai_model
            st.success(f"Model updated to {openai_model}!")
        
        # Test OpenAI connection
        if st.button("Test OpenAI Connection"):
            if not st.session_state.llm_chatbot.openai_api_key:
                st.error("❌ Please set OPEN_AI_KEY in your .env file")
            else:
                try:
                    client = openai.OpenAI(api_key=st.session_state.llm_chatbot.openai_api_key)
                    models = client.models.list()
                    st.success("✅ Connected to OpenAI!")
                    st.info(f"📝 Using model: {st.session_state.llm_chatbot.openai_model}")
                except Exception as e:
                    st.error(f"❌ Cannot connect to OpenAI: {str(e)}")
        
        st.header("🔧 System Status")
        
        if st.button("Check Elasticsearch"):
            with st.spinner("Checking Elasticsearch connection..."):
                health = health_check()
                if health.get("success"):
                    st.success(f"✅ Connected to Elasticsearch")
                    st.info(f"📊 {health.get('document_count', 0)} transactions available")
                    st.info(f"🟢 Status: {health.get('elasticsearch_status', 'unknown')}")
                else:
                    st.error(f"❌ Connection failed: {health.get('error', 'Unknown error')}")
        
        st.header("💡 Example Queries")
        st.markdown("*Click any example below to try it out:*")
        
        # Organize examples by category
        example_categories = {
            "🛍️ Shopping & Merchants": [
                "Show me all my Starbucks purchases from last month",
                "Find all Amazon purchases between $20 and $50",
                "Show me all gas station purchases"
            ],
            "📊 Spending Analysis": [
                "What did I spend on groceries this year?",
                "Give me a spending summary for the last 3 months",
                "What are my biggest expenses this month?"
            ],
            "📍 Location & Amount Filters": [
                "Find all transactions over $100 in San Francisco",
                "Show me my dining expenses from last week"
            ]
        }
        
        for category, examples in example_categories.items():
            st.subheader(category)
            for example in examples:
                if st.button(f"💬 {example}", key=f"llm_example_{hash(example)}", use_container_width=True):
                    # Immediately add user message to chat history
                    st.session_state.llm_messages.append({"role": "user", "content": example})
                    with st.chat_message("user"):
                        st.markdown(example)
                    
                    # Process the query with OpenAI
                    with st.chat_message("assistant"):
                        with st.spinner("🤖 Processing with OpenAI... Understanding your query and searching transactions..."):
                            chatbot = st.session_state.llm_chatbot
                            response = process_and_display_query(example, chatbot)
                    
                    # Add assistant response to chat history
                    st.session_state.llm_messages.append({"role": "assistant", "content": response})
                    st.rerun()
            st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.llm_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Check if we need to process the last user message (from example button)
    if (len(st.session_state.llm_messages) > 0 and 
        st.session_state.llm_messages[-1]["role"] == "user" and
        not st.session_state.get("processing_last_message", False)):
        
        # Mark that we're processing this message to avoid reprocessing
        st.session_state.processing_last_message = True
        
        # Get the last user message
        last_message = st.session_state.llm_messages[-1]["content"]
        
        # Process the query with OpenAI and show spinner
        with st.chat_message("assistant"):
            with st.spinner("🤖 Processing with OpenAI... Understanding your query and searching transactions..."):
                chatbot = st.session_state.llm_chatbot
                response = process_and_display_query(last_message, chatbot)
        
        # Add assistant response to chat history
        st.session_state.llm_messages.append({"role": "assistant", "content": response})
        
        # Reset the processing flag
        st.session_state.processing_last_message = False
    
    # Chat input
    if prompt := st.chat_input("Ask about your transactions..."):
        # Add user message to chat history
        st.session_state.llm_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the query with OpenAI
        with st.chat_message("assistant"):
            with st.spinner("🤖 Processing with OpenAI... Understanding your query and searching transactions..."):
                chatbot = st.session_state.llm_chatbot
                response = process_and_display_query(prompt, chatbot)
        
        # Add assistant response to chat history
        st.session_state.llm_messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
