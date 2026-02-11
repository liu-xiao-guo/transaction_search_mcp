#!/usr/bin/env python3
"""
Chat Client for Banking Transaction Search MCP Server
A Streamlit-based chat interface that uses natural language to query transactions.
"""

import streamlit as st
import asyncio
import json
import re
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    page_title="Banking Transaction Chat",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TransactionChatBot:
    """Natural language interface for transaction search"""
    
    def __init__(self):
        self.conversation_history = []
    
    def parse_natural_language(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into search parameters"""
        query_lower = query.lower()
        params = {}
        
        # Extract merchants
        merchants = [
            "starbucks", "mcdonald's", "walmart", "target", "amazon", "shell", "chevron",
            "safeway", "whole foods", "home depot", "best buy", "apple", "netflix",
            "spotify", "uber", "lyft", "airbnb", "marriott", "olive garden", "pizza hut",
            "subway", "chipotle", "costco", "cvs", "walgreens"
        ]
        
        for merchant in merchants:
            if merchant in query_lower:
                params["merchant"] = merchant.title()
                break
        
        # Extract categories
        categories = {
            "coffee": "dining", "food": "dining", "restaurant": "dining", "dining": "dining",
            "grocery": "groceries", "groceries": "groceries", "supermarket": "groceries",
            "gas": "gas", "fuel": "gas", "gasoline": "gas",
            "shopping": "shopping", "retail": "shopping",
            "entertainment": "entertainment", "movie": "entertainment", "streaming": "entertainment",
            "utility": "utilities", "utilities": "utilities", "electric": "utilities",
            "transport": "transportation", "transportation": "transportation", "uber": "transportation",
            "travel": "travel", "hotel": "travel", "flight": "travel",
            "healthcare": "healthcare", "medical": "healthcare", "doctor": "healthcare",
            "insurance": "insurance",
            "phone": "phone", "internet": "internet"
        }
        
        for keyword, category in categories.items():
            if keyword in query_lower:
                params["category"] = category
                break
        
        # Extract locations
        locations = [
            "san francisco", "new york", "los angeles", "chicago", "seattle",
            "austin", "boston", "denver", "california", "ca", "new york", "ny",
            "texas", "tx", "washington", "wa"
        ]
        
        for location in locations:
            if location in query_lower:
                params["location"] = location.title()
                break
        
        # Extract amounts
        amount_patterns = [
            r"over \$?(\d+)", r"above \$?(\d+)", r"more than \$?(\d+)",
            r"under \$?(\d+)", r"below \$?(\d+)", r"less than \$?(\d+)",
            r"between \$?(\d+) and \$?(\d+)", r"\$?(\d+) to \$?(\d+)"
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if "over" in pattern or "above" in pattern or "more than" in pattern:
                    params["amount_min"] = float(match.group(1))
                elif "under" in pattern or "below" in pattern or "less than" in pattern:
                    params["amount_max"] = float(match.group(1))
                elif "between" in pattern or "to" in pattern:
                    params["amount_min"] = float(match.group(1))
                    params["amount_max"] = float(match.group(2))
                break
        
        # Extract time periods
        today = datetime.now()
        
        if "last week" in query_lower or "past week" in query_lower:
            params["date_from"] = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        elif "last month" in query_lower or "past month" in query_lower:
            params["date_from"] = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        elif "last 3 months" in query_lower or "past 3 months" in query_lower:
            params["date_from"] = (today - timedelta(days=90)).strftime("%Y-%m-%d")
        elif "last year" in query_lower or "past year" in query_lower:
            params["date_from"] = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        elif "this year" in query_lower:
            params["date_from"] = f"{today.year}-01-01"
        elif "this month" in query_lower:
            params["date_from"] = f"{today.year}-{today.month:02d}-01"
        
        # Extract specific months
        months = {
            "january": "01", "february": "02", "march": "03", "april": "04",
            "may": "05", "june": "06", "july": "07", "august": "08",
            "september": "09", "october": "10", "november": "11", "december": "12"
        }
        
        for month_name, month_num in months.items():
            if month_name in query_lower:
                year = today.year
                if "last" in query_lower and month_name in query_lower:
                    if int(month_num) > today.month:
                        year -= 1
                params["date_from"] = f"{year}-{month_num}-01"
                params["date_to"] = f"{year}-{month_num}-31"
                break
        
        # Extract account types
        if "checking" in query_lower:
            params["account_type"] = "checking"
        elif "savings" in query_lower:
            params["account_type"] = "savings"
        elif "credit" in query_lower:
            params["account_type"] = "credit"
        
        # Set default limit
        if "all" in query_lower or "everything" in query_lower:
            params["limit"] = 100
        else:
            params["limit"] = 10
        
        return params
    
    def determine_query_type(self, query: str) -> str:
        """Determine if user wants search results or summary"""
        query_lower = query.lower()
        
        summary_keywords = [
            "summary", "total", "sum", "how much", "spending", "spent",
            "breakdown", "analysis", "statistics", "stats", "overview"
        ]
        
        for keyword in summary_keywords:
            if keyword in query_lower:
                return "summary"
        
        return "search"
    
    def format_search_results(self, results: Dict[str, Any]) -> str:
        """Format search results for display"""
        if not results.get("success"):
            return f"❌ Error: {results.get('error', 'Unknown error')}"
        
        transactions = results.get("transactions", [])
        total_hits = results.get("total_hits", 0)
        
        if not transactions:
            return "No transactions found matching your criteria."
        
        response = f"Found {total_hits} transactions. Showing top {len(transactions)}:\n\n"
        
        for i, txn in enumerate(transactions, 1):
            amount = txn.get("amount", 0)
            amount_str = f"${abs(amount):.2f}" if amount < 0 else f"+${amount:.2f}"
            
            location = txn.get("location", {})
            location_str = f"{location.get('city', '')}, {location.get('state', '')}" if location else ""
            
            response += f"**{i}. {txn.get('merchant', 'Unknown')}**\n"
            response += f"   • Amount: {amount_str}\n"
            response += f"   • Date: {txn.get('transaction_date', 'Unknown')}\n"
            response += f"   • Category: {txn.get('category', 'Unknown')}\n"
            if location_str:
                response += f"   • Location: {location_str}\n"
            response += f"   • Description: {txn.get('description', 'N/A')}\n\n"
        
        return response
    
    def format_summary_results(self, results: Dict[str, Any]) -> str:
        """Format summary results for display"""
        if not results.get("success"):
            return f"❌ Error: {results.get('error', 'Unknown error')}"
        
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

def main():
    st.title("🏦 Banking Transaction Chat Assistant")
    st.markdown("Ask me about your banking transactions in natural language!")
    
    # Initialize chat bot
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = TransactionChatBot()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar with health check and examples
    with st.sidebar:
        st.header("🔧 System Status")
        
        if st.button("Check Connection"):
            with st.spinner("Checking Elasticsearch connection..."):
                health = health_check()
                if health.get("success"):
                    st.success(f"✅ Connected to Elasticsearch")
                    st.info(f"📊 {health.get('document_count', 0)} transactions available")
                    st.info(f"🟢 Status: {health.get('elasticsearch_status', 'unknown')}")
                else:
                    st.error(f"❌ Connection failed: {health.get('error', 'Unknown error')}")
        
        st.header("💡 Example Queries")
        examples = [
            "Show me all Starbucks purchases",
            "Find grocery spending over $50",
            "What did I spend on gas last month?",
            "Show transactions in San Francisco",
            "Give me a spending summary for this year",
            "Find all Amazon purchases between $20 and $100",
            "Show dining expenses from last week",
            "What are my utility payments?",
            "Find all credit card transactions over $200"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{hash(example)}"):
                st.session_state.messages.append({"role": "user", "content": example})
                st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your transactions..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the query
        with st.chat_message("assistant"):
            with st.spinner("Searching transactions..."):
                try:
                    chatbot = st.session_state.chatbot
                    
                    # Determine query type
                    query_type = chatbot.determine_query_type(prompt)
                    st.write(f"Debug: Query type detected as '{query_type}'")
                    
                    if query_type == "summary":
                        # Parse parameters for summary
                        params = chatbot.parse_natural_language(prompt)
                        st.write(f"Debug: Parsed parameters: {params}")
                        
                        summary_params = {}
                        if "date_from" in params:
                            summary_params["date_from"] = params["date_from"]
                        if "date_to" in params:
                            summary_params["date_to"] = params["date_to"]
                        if "category" in params:
                            summary_params["category"] = params["category"]
                        if "account_type" in params:
                            summary_params["account_type"] = params["account_type"]
                        
                        # Get summary
                        results = get_transaction_summary(**summary_params)
                        response = chatbot.format_summary_results(results)
                        
                        # Create visualizations if successful
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
                    
                    else:
                        # Parse parameters for search
                        params = chatbot.parse_natural_language(prompt)
                        st.write(f"Debug: Parsed parameters: {params}")
                        
                        search_params = TransactionSearchParams(**params)
                        
                        # Perform search
                        results = search_transactions(search_params)
                        response = chatbot.format_search_results(results)
                        
                        # Create transaction table if successful
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
                            
                            df = pd.DataFrame(df_data)
                            st.dataframe(df, use_container_width=True)
                    
                    st.markdown(response)
                    
                except Exception as e:
                    error_msg = f"❌ Error processing query: {str(e)}"
                    st.error(error_msg)
                    response = error_msg
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
