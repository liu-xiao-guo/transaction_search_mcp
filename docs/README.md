# Banking Transaction Search MCP Server

An MCP (Model Context Protocol) server for searching personal banking transactions in Elasticsearch using FastMCP. This server provides powerful search capabilities optimized for natural language queries from LLMs.

## Features

- **Flexible Transaction Search**: Search by description, merchant, category, location, amount ranges, dates, and more
- **Transaction Summaries**: Get spending analytics and category breakdowns
- **NLP-Optimized**: Designed to work seamlessly with LLMs for natural language transaction queries
- **Comprehensive Data Model**: Includes all relevant transaction fields with proper Elasticsearch mapping
- **Test Data Generation**: Automated script to create realistic test transactions

## Installation

1. **Clone or create the project directory**:
   ```bash
   mkdir transaction_search_mcp
   cd transaction_search_mcp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Elasticsearch configuration
   ```

4. **Start Elasticsearch** (if running locally):
   ```bash
   # Using Docker
   docker run -d --name elasticsearch \
     -p 9200:9200 -p 9300:9300 \
     -e "discovery.type=single-node" \
     -e "xpack.security.enabled=false" \
     elasticsearch:8.11.1
   ```

5. **Set up the index and test data**:
   ```bash
   python setup_elasticsearch.py
   ```

## Usage

### Starting the MCP Server

```bash
python server.py
```

The server will start and be available for MCP client connections.

### Available Tools

#### 1. `search_transactions`
Search for banking transactions with flexible criteria.

**Parameters** (all optional):
- `description`: Search in transaction description/memo
- `merchant`: Merchant or payee name
- `category`: Transaction category (groceries, gas, dining, etc.)
- `location`: Transaction location (city, state, or address)
- `amount_min`/`amount_max`: Amount range filters
- `date_from`/`date_to`: Date range (YYYY-MM-DD format)
- `account_type`: Account type (checking, savings, credit)
- `transaction_type`: Transaction type (debit, credit, transfer)
- `tags`: Transaction tags
- `limit`: Maximum results (default: 10)

**Example queries**:
```python
# Find all Starbucks purchases
search_transactions(merchant="Starbucks")

# Find grocery purchases over $50 in the last month
search_transactions(
    category="groceries",
    amount_min=50.0,
    date_from="2024-06-01"
)

# Find all transactions in San Francisco
search_transactions(location="San Francisco")
```

#### 2. `get_transaction_summary`
Get summary statistics and spending analytics.

**Parameters** (all optional):
- `date_from`/`date_to`: Date range for summary
- `category`: Filter by category
- `account_type`: Filter by account type

**Returns**:
- Total spending amount
- Average transaction amount
- Transaction count
- Spending by category
- Spending by account type
- Monthly spending trends

#### 3. `health_check`
Check Elasticsearch connection and index status.

## Transaction Data Model

Each transaction includes the following fields:

### Core Transaction Fields
- `transaction_id`: Unique transaction identifier
- `account_id`: Account identifier
- `account_type`: checking, savings, credit
- `transaction_date`: When the transaction occurred
- `posted_date`: When the transaction was posted
- `amount`: Transaction amount (negative for expenses)
- `currency`: Currency code (e.g., USD)

### Description Fields
- `description`: Main transaction description
- `memo`: Additional memo/notes
- `reference`: Reference number
- `merchant`: Merchant/payee name

### Categorization
- `category`: Primary category (groceries, dining, gas, etc.)
- `subcategory`: More specific categorization
- `transaction_type`: debit, credit, transfer, fee, interest
- `tags`: Custom tags for organization

### Location Information
- `location.address`: Street address
- `location.city`: City name
- `location.state`: State/province
- `location.country`: Country code
- `location.postal_code`: ZIP/postal code
- `location.coordinates`: GPS coordinates

### Additional Fields
- `balance_after`: Account balance after transaction
- `is_pending`: Whether transaction is still pending
- `is_recurring`: Whether this is a recurring transaction
- `created_at`/`updated_at`: Timestamps

## Natural Language Query Examples

This MCP server is designed to work with LLMs for natural language queries:

- "Show me all my coffee purchases from last month"
- "Find grocery spending over $100 in San Francisco"
- "What did I spend on gas stations in December?"
- "Show me all recurring utility payments"
- "Find all Amazon purchases between $50 and $200"
- "What are my dining expenses for this quarter?"

## Configuration

### Environment Variables

- `ELASTICSEARCH_HOST`: Elasticsearch host (default: localhost:9200)
- `ELASTICSEARCH_USERNAME`: Username for basic authentication (optional)
- `ELASTICSEARCH_PASSWORD`: Password for basic authentication (optional)
- `ELASTICSEARCH_API_KEY`: API key for authentication (optional, recommended)
- `ELASTICSEARCH_INDEX`: Index name (default: banking_transactions)

### Authentication Options

**Option 1: API Key Authentication (Recommended)**
```bash
ELASTICSEARCH_HOST=your-cluster.es.region.aws.cloud.es.io:443
ELASTICSEARCH_API_KEY=your-base64-encoded-api-key
```

**Option 2: Username/Password Authentication**
```bash
ELASTICSEARCH_HOST=your-cluster.es.region.aws.cloud.es.io:443
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your-password
```

**Note**: API key authentication takes precedence over username/password if both are provided.

## Development

### Adding Custom Fields

To add new transaction fields:

1. Update the `create_index_mapping()` function in `setup_elasticsearch.py`
2. Modify the `generate_test_data()` function to include the new fields
3. Update the search logic in `server.py` if needed
4. Recreate the index: `python setup_elasticsearch.py`

### Testing

The setup script creates 500 realistic test transactions with:
- Various merchants and categories
- Realistic amounts based on category
- Geographic distribution across major US cities
- Mix of expenses and income
- Recurring transactions for utilities/subscriptions
- Random tags and metadata

## Troubleshooting

### Connection Issues
- Ensure Elasticsearch is running and accessible
- Check firewall settings for port 9200
- Verify authentication credentials if using security

### Search Issues
- Use the `health_check` tool to verify index status
- Check Elasticsearch logs for errors
- Ensure index mapping is correct

### Performance
- For large datasets, consider increasing `number_of_shards`
- Use date range filters to limit search scope
- Implement pagination for large result sets

## License

This project is open source and available under the MIT License.
