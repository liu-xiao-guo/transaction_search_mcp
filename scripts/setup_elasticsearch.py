#!/usr/bin/env python3
"""
Script to create Elasticsearch index mapping and populate with test data
for banking transactions.
"""

import os
import json
from datetime import datetime, timedelta
from random import choice, uniform, randint
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Elasticsearch configuration
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")
ES_API_KEY = os.getenv("ELASTICSEARCH_API_KEY", "")
ES_INDEX = os.getenv("ELASTICSEARCH_INDEX", "banking_transactions")

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
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "city": {
                            "type": "text",
                            "analyzer": "standard",
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
                            "type": "keyword"
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
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
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
                    "format": "yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
                },
                "updated_at": {
                    "type": "date",
                    "format": "yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
                }
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "standard": {
                        "type": "standard",
                        "stopwords": "_english_"
                    }
                }
            }
        }
    }
    
    return mapping

def generate_test_data():
    """Generate realistic test banking transaction data"""
    
    # Sample data for realistic transactions
    merchants = [
        "Starbucks", "McDonald's", "Walmart", "Target", "Amazon", "Shell Gas Station",
        "Chevron", "Safeway", "Whole Foods", "Home Depot", "Best Buy", "Apple Store",
        "Netflix", "Spotify", "Uber", "Lyft", "Airbnb", "Hotel Marriott",
        "Restaurant Olive Garden", "Pizza Hut", "Subway", "Chipotle", "Costco",
        "CVS Pharmacy", "Walgreens", "Bank of America ATM", "Chase ATM",
        "Electric Company PG&E", "Verizon Wireless", "Comcast Cable", "Insurance Co"
    ]
    
    categories = [
        "groceries", "dining", "gas", "shopping", "entertainment", "utilities",
        "healthcare", "transportation", "travel", "subscriptions", "cash_withdrawal",
        "insurance", "phone", "internet", "clothing", "electronics", "home_improvement"
    ]
    
    subcategories = {
        "groceries": ["supermarket", "organic", "convenience_store"],
        "dining": ["fast_food", "restaurant", "coffee", "delivery"],
        "gas": ["fuel", "car_wash"],
        "shopping": ["retail", "online", "department_store"],
        "entertainment": ["streaming", "movies", "games", "music"],
        "utilities": ["electricity", "water", "gas_utility"],
        "transportation": ["rideshare", "public_transit", "parking"],
        "travel": ["hotel", "flight", "rental_car"]
    }
    
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
    
    for i in range(500):  # Generate 500 test transactions
        transaction_date = base_date + timedelta(days=randint(0, 365))
        posted_date = transaction_date + timedelta(days=randint(0, 3))
        
        merchant = choice(merchants)
        category = choice(categories)
        subcategory = choice(subcategories.get(category, [category]))
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
        
        # Generate tags
        tags = []
        if "coffee" in merchant.lower() or category == "dining":
            tags.append("food")
        if "gas" in merchant.lower() or category == "gas":
            tags.append("transportation")
        if randint(1, 5) == 1:
            tags.append("business")
        if randint(1, 8) == 1:
            tags.append("tax_deductible")
        
        transaction = {
            "transaction_id": f"txn_{i+1:06d}",
            "account_id": f"acc_{randint(1, 5):03d}",
            "account_type": account_type,
            "transaction_date": transaction_date.strftime("%Y-%m-%d"),
            "posted_date": posted_date.strftime("%Y-%m-%d"),
            "amount": amount,
            "currency": "USD",
            "description": f"{merchant} - {subcategory}",
            "memo": f"Purchase at {merchant}",
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
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",  # Format with milliseconds
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"   # Format with milliseconds
        }
        
        transactions.append(transaction)
    
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
        print("🔄 Generating test transaction data...")
        transactions = generate_test_data()
        
        print(f"📤 Indexing {len(transactions)} transactions...")
        
        # Bulk index the data
        from elasticsearch.helpers import bulk, BulkIndexError
        
        def doc_generator():
            for i, transaction in enumerate(transactions):
                yield {
                    "_index": ES_INDEX,
                    "_id": transaction["transaction_id"],  # Use transaction_id as document ID
                    "_source": transaction
                }
        
        try:
            success, failed = bulk(es, doc_generator(), chunk_size=50, request_timeout=60)
            print(f"✅ Successfully indexed {success} transactions")
            
            if failed:
                print(f"❌ Failed to index {len(failed)} transactions")
                # Show first few errors for debugging
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
        print("- Search for Starbucks transactions")
        print("- Find all grocery purchases over $50")
        print("- Look for transactions in San Francisco")
        print("- Find all gas station purchases")
        print("- Search for recurring utility payments")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
