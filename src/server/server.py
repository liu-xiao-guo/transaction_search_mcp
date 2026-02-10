#!/usr/bin/env python3
"""
MCP Server for Personal Banking Transaction Search in Elasticsearch
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from elasticsearch import Elasticsearch
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("Transaction Search Server")

# Elasticsearch configuration
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")
ES_API_KEY = os.getenv("ELASTICSEARCH_API_KEY", "")
ES_INDEX = os.getenv("ELASTICSEARCH_INDEX", "banking_transactions")

# Initialize Elasticsearch client
def get_es_client():
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

class TransactionSearchParams(BaseModel):
    """Parameters for transaction search"""
    description: Optional[str] = Field(None, description="Search in transaction description/memo")
    merchant: Optional[str] = Field(None, description="Merchant or payee name")
    category: Optional[str] = Field(None, description="Transaction category (e.g., groceries, gas, dining)")
    location: Optional[str] = Field(None, description="Transaction location (city, state, or address)")
    amount_min: Optional[float] = Field(None, description="Minimum transaction amount")
    amount_max: Optional[float] = Field(None, description="Maximum transaction amount")
    date_from: Optional[str] = Field(None, description="Start date (YYYY-MM-DD format)")
    date_to: Optional[str] = Field(None, description="End date (YYYY-MM-DD format)")
    account_type: Optional[str] = Field(None, description="Account type (checking, savings, credit)")
    transaction_type: Optional[str] = Field(None, description="Transaction type (debit, credit, transfer)")
    tags: Optional[List[str]] = Field(None, description="Transaction tags")
    limit: Optional[int] = Field(10, description="Maximum number of results to return")

@mcp.tool()
def search_transactions(params: TransactionSearchParams) -> Dict[str, Any]:
    """
    Search for banking transactions in Elasticsearch with flexible criteria.
    All search parameters are optional and can be combined for precise filtering.
    """
    try:
        es = get_es_client()
        
        # Build Elasticsearch query
        query = {"bool": {"must": []}}
        
        # Text search fields with fuzzy matching
        if params.description:
            query["bool"]["must"].append({
                "multi_match": {
                    "query": params.description,
                    "fields": ["description^2", "memo", "reference"],
                    "fuzziness": "AUTO",
                    "operator": "and"
                }
            })
        
        if params.merchant:
            query["bool"]["must"].append({
                "match": {
                    "merchant": {
                        "query": params.merchant,
                        "fuzziness": "AUTO"
                    }
                }
            })
        
        if params.category:
            query["bool"]["must"].append({
                "match": {
                    "category": {
                        "query": params.category,
                        "fuzziness": "AUTO"
                    }
                }
            })
        
        if params.location:
            query["bool"]["must"].append({
                "multi_match": {
                    "query": params.location,
                    "fields": ["location.city", "location.state", "location.address", "location.country"],
                    "fuzziness": "AUTO"
                }
            })
        
        # Exact match fields
        if params.account_type:
            query["bool"]["must"].append({
                "term": {"account_type.keyword": params.account_type.lower()}
            })
        
        if params.transaction_type:
            query["bool"]["must"].append({
                "term": {"transaction_type.keyword": params.transaction_type.lower()}
            })
        
        # Range queries
        if params.amount_min is not None or params.amount_max is not None:
            range_query = {}
            if params.amount_min is not None:
                range_query["gte"] = params.amount_min
            if params.amount_max is not None:
                range_query["lte"] = params.amount_max
            query["bool"]["must"].append({
                "range": {"amount": range_query}
            })
        
        if params.date_from or params.date_to:
            range_query = {}
            if params.date_from:
                range_query["gte"] = params.date_from
            if params.date_to:
                range_query["lte"] = params.date_to
            query["bool"]["must"].append({
                "range": {"transaction_date": range_query}
            })
        
        # Tags search
        if params.tags:
            query["bool"]["must"].append({
                "terms": {"tags.keyword": params.tags}
            })
        
        # If no filters specified, match all
        if not query["bool"]["must"]:
            query = {"match_all": {}}
        
        # Execute search
        response = es.search(
            index=ES_INDEX,
            body={
                "query": query,
                "sort": [{"transaction_date": {"order": "desc"}}],
                "size": params.limit or 10
            }
        )
        
        # Format results
        transactions = []
        for hit in response["hits"]["hits"]:
            transaction = hit["_source"]
            transaction["_score"] = hit["_score"]
            transaction["_id"] = hit["_id"]
            transactions.append(transaction)
        
        return {
            "success": True,
            "total_hits": response["hits"]["total"]["value"],
            "returned_count": len(transactions),
            "transactions": transactions,
            "query_info": {
                "search_params": params.dict(exclude_none=True),
                "elasticsearch_query": query
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "transactions": []
        }

@mcp.tool()
def get_transaction_summary(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    category: Optional[str] = None,
    account_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get summary statistics for transactions within specified criteria.
    Provides spending patterns, category breakdowns, and account summaries.
    """
    try:
        es = get_es_client()
        
        # Build base query
        query = {"bool": {"must": []}}
        
        if date_from or date_to:
            range_query = {}
            if date_from:
                range_query["gte"] = date_from
            if date_to:
                range_query["lte"] = date_to
            query["bool"]["must"].append({
                "range": {"transaction_date": range_query}
            })
        
        if category:
            query["bool"]["must"].append({
                "match": {"category": category}
            })
        
        if account_type:
            query["bool"]["must"].append({
                "term": {"account_type.keyword": account_type.lower()}
            })
        
        if not query["bool"]["must"]:
            query = {"match_all": {}}
        
        # Aggregation query
        aggs = {
            "total_amount": {"sum": {"field": "amount"}},
            "avg_amount": {"avg": {"field": "amount"}},
            "transaction_count": {"value_count": {"field": "amount"}},
            "by_category": {
                "terms": {"field": "category.keyword", "size": 20},
                "aggs": {"total_spent": {"sum": {"field": "amount"}}}
            },
            "by_account": {
                "terms": {"field": "account_type.keyword"},
                "aggs": {"total_amount": {"sum": {"field": "amount"}}}
            },
            "by_month": {
                "date_histogram": {
                    "field": "transaction_date",
                    "calendar_interval": "month"
                },
                "aggs": {"monthly_total": {"sum": {"field": "amount"}}}
            }
        }
        
        response = es.search(
            index=ES_INDEX,
            body={
                "query": query,
                "size": 0,
                "aggs": aggs
            }
        )
        
        # Format aggregation results
        aggregations = response["aggregations"]
        
        return {
            "success": True,
            "summary": {
                "total_amount": round(aggregations["total_amount"]["value"] or 0, 2),
                "average_amount": round(aggregations["avg_amount"]["value"] or 0, 2),
                "transaction_count": aggregations["transaction_count"]["value"],
                "spending_by_category": [
                    {
                        "category": bucket["key"],
                        "total_spent": round(bucket["total_spent"]["value"], 2),
                        "transaction_count": bucket["doc_count"]
                    }
                    for bucket in aggregations["by_category"]["buckets"]
                ],
                "spending_by_account": [
                    {
                        "account_type": bucket["key"],
                        "total_amount": round(bucket["total_amount"]["value"], 2),
                        "transaction_count": bucket["doc_count"]
                    }
                    for bucket in aggregations["by_account"]["buckets"]
                ],
                "monthly_spending": [
                    {
                        "month": bucket["key_as_string"],
                        "total_spent": round(bucket["monthly_total"]["value"], 2),
                        "transaction_count": bucket["doc_count"]
                    }
                    for bucket in aggregations["by_month"]["buckets"]
                ]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def health_check() -> Dict[str, Any]:
    """Check the health of the Elasticsearch connection and index."""
    try:
        es = get_es_client()
        
        # Check cluster health
        cluster_health = es.cluster.health()
        
        # Check if index exists
        index_exists = es.indices.exists(index=ES_INDEX)
        
        # Get index stats if it exists
        index_stats = None
        doc_count = 0
        if index_exists:
            index_stats = es.indices.stats(index=ES_INDEX)
            doc_count = index_stats["indices"][ES_INDEX]["total"]["docs"]["count"]
        
        return {
            "success": True,
            "elasticsearch_status": cluster_health["status"],
            "index_exists": bool(index_exists),
            "index_name": ES_INDEX,
            "document_count": doc_count,
            "cluster_name": cluster_health["cluster_name"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    mcp.run()
