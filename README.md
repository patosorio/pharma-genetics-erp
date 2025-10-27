# Pharma Genetics ERP

## Overview

This repository contains the complete business management system for Thai Cannabis Genetics Co., a GACP-certified cannabis clone cultivation business. The system consists of two primary components:

1. **Django ERP** - Operational system for day-to-day business management
2. **Plotly Dash BI Dashboard** - Investor-facing analytics and business intelligence

The architecture implements a clear separation between operational and analytical workloads for optimal performance and scalability.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     DJANGO ERP (Operational)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Genetics  │  │Cultivation│ │Inventory │  │  Sales   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Purchasing│  │    HR     │  │Accounting│  │  Core    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│               PostgreSQL (Transactional DB)                 │
│               ↓ (Optimized for WRITES)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ ETL Pipeline
                           │ (Cloud Functions + Cloud Scheduler)
                           │ - Data validation & transformation
                           │
                           ↓
         ┌─────────────────────────────────────┐
         │    GCP BigQuery (Data Warehouse)    │
         │                                     │           │
         └──────────────────┬───────────────────┘
                           │
                           │ Direct SQL Queries
                           │ (Read-only access)
                           │
                           ↓
         ┌─────────────────────────────────────┐
         │   PLOTLY DASH BI DASHBOARD          │
         │   (Investor & Management Analytics) │
         │                                      │
         │  Features:                        │
         │  ├── Financial KPIs                 │
         │  ├── Production Metrics             │
         │  ├── Sales Analytics                │
         │  ├── Capacity Planning              │
         │  └── Investor Reports               │
         └─────────────────────────────────────┘
```

## Component Details

### 1. Django ERP (Operational System)

**Purpose**: Handle all day-to-day business operations with real-time data entry and management.

**Technology Stack**:
- Django 5.0+
- PostgreSQL (Cloud SQL)
- Firebase Auth (Authentication)
- Django Admin (Primary UI)
- Django REST Framework (Optional API)
- Frontend: Next.Js (V0 Generated)

**Key Apps**:
- `core/` - Shared models (Location, Contact, Currency, Settings)
- `genetics/` - Strain catalog and genetic profiles
- `cultivation/` - Mother plant management, production batches, clone tracking
- `inventory/` - Clone stock levels, movements, alerts
- `sales/` - Orders, customers, invoices, payments
- `purchasing/` - Suppliers, purchase orders, expenses
- `hr/` - Payroll, employees, attendance
- `accounting/` - General ledger, journal entries, tax management

**Database Design**:
- Normalized schema (3NF) for data integrity
- Foreign key constraints
- Audit trails (created_at, updated_at, updated_by)
- Soft deletes where applicable

**Users**:
- Internal staff (cultivation managers, sales reps, accountants)
- Primary interaction via Django Admin interface
- Real-time CRUD operations

---

### 2. ETL Pipeline (Data Synchronization)

**Purpose**: Extract operational data from Django ERP and load it into BigQuery for analytics.

**Technology Stack**:
- Google Cloud Functions (Python 3.11)
- Cloud Scheduler (Cron jobs)
- Cloud SQL Proxy (Secure DB access)
- BigQuery Python Client

**Pipeline Architecture**:

```python
# Conceptual flow (actual implementation in /etl directory)

1. EXTRACT (from Django PostgreSQL)
   ├── Connect via Cloud SQL Proxy

2. TRANSFORM

3. LOAD (to BigQuery)
   ├── Upsert to staging tables
   ├── Merge to production tables (SCD Type 2 for history)
   ├── Update metadata tables (last_sync_time, row_counts)
   └── Send alerts on failures
```

**Schedule**:
- **Daily Sync**: TBC
- **Incremental**: Only sync changed records (based on `updated_at`)
- **Full Refresh**: TBC

**Data Quality Checks**:
- Row count validation (source vs destination)
- Foreign key integrity checks
- Business rule validations 
- Duplicate detection

---

### 3. BigQuery Data Warehouse

**Purpose**: Centralized analytical database optimized for complex queries and aggregations.

**Schema Design**:

-> TODO: create reasme schema with claude from sql tables we have. 

### 4. Plotly Dash BI Dashboard

**Purpose**: Investor-facing analytics dashboard with interactive visualizations and financial projections.

**Technology Stack**:
- Plotly Dash (Python framework)
- Plotly Express / Plotly Graph Objects (Visualizations)
- Dash Bootstrap Components (UI framework)
- BigQuery Python Client (Data access)
- Pandas (Data manipulation)

**Key Features**:

#### A. Executive Summary (Homepage)
- TODO: Summary dashboard
#### B. Financial Performance
- P&L Statement (monthly/quarterly/annual)
- Cash Flow Waterfall
- Gross Margin by Product Tier
- Break-even Analysis
- Unit Economics Dashboard

#### C. Production Analytics
- Clone Production by Strain
- Mother Plant Utilization
- Batch Success Rates
- Production Cycle Times
- Capacity Planning Scenarios

#### D. Sales Analytics
- Customer Tier Analysis
- Top Customers by Revenue
- Average Order Value by Tier
- Sales Pipeline (if applicable)
- Geographic Distribution

#### E. Investor Reports
- Sources & Uses of Funds
- ROI Projections
- Payback Period Calculations
- Scenario Analysis (conservative/base/optimistic)
- Export to PDF functionality

**Authentication**:
- Firebase Auth integration
- Role-based access (Investors see different views than management)
- Read-only access to data (no write operations)

**Performance Optimization**:
- Query result caching (Redis or in-memory)
- Materialized views in BigQuery (pre-aggregated data)
- Lazy loading of heavy visualizations
- Date range filters to limit data volume

---

**Architecture Flow:**
```
Next.js Frontend (ERP UI) ─────► Django REST API ─────► PostgreSQL
                                        │
                                        │ ETL Pipeline
                                        ↓
                                   BigQuery
                                        │
                                        ↓
                          Plotly Dash (Investor Dashboard)

---

## Data Flow

### Step 1: User Creates Order in Django ERP (employers can manage their work in their ERP)
### Step 2: ETL Pipeline Runs (X day at x Time)
### Step 3: Dashboard Queries BigQuery
### Step 4: Investor Views Dashboard

## Getting Started

TODO: SETUP!
TODO: Dashboard: move to a new repository.
