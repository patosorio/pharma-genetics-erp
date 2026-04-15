# Pharma Genetics ERP

## Overview

This repository contains the complete business management system for Genetics GACP-certified cultivation business. The system consists of two primary components:

1. **Django ERP** - Operational system for day-to-day business management
2. **Plotly Dash BI Dashboard** - Investor-facing analytics and business intelligence

The architecture implements a clear separation between operational and analytical workloads for optimal performance and scalability.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     DJANGO ERP (Operational)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Genetics  │  │Cultivation│ │Inventory │  │  Sales   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Purchasing│  │    HR     │  │Accounting│  │  Core    │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                             │
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
         │                                     │           
         └──────────────────┬───────────────────┘
                           │
                           │ Direct SQL Queries
                           │ (Read-only access)
                           │
                           ↓
         ┌─────────────────────────────────────┐
         │   PLOTLY DASH BI DASHBOARD          │
         │   (Investor & Management Analytics) │
         │                                     │
         │  Features:                          │
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

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Git

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/pharma-genetics-erp.git
cd pharma-genetics-erp
```

---

### 2. Backend Setup (Django)

#### Create and activate a virtual environment

```bash
python -m venv env
source env/bin/activate        # macOS / Linux
# env\Scripts\activate         # Windows
```

#### Install Python dependencies

```bash
pip install -r requirements.txt
```

#### Configure environment variables

Create a `.env` file inside the `backend/` directory:

```bash
cp backend/.env.example backend/.env   # if the example file exists, otherwise create it manually
```

Minimum required variables:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

For PostgreSQL (production), add:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pharma_erp
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

> In development the project defaults to SQLite — no extra DB config needed.

#### Apply migrations and create a superuser

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

#### Run the development server

```bash
python manage.py runserver
```

The Django API and admin panel will be available at `http://localhost:8000`.  
Admin panel: `http://localhost:8000/admin/`

---

### 3. Frontend Setup (Next.js)

```bash
cd client
npm install
npm run dev
```

The Next.js app will be available at `http://localhost:3000`.

#### Frontend environment variables

Create a `client/.env.local` file if you need to override the API base URL or Firebase config:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
```

---

### 4. Running Both Services Together

Open two terminal tabs and run each service independently:

| Terminal | Command | URL |
|----------|---------|-----|
| 1 | `cd backend && python manage.py runserver` | `http://localhost:8000` |
| 2 | `cd client && npm run dev` | `http://localhost:3000` |

---

### 5. Useful Django Commands

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Open Django shell
python manage.py shell

# Load fixture data (if any)
python manage.py loaddata fixtures/initial_data.json

# Run tests
python manage.py test
```

---

> **Note:** The Plotly Dash BI Dashboard and ETL pipeline are planned to be moved to a separate repository. Setup instructions for those components will be added once migrated.
