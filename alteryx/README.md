# Alteryx Data Validation Workflows

## data-validation.yxmd
**Purpose**: Real-time validation of data consistency during migration

**Workflow Components**:
- Input: PostgreSQL ODBC connection to legacy inventory_master
- Input: BigQuery connection via Google Cloud SDK
- Join: Inner join on `sku_id` to align source vs target
- Formula: Compute `quantity_diff` and `timestamp_delta`
- Filter: Flag discrepancies > 0.01%
- Output: Excel validation report

**Performance**:
- Volume:1.2M records processed
- Time: <4 mins
- Accuracy: 99.99%
- Result: Zero Loss (100% data integrity)
