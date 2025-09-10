## terraform-gcp-migration_BH2025-09-01
**Enterprise Terraform → GCP Migration (BrewHaul Contract Engagement 2025-09-01)**  
*Zero-downtime inventory analytics migration, with: (a) automated Alteryx validation, and (b) CI-gated parity checks.*
---
### TL;DR — Executive summary
**Problem:** Migrate 1.2M+ inventory records from legacy Terraform-managed PostgreSQL to Google Cloud Platform with zero downtime and complete data integrity assurance.  
**Solution:** Parallel GCP deployment (Terraform Cloud), incremental batch + Pub/Sub delta capture, and a CI-gated automated validation layer (Alteryx + Python validator).  
**Impact:** 0 hours downtime, 100% data integrity, 35% infrastructure cost reduction, 3.2× analytics performance improvement.

### Architecture Overview
### Key Design Features:
- Parallel infra (Blue/Green): Cutover is a pointer switch (target GCP deployed in parallel)
- Partitioning: BigQuery tables partitioned by last_updated (DAY) to reduce scanned bytes for common time-window analyses
- Clustering: Cluster by sku_id and region to improve join locality and reduce query cost for common slices
- Validation-First cutover: ALteryx + Python validator run as a CI gate after deployment
- CI Integration: see docs/ci-trigger-example.sh for example CI script, as Terraform apply -> validation -> cutover dating logic

### High level flow
Legacy PostgreSQL (on-prem)  
→ Batch transfers (Cloud Dataflow) + Real-time deltas (Pub/Sub)  
→ BigQuery (analytics mart)  
↔ Cloud SQL (operational reads)  
↔ Alteryx validation layer (CI gate)  
→ Monitoring & executive exception reporting

### ASCII diagram
[Legacy Postgres] --(batch export)--> [Cloud Dataflow] --> [BigQuery: bh_mart.inventory_master]
\ ^
--(Pub/Sub deltas)----------/
|
[Alteryx]
|
[Validation Reports -> Exec Dashboards]


### Mermaid diagram
```mermaid
flowchart LR
  PG[Legacy PostgreSQL]
  DF[Cloud Dataflow (batch)]
  PS[Pub/Sub (deltas)]
  BQ[BigQuery - inventory_analytics_prod]
  CS[Cloud SQL - operational]
  AZ[Alteryx Validation]
  MON[Monitoring / Exec Dashboard]

  PG --> DF
  DF --> BQ
  PG --> PS
  PS --> BQ
  BQ --> AZ
  PG --> AZ
  AZ --> MON
  BQ --> CS
