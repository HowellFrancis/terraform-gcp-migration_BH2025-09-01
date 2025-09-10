#!/usr/bin/env python3
"""
DATA INTEGRITY VALIDATION
Compares: PostgreSQL source [vs] BigQuery target
"""

import pandas as pd
import psycopg2
from google.cloud import bigquery
import logging

logging.basicConfig(level=logging.INFO)

class MigrationValidator:
    def __init__(self, postgres_conn: str, gcp_project: str):
        self.postgres_conn = postgres_conn
        self.bq_client = bigquery.Client(project=gcp_project)

    def validate_record_counts(self):
        """Compares record counts between TF source and GCP target"""
        pg_conn = psycopg2.connect(self.postgres_conn)
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("SELECT COUNT(*) FROM inventory_master")
        postgres_count = pg_cursor.fetchone()[0]
        pg_conn.close()

        bq_query = "SELECT COUNT(*) FROM `inventory_analytics_prod.inventory_master`"
        bq_result = self.bq_client.query(bq_query)
        bigquery_count = list(bq_result)[0][0]

        discrepancy = abs(postgres_count - bigquery_count)

        logging.info(f"Postgres: {postgres_count}, BigQuery: {bigquery_count}, Discrepancy: {discrepancy}")
        return {
            "postgres_records": postgres_count,
            "bigquery_records": bigquery_count,
            "discrepancy": discrepancy,
        }

    def validate_data_integrity(self, sample_size: int = 1000):
        """SAMPLE-BASED VALIDATION"""
        pg_query = f"""
        SELECT sku_id, quantity, last_updated
        FROM inventory_master
        ORDER BY RANDOM()
        LIMIT {sample_size}
        """
        pg_df = pd.read_sql(pg_query, self.postgres_conn)

        accuracy_count = 0
        for _, row in pg_df.iterrows():
            bq_query = f"""
            SELECT quantity, last_updated
            FROM `inventory_analytics_prod.inventory_master`
            WHERE sku_id = '{row['sku_id']}'
            """
            bq_result = list(self.bq_client.query(bq_query))
            if bq_result and bq_result[0][0] == row["quantity"]:
                accuracy_count += 1

        accuracy = (accuracy_count / sample_size) * 100
        logging.info(f"Sample validation accuracy: {accuracy:.2f}%")
        return accuracy

if __name__ == "__main__":
    validator = MigrationValidator(
        postgres_conn="postgresql://user:pass@legacy-host:5432/inventory",
        gcp_project="client-migration-project"
    )

    counts = validator.validate_record_counts()
    accuracy = validator.validate_data_integrity()

    print("Migration Validation Results:")
    print(f"Source Records: {counts['postgres_records']:,}")
    print(f"Target Records: {counts['bigquery_records']:,}")
    print(f"Data Accuracy: {accuracy:.2f}%")
