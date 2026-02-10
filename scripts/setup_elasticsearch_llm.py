#!/usr/bin/env python3
"""
Enhanced script to create Elasticsearch index mapping and populate with test data
for banking transactions using LM Studio for realistic data generation.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from random import choice, uniform, randint, sample
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from typing import List, Dict, Any
import time

# Load environment variables
load_dotenv()

# Elasticsearch configuration
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")
ES_API_KEY = os.getenv("ELASTICSEARCH_API_KEY", "")
ES_INDEX = os.getenv("ELASTICSEARCH_INDEX", "banking_transactions")

# LM Studio configuration
LM_STUDIO_HOST = os.getenv("LM_STUDIO_HOST", "http://localhost:1234")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "")  # Will use default model if not specified

def get_es_client():
    """Initialize Elasticsearch client"""
    # For cloud instances, use proper certificate verification
    # verify_certs = "cloud.es.io" in ES_HOST or "elastic-cloud.com" in ES_HOST
    verify_certs = False
    
    if ES_API_KEY:
        return Elasticsearch(
            [ES_HOST],
            api_key=ES_API_KEY,
            verify_certs=verify_certs
        )
    elif ES_USERNAME and ES_PASSWORD:
        return Elasticsearch(
            [ES_HOST],
            basic_auth=(ES_USERNAME, ES_PASSWORD),
            verify_certs=verify_certs
        )
    else:
        return Elasticsearch([ES_HOST], verify_certs=verify_certs)

def create_index_mapping():
    """Create the index with proper mapping for banking transactions"""
    
    mapping = {
        "mappings": {
            "properties": {
                "transaction_id": {
                    "type": "keyword"
                },
                "account_id": {
                    "type": "keyword"
                },
                "account_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "transaction_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
                },
                "posted_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
                },
                "amount": {
                    "type": "double"
                },
                "currency": {
                    "type": "keyword"
                },
                "description": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "memo": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "reference": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "merchant": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "category": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "subcategory": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "transaction_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "location": {
                    "properties": {
                        "address": {
                            "type": "text"
                        },
                        "city": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "state": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "country": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "postal_code": {
                            "type": "keyword"
                        },
                        "coordinates": {
                            "type": "geo_point"
                        }
                    }
                },
                "tags": {
                    "type": "keyword"
                },
                "balance_after": {
                    "type": "double"
                },
                "is_pending": {
                    "type": "boolean"
                },
                "is_recurring": {
                    "type": "boolean"
                },
                "created_at": {
                    "type": "date",
                    "format": "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
                },
                "updated_at": {
                    "type": "date",
                    "format": "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
                }
            }
        }
    }
    
    return mapping

class LMStudioClient:
    """Client for interacting with LM Studio API"""
    
    def __init__(self, host: str = "http://localhost:1234", model: str = ""):
        self.host = host.rstrip('/')
        self.model = model
        self.session = requests.Session()
        
    def test_connection(self) -> bool:
        """Test if LM Studio is running and accessible"""
        try:
            response = self.session.get(f"{self.host}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_transaction_data(self, category: str, amount: float, location: str, date: str) -> Dict[str, Any]:
        """Generate realistic transaction data using LM Studio"""
        
        prompt = f"""Generate a realistic banking transaction for the following parameters:
Category: {category}
Amount: ${abs(amount):.2f}
Location: {location}
Date: {date}

Please provide a JSON response with the following fields:
- merchant: A realistic merchant name for this category and location
- description: A realistic transaction description as it would appear on a bank statement
- memo: A brief memo or note about the transaction
- subcategory: A specific subcategory within {category}
- tags: An array of 1-3 relevant tags for this transaction

Make it realistic and varied. For example:
- Coffee shops should have realistic names like "Blue Bottle Coffee" or "Local Grounds Cafe"
- Gas stations should include brand names and location details
- Restaurants should have creative but believable names
- Online purchases should reflect realistic e-commerce patterns

Respond only with valid JSON, no additional text."""

        try:
            response = self.session.post(
                f"{self.host}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that generates realistic banking transaction data. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 300,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Try to parse JSON from the response
                try:
                    # Remove any markdown code blocks if present
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()
                    
                    return json.loads(content)
                except json.JSONDecodeError:
                    print(f"⚠️  Failed to parse JSON response: {content}")
                    return None
            else:
                print(f"⚠️  LM Studio API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️  Error calling LM Studio: {str(e)}")
            return None

def generate_fallback_data(category: str, amount: float, location: str) -> Dict[str, Any]:
    """Generate fallback transaction data when LM Studio is not available"""
    
    fallback_merchants = {
        "groceries": ["Safeway", "Whole Foods", "Kroger", "Trader Joe's", "Local Market"],
        "dining": ["McDonald's", "Starbucks", "Olive Garden", "Local Bistro", "Pizza Palace"],
        "gas": ["Shell", "Chevron", "BP", "Exxon", "Mobil"],
        "shopping": ["Target", "Walmart", "Amazon", "Best Buy", "Local Store"],
        "entertainment": ["Netflix", "Spotify", "AMC Theaters", "Steam", "Apple Music"],
        "utilities": ["PG&E", "Electric Co", "Water Dept", "Gas Company", "City Utilities"],
        "transportation": ["Uber", "Lyft", "Metro Transit", "Parking Meter", "Taxi Co"],
        "healthcare": ["CVS Pharmacy", "Walgreens", "Medical Center", "Dental Office", "Clinic"]
    }
    
    subcategories = {
        "groceries": ["supermarket", "organic", "convenience"],
        "dining": ["fast_food", "restaurant", "coffee", "delivery"],
        "gas": ["fuel", "car_wash"],
        "shopping": ["retail", "online", "electronics"],
        "entertainment": ["streaming", "movies", "games"],
        "utilities": ["electricity", "water", "internet"],
        "transportation": ["rideshare", "parking", "transit"],
        "healthcare": ["pharmacy", "medical", "dental"]
    }
    
    merchant = choice(fallback_merchants.get(category, ["Generic Merchant"]))
    subcategory = choice(subcategories.get(category, [category]))
    
    return {
        "merchant": merchant,
        "description": f"{merchant} - {subcategory}",
        "memo": f"Purchase at {merchant}",
        "subcategory": subcategory,
        "tags": [category, subcategory] if subcategory != category else [category]
    }

def generate_test_data_with_llm(num_transactions: int = 500) -> List[Dict[str, Any]]:
    """Generate realistic test banking transaction data using LM Studio"""
    
    # Initialize LM Studio client
    llm_client = LMStudioClient(LM_STUDIO_HOST, LM_STUDIO_MODEL)
    use_llm = llm_client.test_connection()
    
    if use_llm:
        print("✅ Connected to LM Studio - using AI for realistic transaction generation")
    else:
        print("⚠️  LM Studio not available - using fallback data generation")
    
    # Base data for generation
    categories = [
        "groceries", "dining", "gas", "shopping", "entertainment", "utilities",
        "healthcare", "transportation", "travel", "subscriptions", "cash_withdrawal",
        "insurance", "phone", "internet", "clothing", "electronics", "home_improvement"
    ]
    
    cities = [
        ("San Francisco", "CA", "US", "94102"),
        ("New York", "NY", "US", "10001"),
        ("Los Angeles", "CA", "US", "90210"),
        ("Chicago", "IL", "US", "60601"),
        ("Seattle", "WA", "US", "98101"),
        ("Austin", "TX", "US", "73301"),
        ("Boston", "MA", "US", "02101"),
        ("Denver", "CO", "US", "80202")
    ]
    
    account_types = ["checking", "savings", "credit"]
    transaction_types = ["debit", "credit", "transfer", "fee", "interest"]
    
    transactions = []
    base_date = datetime.now() - timedelta(days=365)
    
    print(f"🔄 Generating {num_transactions} realistic transactions...")
    
    for i in range(num_transactions):
        if i % 50 == 0:
            print(f"   Generated {i}/{num_transactions} transactions...")
        
        transaction_date = base_date + timedelta(days=randint(0, 365))
        posted_date = transaction_date + timedelta(days=randint(0, 3))
        
        category = choice(categories)
        city, state, country, postal_code = choice(cities)
        account_type = choice(account_types)
        transaction_type = choice(transaction_types)
        
        # Generate amount based on category
        if category in ["groceries", "dining"]:
            amount = round(uniform(5.0, 150.0), 2)
        elif category == "gas":
            amount = round(uniform(25.0, 80.0), 2)
        elif category in ["shopping", "electronics"]:
            amount = round(uniform(20.0, 500.0), 2)
        elif category == "utilities":
            amount = round(uniform(50.0, 300.0), 2)
        elif category == "cash_withdrawal":
            amount = choice([20, 40, 60, 80, 100, 200])
        else:
            amount = round(uniform(10.0, 200.0), 2)
        
        # Make some transactions negative (expenses) and some positive (income/refunds)
        if transaction_type == "credit" or randint(1, 10) == 1:
            amount = abs(amount)
        else:
            amount = -abs(amount)
        
        # Generate transaction details using LM Studio or fallback
        if use_llm and randint(1, 3) == 1:  # Use LLM for 1/3 of transactions to avoid rate limits
            llm_data = llm_client.generate_transaction_data(
                category, amount, f"{city}, {state}", transaction_date.strftime("%Y-%m-%d")
            )
            time.sleep(0.1)  # Small delay to avoid overwhelming the API
        else:
            llm_data = None
        
        if llm_data:
            merchant = llm_data.get("merchant", "Unknown Merchant")
            description = llm_data.get("description", f"{merchant} - {category}")
            memo = llm_data.get("memo", f"Purchase at {merchant}")
            subcategory = llm_data.get("subcategory", category)
            tags = llm_data.get("tags", [category])
        else:
            fallback_data = generate_fallback_data(category, amount, f"{city}, {state}")
            merchant = fallback_data["merchant"]
            description = fallback_data["description"]
            memo = fallback_data["memo"]
            subcategory = fallback_data["subcategory"]
            tags = fallback_data["tags"]
        
        # Add some additional contextual tags
        if "coffee" in merchant.lower() or "starbucks" in merchant.lower():
            tags.append("coffee")
        if "gas" in merchant.lower() or category == "gas":
            tags.append("fuel")
        if randint(1, 5) == 1:
            tags.append("business")
        if randint(1, 8) == 1:
            tags.append("tax_deductible")
        
        # Remove duplicates from tags
        tags = list(set(tags))
        
        transaction = {
            "transaction_id": f"txn_{i+1:06d}",
            "account_id": f"acc_{randint(1, 5):03d}",
            "account_type": account_type,
            "transaction_date": transaction_date.strftime("%Y-%m-%d"),
            "posted_date": posted_date.strftime("%Y-%m-%d"),
            "amount": amount,
            "currency": "USD",
            "description": description,
            "memo": memo,
            "reference": f"REF{randint(100000, 999999)}",
            "merchant": merchant,
            "category": category,
            "subcategory": subcategory,
            "transaction_type": transaction_type,
            "location": {
                "city": city,
                "state": state,
                "country": country,
                "postal_code": postal_code,
                "coordinates": {
                    "lat": round(uniform(25.0, 49.0), 6),
                    "lon": round(uniform(-125.0, -66.0), 6)
                }
            },
            "tags": tags,
            "balance_after": round(uniform(100.0, 5000.0), 2),
            "is_pending": randint(1, 20) == 1,
            "is_recurring": category in ["utilities", "subscriptions", "insurance"],
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        }
        
        transactions.append(transaction)
    
    print(f"✅ Generated {len(transactions)} transactions")
    return transactions

def main():
    """Main function to set up Elasticsearch index and data"""
    try:
        es = get_es_client()
        
        print(f"Connecting to Elasticsearch at {ES_HOST}...")
        
        # Check connection
        if not es.ping():
            print("❌ Could not connect to Elasticsearch")
            return
        
        print("✅ Connected to Elasticsearch")
        
        # Delete index if it exists
        if es.indices.exists(index=ES_INDEX):
            print(f"🗑️  Deleting existing index: {ES_INDEX}")
            es.indices.delete(index=ES_INDEX)
        
        # Create index with mapping
        print(f"📋 Creating index: {ES_INDEX}")
        mapping = create_index_mapping()
        es.indices.create(index=ES_INDEX, body=mapping)
        print("✅ Index created successfully")
        
        # Generate and index test data
        print("🤖 Generating AI-enhanced test transaction data...")
        transactions = generate_test_data_with_llm()
        
        print(f"📤 Indexing {len(transactions)} transactions...")
        
        # Bulk index the data
        from elasticsearch.helpers import bulk, BulkIndexError
        
        def doc_generator():
            for i, transaction in enumerate(transactions):
                yield {
                    "_index": ES_INDEX,
                    "_id": transaction["transaction_id"],
                    "_source": transaction
                }
        
        try:
            success, failed = bulk(es, doc_generator(), chunk_size=50, request_timeout=60)
            print(f"✅ Successfully indexed {success} transactions")
            
            if failed:
                print(f"❌ Failed to index {len(failed)} transactions")
                for i, error in enumerate(failed[:3]):
                    print(f"Error {i+1}: {error}")
                    
        except BulkIndexError as e:
            print(f"❌ Bulk indexing error: {str(e)}")
            print("First few errors:")
            for i, error in enumerate(e.errors[:5]):
                print(f"Error {i+1}: {error}")
            success = 0
        
        # Refresh index to make data searchable
        es.indices.refresh(index=ES_INDEX)
        
        # Get index stats
        stats = es.indices.stats(index=ES_INDEX)
        doc_count = stats["indices"][ES_INDEX]["total"]["docs"]["count"]
        
        print(f"📊 Index '{ES_INDEX}' now contains {doc_count} documents")
        print("🎉 Setup completed successfully!")
        
        # Show some sample queries
        print("\n📝 Sample search queries you can try:")
        print("- Search for coffee shop transactions")
        print("- Find all grocery purchases over $50")
        print("- Look for gas station visits in San Francisco")
        print("- Find streaming service subscriptions")
        print("- Search for business-related expenses")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
