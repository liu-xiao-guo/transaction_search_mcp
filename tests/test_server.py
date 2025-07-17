#!/usr/bin/env python3
"""
Test script for the Banking Transaction Search MCP Server
"""

import asyncio
import json
import sys
import os

# Add the project root to Python path so we can import from src
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.server.server import search_transactions, get_transaction_summary, health_check, TransactionSearchParams

async def test_health_check():
    """Test the health check functionality"""
    print("🔍 Testing health check...")
    result = health_check()
    print(f"Health check result: {json.dumps(result, indent=2)}")
    return result["success"]

async def test_basic_search():
    """Test basic transaction search"""
    print("\n🔍 Testing basic transaction search...")
    
    # Search for all transactions (no filters)
    params = TransactionSearchParams(limit=5)
    result = search_transactions(params)
    
    print(f"Found {result.get('total_hits', 0)} total transactions")
    print(f"Returned {result.get('returned_count', 0)} transactions")
    
    if result.get("transactions"):
        print("\nSample transaction:")
        sample = result["transactions"][0]
        print(f"- Date: {sample.get('transaction_date')}")
        print(f"- Merchant: {sample.get('merchant')}")
        print(f"- Amount: ${sample.get('amount')}")
        print(f"- Category: {sample.get('category')}")
        print(f"- Location: {sample.get('location', {}).get('city')}, {sample.get('location', {}).get('state')}")
    
    return result["success"]

async def test_merchant_search():
    """Test searching by merchant"""
    print("\n🔍 Testing merchant search (Starbucks)...")
    
    params = TransactionSearchParams(merchant="Starbucks", limit=3)
    result = search_transactions(params)
    
    print(f"Found {result.get('total_hits', 0)} Starbucks transactions")
    
    for i, transaction in enumerate(result.get("transactions", [])[:3]):
        print(f"{i+1}. {transaction.get('merchant')} - ${transaction.get('amount')} on {transaction.get('transaction_date')}")
    
    return result["success"]

async def test_category_search():
    """Test searching by category"""
    print("\n🔍 Testing category search (groceries)...")
    
    params = TransactionSearchParams(category="groceries", limit=3)
    result = search_transactions(params)
    
    print(f"Found {result.get('total_hits', 0)} grocery transactions")
    
    for i, transaction in enumerate(result.get("transactions", [])[:3]):
        print(f"{i+1}. {transaction.get('merchant')} - ${transaction.get('amount')} ({transaction.get('category')})")
    
    return result["success"]

async def test_amount_range_search():
    """Test searching by amount range"""
    print("\n🔍 Testing amount range search ($50-$100)...")
    
    params = TransactionSearchParams(amount_min=50.0, amount_max=100.0, limit=3)
    result = search_transactions(params)
    
    print(f"Found {result.get('total_hits', 0)} transactions between $50-$100")
    
    for i, transaction in enumerate(result.get("transactions", [])[:3]):
        amount = transaction.get('amount', 0)
        print(f"{i+1}. {transaction.get('merchant')} - ${abs(amount):.2f}")
    
    return result["success"]

async def test_location_search():
    """Test searching by location"""
    print("\n🔍 Testing location search (San Francisco)...")
    
    params = TransactionSearchParams(location="San Francisco", limit=3)
    result = search_transactions(params)
    
    print(f"Found {result.get('total_hits', 0)} transactions in San Francisco")
    
    for i, transaction in enumerate(result.get("transactions", [])[:3]):
        location = transaction.get('location', {})
        print(f"{i+1}. {transaction.get('merchant')} in {location.get('city')}, {location.get('state')}")
    
    return result["success"]

async def test_complex_search():
    """Test complex search with multiple filters"""
    print("\n🔍 Testing complex search (dining in CA, last 6 months, >$20)...")
    
    params = TransactionSearchParams(
        category="dining",
        location="CA",
        amount_min=20.0,
        date_from="2024-01-01",
        limit=3
    )
    result = search_transactions(params)
    
    print(f"Found {result.get('total_hits', 0)} matching transactions")
    
    for i, transaction in enumerate(result.get("transactions", [])[:3]):
        location = transaction.get('location', {})
        amount = abs(transaction.get('amount', 0))
        print(f"{i+1}. {transaction.get('merchant')} - ${amount:.2f} in {location.get('city')}, {location.get('state')}")
    
    return result["success"]

async def test_transaction_summary():
    """Test transaction summary functionality"""
    print("\n📊 Testing transaction summary...")
    
    result = get_transaction_summary()
    
    if result.get("success"):
        summary = result["summary"]
        print(f"Total transactions: {summary.get('transaction_count', 0)}")
        print(f"Total amount: ${summary.get('total_amount', 0):.2f}")
        print(f"Average amount: ${summary.get('average_amount', 0):.2f}")
        
        print("\nTop spending categories:")
        for category in summary.get("spending_by_category", [])[:5]:
            print(f"- {category['category']}: ${abs(category['total_spent']):.2f} ({category['transaction_count']} transactions)")
        
        print("\nSpending by account type:")
        for account in summary.get("spending_by_account", []):
            print(f"- {account['account_type']}: ${abs(account['total_amount']):.2f}")
    
    return result["success"]

async def test_date_range_summary():
    """Test transaction summary with date range"""
    print("\n📊 Testing transaction summary for last 30 days...")
    
    from datetime import datetime, timedelta
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    result = get_transaction_summary(date_from=date_from)
    
    if result.get("success"):
        summary = result["summary"]
        print(f"Last 30 days - Total transactions: {summary.get('transaction_count', 0)}")
        print(f"Last 30 days - Total amount: ${summary.get('total_amount', 0):.2f}")
    
    return result["success"]

async def main():
    """Run all tests"""
    print("🚀 Starting MCP Server Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Basic Search", test_basic_search),
        ("Merchant Search", test_merchant_search),
        ("Category Search", test_category_search),
        ("Amount Range Search", test_amount_range_search),
        ("Location Search", test_location_search),
        ("Complex Search", test_complex_search),
        ("Transaction Summary", test_transaction_summary),
        ("Date Range Summary", test_date_range_summary),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            if success:
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your MCP server is ready to use.")
    else:
        print("⚠️  Some tests failed. Check your Elasticsearch setup and try again.")

if __name__ == "__main__":
    asyncio.run(main())
