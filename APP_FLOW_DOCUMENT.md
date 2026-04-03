# Multi-Platform E-Commerce Management System — Complete Flow Document

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Business Model — Primary Sales vs Secondary Sales](#2-business-model--primary-sales-vs-secondary-sales)
3. [Problem Statement](#3-problem-statement)
4. [Solution — One Unified App](#4-solution--one-unified-app)
5. [Platform Integration](#5-platform-integration)
6. [User Roles & Permissions](#6-user-roles--permissions)
7. [App Modules Overview](#7-app-modules-overview)
8. [Module 1: Authentication & Authorization](#8-module-1-authentication--authorization)
9. [Module 2: Company Management (Brand & Product Catalog)](#9-module-2-company-management-brand--product-catalog)
10. [Module 3: Distributor Management](#10-module-3-distributor-management)
11. [Module 4: Platform Management](#11-module-4-platform-management)
12. [Module 5: Primary Sales (Company to Distributor)](#12-module-5-primary-sales-company-to-distributor)
13. [Module 6: Secondary Sales / Order Management (Platform Orders)](#13-module-6-secondary-sales--order-management-platform-orders)
14. [Module 7: Inventory Management (Multi-Level)](#14-module-7-inventory-management-multi-level)
15. [Module 8: Fulfillment Process (Per-Platform Shipping)](#15-module-8-fulfillment-process-per-platform-shipping)
16. [Module 9: Returns & Refunds Management](#16-module-9-returns--refunds-management)
17. [Module 10: Payments & Reconciliation](#17-module-10-payments--reconciliation)
18. [Module 11: Dashboard (Unified + Per-Platform)](#18-module-11-dashboard-unified--per-platform)
19. [Module 12: Reports & Analytics](#19-module-12-reports--analytics)
20. [Module 13: Notifications System](#20-module-13-notifications-system)
21. [Module 14: Audit Trail](#21-module-14-audit-trail)
22. [Module 15: SAP Integration (ERP Connectivity)](#22-module-15-sap-integration-erp-connectivity)
23. [Database Design — Detailed Table Structures](#23-database-design--detailed-table-structures)
24. [ER Model (Entity Relationship Diagram)](#24-er-model-entity-relationship-diagram)
25. [Platform-Specific Integration Details](#25-platform-specific-integration-details)
26. [Complete Flow Diagrams](#26-complete-flow-diagrams)
27. [Error Handling](#27-error-handling)
28. [Security Considerations](#28-security-considerations)
29. [Tech Stack Recommendation](#29-tech-stack-recommendation)
30. [Build Priority Order](#30-build-priority-order)

---

## 1. Project Overview

**App Name:** Multi-Platform E-Commerce Management System (MPEMS)

**Purpose:** Build a single, unified application that manages the entire lifecycle of
products flowing from a Brand/Manufacturer (Company) through Distributors and onto
multiple e-commerce platforms (Amazon, Flipkart, Meesho, Myntra, JioMart, Snapdeal, etc.).

**Business Reality:**
- The Company (Brand/Manufacturer) does NOT sell directly on any platform
- The Company sells stock to Distributors (this is PRIMARY SALES)
- Distributors list and sell products on multiple e-commerce platforms (this is SECONDARY SALES)
- Each platform sends Purchase Orders (POs) with different formats, rules, and APIs
- Managing all this across 6+ platforms manually is chaos

**What This App Does:**
- Manages Company product catalog and pricing
- Tracks stock transfers from Company to Distributors (Primary Sales)
- Integrates with ALL major e-commerce platforms via their APIs
- Unifies orders from all platforms into one view
- Manages multi-level inventory (Company → Distributor → Platform)
- Handles platform-specific fulfillment, returns, and payments
- Provides cross-platform analytics and reporting

**Who Uses It:**
- Company Admin (brand owner / management)
- Distributor Managers (run distribution operations)
- Warehouse Staff (handle physical stock and shipments)
- Platform Managers (manage listings and orders on specific platforms)
- Viewers (read-only access for stakeholders)

---

## 2. Business Model — Primary Sales vs Secondary Sales

### 2.1 The Two-Tier Sales Model

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         BUSINESS MODEL OVERVIEW                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  TIER 1: PRIMARY SALES (Company → Distributor)                             ║
║  ═══════════════════════════════════════════════                            ║
║                                                                            ║
║  ┌──────────────────┐    Stock Transfer    ┌──────────────────┐            ║
║  │                  │ ──────────────────► │                  │            ║
║  │   COMPANY        │    Invoice           │  DISTRIBUTOR     │            ║
║  │   (Brand /       │ ──────────────────► │  (Region-based)  │            ║
║  │    Manufacturer) │                      │                  │            ║
║  │                  │ ◄────────────────── │                  │            ║
║  └──────────────────┘    Payment           └──────────────────┘            ║
║                                                    │                       ║
║  - Company manufactures products                   │                       ║
║  - Company sells IN BULK to distributors           │                       ║
║  - Each distributor covers a region/set of         │                       ║
║    platforms                                       │                       ║
║  - This is the Company's actual revenue source     │                       ║
║                                                    │                       ║
║  ══════════════════════════════════════════════════ │ ════════════════════  ║
║                                                    │                       ║
║  TIER 2: SECONDARY SALES (Distributor → Platform → End Customer)           ║
║  ═══════════════════════════════════════════════════════════════            ║
║                                                    │                       ║
║                                                    ▼                       ║
║                                           ┌────────────────┐              ║
║                                           │  DISTRIBUTOR   │              ║
║                                           │  WAREHOUSE     │              ║
║                                           └───────┬────────┘              ║
║                                                   │                       ║
║                          ┌────────────────────────┼────────────────┐      ║
║                          │            │           │          │     │      ║
║                          ▼            ▼           ▼          ▼     ▼      ║
║                      ┌───────┐  ┌────────┐  ┌───────┐  ┌──────┐┌──────┐ ║
║                      │Amazon │  │Flipkart│  │Meesho │  │Myntra││Others│ ║
║                      └───┬───┘  └───┬────┘  └───┬───┘  └──┬───┘└──┬───┘ ║
║                          │          │           │          │       │      ║
║                          ▼          ▼           ▼          ▼       ▼      ║
║                      ┌──────────────────────────────────────────────┐     ║
║                      │           END CUSTOMERS                      │     ║
║                      └──────────────────────────────────────────────┘     ║
║                                                                            ║
║  - Distributor lists products on each platform                             ║
║  - Each platform has its own rules, fees, APIs                             ║
║  - Customer places order on a platform                                     ║
║  - Platform sends PO to distributor                                        ║
║  - Distributor ships from their warehouse                                  ║
║  - Platform collects payment, deducts fees, settles to distributor         ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### 2.2 Stock Flow Diagram

```
COMPLETE STOCK FLOW:

  MANUFACTURER
       │
       │  (Production)
       ▼
  ┌──────────────────┐
  │  COMPANY         │
  │  WAREHOUSE       │
  │  (Central Stock) │
  └────────┬─────────┘
           │
           │  PRIMARY SALE (Bulk Transfer + Invoice)
           │
     ┌─────┴─────────────────────────────┐
     │                                   │
     ▼                                   ▼
┌──────────────────┐            ┌──────────────────┐
│  DISTRIBUTOR A   │            │  DISTRIBUTOR B   │
│  (North Region)  │            │  (South Region)  │
│  ──────────────  │            │  ──────────────  │
│  Platforms:      │            │  Platforms:      │
│  - Amazon        │            │  - Flipkart      │
│  - Flipkart      │            │  - Meesho        │
│  - JioMart       │            │  - Myntra        │
└────────┬─────────┘            └────────┬─────────┘
         │                               │
         │  SECONDARY SALE               │  SECONDARY SALE
         │  (Platform POs)               │  (Platform POs)
         │                               │
   ┌─────┼──────┐                  ┌─────┼──────┐
   │     │      │                  │     │      │
   ▼     ▼      ▼                  ▼     ▼      ▼
 Amz   Flip  JioMart           Flip  Meesho  Myntra
  │     │      │                  │     │      │
  ▼     ▼      ▼                  ▼     ▼      ▼
 End   End    End               End   End    End
 Cust  Cust   Cust              Cust  Cust   Cust
```

### 2.3 Revenue Flow

```
MONEY FLOW:

  END CUSTOMER
       │
       │  Pays full MRP/sale price
       ▼
  ┌──────────────────┐
  │  PLATFORM        │
  │  (Amazon, etc.)  │
  │                  │
  │  Deducts:        │
  │  - Commission    │
  │  - Shipping fee  │
  │  - TCS/TDS      │
  │  - Return costs  │
  │  - Penalties     │
  └────────┬─────────┘
           │
           │  Net settlement amount
           ▼
  ┌──────────────────┐
  │  DISTRIBUTOR     │
  │                  │
  │  Revenue:        │
  │  Settlement      │
  │  - Cost Price    │
  │  = Margin        │
  └────────┬─────────┘
           │
           │  Pays Company for stock purchased
           ▼
  ┌──────────────────┐
  │  COMPANY         │
  │                  │
  │  Revenue:        │
  │  Distributor     │
  │  payment         │
  │  - Manufacturing │
  │  = Profit        │
  └──────────────────┘
```

---

## 3. Problem Statement

### Current Process (Manual Multi-Platform Chaos)

```
TODAY'S REALITY:

  Distributor has accounts on 6 platforms.
  Each platform has its own seller dashboard.
  Each day:

  ┌─────────────────────────────────────────────────────────────┐
  │  8:00 AM  - Login to Amazon Seller Central                  │
  │           - Check new orders                                │
  │           - Download shipping labels                        │
  │           - Check returns                                   │
  │                                                             │
  │  8:30 AM  - Login to Flipkart Seller Hub                   │
  │           - Check new orders                                │
  │           - Download manifests                              │
  │           - Check returns                                   │
  │                                                             │
  │  9:00 AM  - Login to Meesho Supplier Panel                 │
  │           - Check new orders                                │
  │           - Process shipments                               │
  │           - Check returns                                   │
  │                                                             │
  │  9:30 AM  - Login to Myntra Partner Portal                 │
  │           - Check new orders...                             │
  │                                                             │
  │  10:00 AM - Login to JioMart Seller Portal...              │
  │  10:30 AM - Login to Snapdeal Seller Panel...              │
  │                                                             │
  │  11:00 AM - Open Excel to track inventory across platforms  │
  │  11:30 AM - Manually update stock on each platform          │
  │  12:00 PM - Calculate which platform owes what money        │
  │                                                             │
  │  REPEAT DAILY.                                              │
  └─────────────────────────────────────────────────────────────┘
```

### Problems with Current Process

| #  | Problem                                          | Impact                                                |
|----|--------------------------------------------------|-------------------------------------------------------|
| 1  | Login to 6+ platform dashboards daily            | Wastes 2-3 hours just switching between platforms     |
| 2  | No unified order view                            | Miss orders, late shipments, penalties                |
| 3  | Inventory tracked in Excel                       | Overselling on one platform, dead stock on another    |
| 4  | Stock updates done manually per platform         | One wrong number = oversell = cancellation penalty    |
| 5  | Each platform has different return policies      | Returns processed incorrectly, money lost             |
| 6  | No visibility of cross-platform performance      | Cannot compare which platform is profitable           |
| 7  | Company has no view into distributor operations  | Cannot track if stock sent to distributor is selling  |
| 8  | Payment reconciliation done in Excel             | Platform fees miscalculated, revenue leakage          |
| 9  | No audit trail across platforms                  | Disputes cannot be resolved with data                 |
| 10 | Adding a new platform = more manual work         | Scaling is impossible                                 |
| 11 | Multiple distributors = multiply all problems    | Company cannot manage 5 distributors x 6 platforms    |
| 12 | Primary sales (Company to Distributor) tracked   | Stock transfers tracked in paper/WhatsApp             |
|    | outside the system                               |                                                       |

---

## 4. Solution — One Unified App

Build a single web application that:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     ONE APP TO MANAGE EVERYTHING                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PRIMARY SALES (Company → Distributor):                                  │
│  ─────────────────────────────────────                                   │
│  - Manage product catalog and pricing                                    │
│  - Create and track stock transfers to distributors                      │
│  - Generate invoices for distributor purchases                           │
│  - Track distributor payments and outstanding amounts                    │
│                                                                          │
│  SECONDARY SALES (Distributor → Platform → Customer):                    │
│  ────────────────────────────────────────────────────                    │
│  - Connect ALL platform accounts in one place                            │
│  - See orders from ALL platforms in a single unified view                │
│  - Manage inventory across ALL platforms from one screen                 │
│  - Process fulfillment with platform-specific shipping rules             │
│  - Handle returns per platform's return policy                           │
│  - Track payments and commissions per platform                           │
│                                                                          │
│  UNIFIED INTELLIGENCE:                                                   │
│  ────────────────────                                                    │
│  - Dashboard showing all platforms at a glance                           │
│  - Cross-platform analytics (which platform sells more?)                 │
│  - Distributor performance tracking                                      │
│  - Inventory optimization across platforms                               │
│  - Automated alerts and notifications                                    │
│  - Complete audit trail of every action                                  │
│                                                                          │
│  SAP / ERP INTEGRATION:                                                  │
│  ──────────────────────                                                  │
│  - Sync product master data, pricing, and stock from SAP                 │
│  - Push sales orders, invoices, and payments back to SAP                 │
│  - Two-way inventory sync (SAP ↔ MPEMS)                                 │
│  - Financial posting: all transactions reflected in SAP accounting       │
│  - Distributor ledger sync with SAP FI (Finance) module                  │
│                                                                          │
│  ARCHITECTURE:                                                           │
│                                                                          │
│  ┌─────────┐  ┌─────────┐  ┌──────┐  ┌──────┐  ┌───────┐  ┌────────┐  │
│  │ Amazon  │  │Flipkart │  │Meesho│  │Myntra│  │JioMart│  │Snapdeal│  │
│  │  API      │  │  API    │  │ API  │  │ API  │  │  API  │  │  API   │  │
│  └────┬────┘  └────┬────┘  └──┬───┘  └──┬───┘  └───┬───┘  └───┬────┘  │
│       │            │          │         │          │           │        │
│       └────────────┴──────────┴────┬────┴──────────┴───────────┘        │
│                                    │                                     │
│                            ┌───────▼────────┐       ┌────────────────┐  │
│                            │  PLATFORM      │       │  SAP ERP       │  │
│                            │  INTEGRATION   │       │  ────────────  │  │
│                            │  LAYER         │       │  MM / SD / FI  │  │
│                            └───────┬────────┘       │  FICO / WM     │  │
│                                    │                └───────┬────────┘  │
│                                    │                        │           │
│                            ┌───────▼────────────────────────▼──┐       │
│                            │                                   │       │
│                            │         UNIFIED APP (MPEMS)       │       │
│                            │   ┌──────────────────────────┐    │       │
│                            │   │   SAP Integration Layer  │    │       │
│                            │   │   (RFC / BAPI / OData)   │    │       │
│                            │   └──────────────────────────┘    │       │
│                            │                                   │       │
│                            └───────────────┬───────────────────┘       │
│                                            │                           │
│                    ┌───────────────┬────────┼────────┬──────────┐      │
│                    │               │        │        │          │      │
│              ┌─────▼─────┐  ┌─────▼─────┐  │  ┌─────▼─────┐   │      │
│              │  Company  │  │Distributor│  │  │ Platform  │   │      │
│              │  Module   │  │  Module   │  │  │  Module   │   │      │
│              └───────────┘  └───────────┘  │  └───────────┘   │      │
│                                      ┌─────▼─────┐  ┌────────▼───┐  │
│                                      │    SAP    │  │  Admin     │  │
│                                      │  Module   │  │ Dashboard  │  │
│                                      └───────────┘  └────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Platform Integration

### 5.1 Supported Platforms

| #  | Platform   | Type               | API Available | Integration Method         |
|----|------------|--------------------|---------------|----------------------------|
| 1  | Amazon     | Marketplace        | Yes (SP-API)  | REST API (Selling Partner)  |
| 2  | Flipkart   | Marketplace        | Yes           | REST API (Seller API)       |
| 3  | Meesho     | Social Commerce    | Yes           | REST API (Supplier API)     |
| 4  | Myntra     | Fashion Marketplace| Yes (Partner) | REST API (Partner Portal)   |
| 5  | JioMart    | Marketplace        | Yes           | REST API (Seller API)       |
| 6  | Snapdeal   | Marketplace        | Yes           | REST API (Seller API)       |
| 7  | SAP ERP    | ERP System         | Yes (RFC/OData)| RFC, BAPI, OData REST API  |
| 8  | [New]      | Extensible         | -             | Plugin architecture         |

### 5.2 Platform Fee Structures

```
PLATFORM FEE COMPARISON:

┌──────────────────────────────────────────────────────────────────────────────┐
│  Platform   │ Commission  │ Shipping Fee   │ Payment Cycle │ Return Window │
├──────────────────────────────────────────────────────────────────────────────┤
│  Amazon     │ 5-15%       │ Weight-based   │ 7-14 days     │ 7-30 days     │
│             │ (category)  │ + distance     │               │ (category)    │
├──────────────────────────────────────────────────────────────────────────────┤
│  Flipkart   │ 5-20%       │ Weight-based   │ 7-15 days     │ 7-30 days     │
│             │ (category)  │ + zone         │               │ (category)    │
├──────────────────────────────────────────────────────────────────────────────┤
│  Meesho     │ 0% (margin  │ Free for       │ 7-10 days     │ 7 days        │
│             │  based)     │ supplier       │               │               │
├──────────────────────────────────────────────────────────────────────────────┤
│  Myntra     │ 10-25%      │ Platform       │ 7-15 days     │ 7-30 days     │
│             │ (category)  │ managed        │               │ (category)    │
├──────────────────────────────────────────────────────────────────────────────┤
│  JioMart    │ 5-12%       │ Weight-based   │ 7-14 days     │ 7-15 days     │
│             │ (category)  │               │               │               │
├──────────────────────────────────────────────────────────────────────────────┤
│  Snapdeal   │ 5-15%       │ Weight-based   │ 7-10 days     │ 7 days        │
│             │ (category)  │ + distance     │               │               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Platform Order Format Differences

```
Each platform sends order data in different formats.
The Integration Layer normalizes all of them into one unified format.

AMAZON ORDER:                    FLIPKART ORDER:
─────────────                    ────────────────
{                                {
  "AmazonOrderId": "X",           "order_id": "X",
  "PurchaseDate": "...",           "created_at": "...",
  "OrderStatus": "Pending",       "status": "APPROVED",
  "OrderItems": [...]              "order_items": [...]
}                                }

MEESHO ORDER:                    MYNTRA ORDER:
─────────────                    ─────────────
{                                {
  "sub_order_id": "X",            "orderNo": "X",
  "created_at": "...",            "orderDate": "...",
  "order_status": "pending",      "orderStatus": "CREATED",
  "product": {...}                 "items": [...]
}                                }

                    ▼ NORMALIZED TO ▼

            UNIFIED ORDER FORMAT:
            ─────────────────────
            {
              "order_id": "UNIFIED-X",
              "platform": "amazon|flipkart|meesho|...",
              "platform_order_id": "ORIGINAL-ID",
              "distributor_id": 1,
              "status": "PENDING",
              "items": [...],
              "created_at": "...",
              "shipping_details": {...},
              "platform_fees": {...}
            }
```

---

## 6. User Roles & Permissions

### Role: Company Admin
| Feature                        | Access    |
|--------------------------------|-----------|
| Dashboard (all distributors)   | Full      |
| Product Catalog                | Full      |
| Distributor Management         | Full      |
| Platform Configuration         | Full      |
| Primary Sales (Stock Transfers)| Full      |
| Secondary Sales (View)         | View Only |
| Inventory (all levels)         | Full      |
| Fulfillment                    | View Only |
| Returns                        | View Only |
| Payments & Reconciliation      | Full      |
| Reports & Analytics            | Full      |
| User Management                | Full      |
| Audit Trail                    | Full      |
| System Settings                | Full      |

### Role: Distributor Manager
| Feature                        | Access              |
|--------------------------------|---------------------|
| Dashboard (own distributor)    | Full                |
| Product Catalog                | View Only           |
| Distributor Management         | Own Profile Only    |
| Platform Configuration         | Own Platforms Only  |
| Primary Sales (Stock Transfers)| View + Acknowledge  |
| Secondary Sales (Orders)       | Full (own orders)   |
| Inventory (own warehouse)      | Full                |
| Fulfillment                    | Full (own orders)   |
| Returns                        | Full (own returns)  |
| Payments & Reconciliation      | Own Data Only       |
| Reports & Analytics            | Own Data Only       |
| User Management                | Own Staff Only      |
| Audit Trail                    | Own Actions Only    |
| System Settings                | Limited             |

### Role: Warehouse Staff
| Feature                        | Access              |
|--------------------------------|---------------------|
| Dashboard                      | View Only           |
| Product Catalog                | View Only           |
| Distributor Management         | No Access           |
| Platform Configuration         | No Access           |
| Primary Sales (Stock Transfers)| Receive & Count     |
| Secondary Sales (Orders)       | View + Fulfill      |
| Inventory (own warehouse)      | View + Update Stock |
| Fulfillment                    | Full (pick/pack/ship)|
| Returns                        | Process Returns     |
| Payments & Reconciliation      | No Access           |
| Reports & Analytics            | Limited             |
| User Management                | No Access           |
| Audit Trail                    | Own Actions Only    |
| System Settings                | No Access           |

### Role: Platform Manager
| Feature                        | Access              |
|--------------------------------|---------------------|
| Dashboard (assigned platforms) | View Only           |
| Product Catalog                | View Only           |
| Distributor Management         | No Access           |
| Platform Configuration         | Assigned Platforms  |
| Primary Sales                  | No Access           |
| Secondary Sales (Orders)       | Assigned Platforms  |
| Inventory                      | View Only           |
| Fulfillment                    | Assigned Platforms  |
| Returns                        | Assigned Platforms  |
| Payments & Reconciliation      | View (own platforms)|
| Reports & Analytics            | Own Platforms Only  |
| User Management                | No Access           |
| Audit Trail                    | Own Actions Only    |
| System Settings                | No Access           |

### Role: Viewer
| Feature                        | Access    |
|--------------------------------|-----------|
| Dashboard                      | View Only |
| Product Catalog                | View Only |
| Distributor Management         | View Only |
| Platform Configuration         | No Access |
| Primary Sales                  | View Only |
| Secondary Sales (Orders)       | View Only |
| Inventory                      | View Only |
| Fulfillment                    | View Only |
| Returns                        | View Only |
| Payments & Reconciliation      | View Only |
| Reports & Analytics            | View Only |
| User Management                | No Access |
| Audit Trail                    | No Access |
| System Settings                | No Access |

---

## 7. App Modules Overview

```
┌────────────────────────────────────────────────────────────────┐
│                       APP MODULES                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  CORE MODULES:                                                 │
│  1.  Authentication & Authorization                            │
│  2.  Company Management (Brand & Product Catalog)              │
│  3.  Distributor Management                                    │
│  4.  Platform Management (Connect & Configure Marketplaces)    │
│                                                                │
│  SALES MODULES:                                                │
│  5.  Primary Sales (Company → Distributor Stock Transfers)     │
│  6.  Secondary Sales / Order Management (Platform Orders)      │
│                                                                │
│  OPERATIONS MODULES:                                           │
│  7.  Inventory Management (Multi-Level)                        │
│  8.  Fulfillment Process (Per-Platform Shipping Rules)         │
│  9.  Returns & Refunds Management (Platform-Specific)          │
│  10. Payments & Reconciliation (Platform Fees & Settlements)   │
│                                                                │
│  INTELLIGENCE MODULES:                                         │
│  11. Dashboard (Unified + Per-Platform Views)                  │
│  12. Reports & Analytics (Cross-Platform Comparison)           │
│  13. Notifications System                                      │
│  14. Audit Trail                                               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 8. Module 1: Authentication & Authorization

### 8.1 Login Flow

```
START
  |
  +-- User opens app in browser
  |
  +-- App shows Login page
  |     - Email / Username field
  |     - Password field
  |     - Login button
  |
  +-- User enters credentials and clicks Login
  |
  +-- System validates:
  |     +-- Are fields empty?
  |     |     +-- YES -> Show error: "Please fill all fields"
  |     |
  |     +-- Does user exist in database?
  |     |     +-- NO -> Show error: "Invalid credentials"
  |     |
  |     +-- Does password match (bcrypt hash comparison)?
  |     |     +-- NO -> Show error: "Invalid credentials"
  |     |     +-- Increment failed_login_count
  |     |     +-- If failed_login_count >= 5 -> Lock account for 30 minutes
  |     |
  |     +-- Is account active?
  |     |     +-- NO -> Show error: "Account is disabled. Contact admin"
  |     |
  |     +-- Is account locked?
  |           +-- YES -> Show error: "Account locked. Try again in X minutes"
  |
  +-- Login successful:
  |     +-- Create JWT token containing:
  |     |     - user_id
  |     |     - role (company_admin / distributor_manager / warehouse / platform_mgr / viewer)
  |     |     - distributor_id (if distributor user)
  |     |     - assigned_platforms[] (if platform manager)
  |     +-- Log login event (user, timestamp, IP, device)
  |     +-- Redirect to role-appropriate Dashboard
  |
  END
```

### 8.2 Multi-Tenant Access Control

```
ACCESS IS SCOPED BY:

  Company Admin  --> Sees ALL distributors, ALL platforms, ALL data
  Distributor Mgr --> Sees ONLY their distributor's data
  Warehouse Staff --> Sees ONLY their warehouse's operations
  Platform Mgr  --> Sees ONLY their assigned platform(s) data
  Viewer        --> Sees ONLY what their scope allows (read-only)

EVERY API REQUEST:
  1. Validate JWT token
  2. Extract user role and scope
  3. Apply data filters based on scope
  4. Return only authorized data

EXAMPLE:
  GET /api/orders
  - Company Admin   -> Returns orders from ALL distributors, ALL platforms
  - Distributor Mgr -> Returns orders from THEIR distributor only
  - Platform Mgr    -> Returns orders from THEIR assigned platforms only
```

### 8.3 Session Management

```
- JWT token expires after 8 hours (one shift)
- Refresh token expires after 7 days
- On every API request, validate token
- If token expired -> Attempt silent refresh with refresh token
- If refresh token expired -> Redirect to login
- Logout -> Invalidate both tokens, redirect to login
- Concurrent sessions allowed (mobile + desktop)
```

### 8.4 Password Management

```
- Passwords stored as bcrypt hash (cost factor 12)
- Admin can reset any user's password
- Distributor Manager can reset their staff passwords
- Minimum password length: 8 characters
- Must contain: uppercase + lowercase + number + special character
- Password history: cannot reuse last 5 passwords
```

---

## 9. Module 2: Company Management (Brand & Product Catalog)

### 9.1 Company Profile

```
┌──────────────────────────────────────────────────────────────┐
│  COMPANY PROFILE                                             │
│  ──────────────                                              │
│                                                              │
│  Company Name:     [Brand Name Pvt Ltd]                      │
│  GSTIN:            [27AABCU9603R1ZM]                         │
│  PAN:              [AABCU9603R]                               │
│  Registered Address: [Full Address]                           │
│  Contact Email:    [admin@brand.com]                          │
│  Contact Phone:    [+91-XXXXXXXXXX]                          │
│                                                              │
│  Bank Details (for receiving payments from distributors):     │
│  Account Name:     [Brand Name Pvt Ltd]                      │
│  Account Number:   [XXXXXXXXXX]                              │
│  IFSC Code:        [XXXX0XXXXXX]                             │
│  Bank Name:        [Bank Name]                               │
│                                                              │
│  [Edit Profile]                                              │
└──────────────────────────────────────────────────────────────┘
```

### 9.2 Product Catalog

```
THIS IS THE MASTER PRODUCT LIST.
All distributors and platforms reference products from this catalog.

┌────────────────────────────────────────────────────────────────────────────┐
│  PRODUCT CATALOG                                  [+ Add Product] [Import]│
│  ──────────────────────────────────────────────────────────────            │
│                                                                            │
│  FILTERS: [Category ▼] [Brand ▼] [Status ▼] [Search SKU/Name]            │
│                                                                            │
│  #  | SKU       | Name           | Category | MRP    | Dist.Price | Status│
│  1  | SKU-001   | T-Shirt Blue M | Apparel  | 799    | 399        | Active│
│  2  | SKU-002   | T-Shirt Blue L | Apparel  | 799    | 399        | Active│
│  3  | SKU-003   | Jeans Black 32 | Apparel  | 1499   | 749        | Active│
│  4  | SKU-004   | Sneakers Wht 9 | Footwear | 2499   | 1249       | Draft │
│                                                                            │
│  MRP = Maximum Retail Price (what end customer pays)                       │
│  Dist.Price = Price at which Company sells to Distributor (Primary Sale)   │
│                                                                            │
│  Showing 1-20 of 350       [<- Prev] [1] [2] [3] [Next ->]               │
└────────────────────────────────────────────────────────────────────────────┘
```

### 9.3 Product Detail Structure

```
EACH PRODUCT HAS:

  Basic Information:
  - SKU (Stock Keeping Unit) -- unique identifier
  - Product Name
  - Description (short + long)
  - Category / Sub-category
  - Brand
  - Images (multiple)
  - Weight, Dimensions
  - HSN Code (for GST)
  - GST Rate (5%, 12%, 18%, etc.)

  Pricing:
  - MRP (Maximum Retail Price)
  - Distributor Price (Company sells to Distributor at this price)
  - Recommended Selling Price per platform (optional)
  - Cost Price (manufacturing cost -- internal)

  Variants (if applicable):
  - Size: S, M, L, XL, XXL
  - Color: Blue, Red, Black
  - Each variant has its own SKU, stock, pricing

  Platform Mappings:
  - Amazon ASIN (if listed)
  - Flipkart FSN/Listing ID (if listed)
  - Meesho Product ID (if listed)
  - Myntra Style ID (if listed)
  - JioMart Product ID (if listed)
  - Snapdeal Product ID (if listed)

  Status: Draft / Active / Discontinued
```

### 9.4 Add Product Flow

```
START
  |
  +-- Company Admin clicks "+ Add Product"
  |
  +-- Fill product form:
  |     - Basic info (SKU, name, description, category)
  |     - Pricing (MRP, distributor price, cost price)
  |     - Images (upload multiple)
  |     - Variants (if applicable)
  |     - Weight and dimensions
  |     - HSN code and GST rate
  |
  +-- System validates:
  |     +-- SKU unique?
  |     +-- All required fields filled?
  |     +-- Distributor price < MRP?
  |     +-- At least one image uploaded?
  |     +-- Valid HSN code format?
  |
  +-- Save product (status = DRAFT)
  |
  +-- Product now available for:
  |     - Stock transfers to distributors (Primary Sales)
  |     - Listing on platforms (via Platform Management)
  |
  END
```

---

## 10. Module 3: Distributor Management

### 10.1 Distributor List

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  DISTRIBUTORS                                          [+ Add Distributor]  │
│  ────────────────────────────────────────────────────────────────           │
│                                                                              │
│  #  | Name              | Region      | Platforms        | Status | Action  │
│  1  | NorthStar Dist.   | North India | Amz, Flip, Jio   | Active | [View] │
│  2  | SouthWave Dist.   | South India | Flip, Meesho, Myn| Active | [View] │
│  3  | WestEnd Traders   | West India  | Amz, Snap, Jio   | Active | [View] │
│  4  | EastLink Supply   | East India  | Flip, Meesho     | Paused | [View] │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Distributor Profile (Detail View)

When Company Admin or Distributor Manager clicks [View] on a distributor,
they see the **full distributor detail page** with ALL data — business info,
sales activity, inventory, shipping zones, payments, returns, and platform
performance — everything in one place.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  DISTRIBUTOR DETAIL: NorthStar Distribution Pvt Ltd          Status: ACTIVE │
│  ════════════════════════════════════════════════════════════════════════════ │
│                                                                              │
│  TABS: [Overview] [Sales] [Inventory] [Shipping] [Payments] [Returns]       │
│        [Platform Performance] [Activity Log]                                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### 10.2.1 Overview Tab — Business & Financial Summary

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  TAB: OVERVIEW                                              [Edit] [Export] │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ┌─ BUSINESS DETAILS ──────────────────────────────────────────────────────┐│
│  │  Company Name:     NorthStar Distribution Pvt Ltd                       ││
│  │  GSTIN:            07AABCU1234R1ZM                                      ││
│  │  PAN:              AABCU1234R                                           ││
│  │  Region:           North India (Delhi, UP, Haryana, Punjab, Rajasthan)  ││
│  │  Contact Person:   Rahul Sharma (Distributor Manager)                   ││
│  │  Email:            rahul@northstar.com                                  ││
│  │  Phone:            +91-98XXXXXXXX                                       ││
│  │  Onboarded:        2025-06-15                                           ││
│  │  Credit Limit:     Rs. 25,00,000                                        ││
│  │  Payment Terms:    Net 30 days                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─ WAREHOUSE(S) ─────────────────────────────────────────────────────────┐ │
│  │  #  | Warehouse Name        | Address              | PIN    | Manager  │ │
│  │  1  | Main Warehouse        | Plot 45, Okhla Ind.  | 110020 | Amit K.  │ │
│  │  2  | Secondary (Gurgaon)   | Sec 17, Gurgaon      | 122001 | Ravi S.  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─ CONNECTED PLATFORMS ──────────────────────────────────────────────────┐ │
│  │  Platform   | Status      | Account ID       | Last Sync    | Orders  │ │
│  │  Amazon     | Connected   | NORTHSTAR_AMZ    | 2 min ago    | 23 today│ │
│  │  Flipkart   | Connected   | NORTHSTAR_FK     | 5 min ago    | 18 today│ │
│  │  JioMart    | Connected   | NORTHSTAR_JIO    | 3 min ago    | 8 today │ │
│  │  Meesho     | Not Connected| —               | —            | —       │ │
│  │  Myntra     | Not Connected| —               | —            | —       │ │
│  │  Snapdeal   | Not Connected| —               | —            | —       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─ FINANCIAL SNAPSHOT (This Month) ──────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────┐│ │
│  │  │ Stock     │ │ Secondary │ │ Payments  │ │Outstanding│ │ Net      ││ │
│  │  │ Received  │ │ Sales     │ │ Made      │ │ Balance   │ │ Profit   ││ │
│  │  │ 15.0L     │ │ 22.0L     │ │ 11.5L     │ │ 3.5L      │ │ 4.2L     ││ │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └──────────┘│ │
│  │                                                                         │ │
│  │  Credit Utilization: ████████████░░░░░░░░  56% (14L / 25L limit)       │ │
│  │  Payment Status: ⚠ Rs. 1,50,000 overdue (past Net 30)                 │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  [View Stock Transfers] [View Orders] [View Payments] [View Returns]        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### 10.2.2 Sales Tab — Everything Sold by This Distributor

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  TAB: SALES                                                      [Export]   │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  PERIOD: [This Month v]   PLATFORM: [All v]   [Apply]                       │
│                                                                              │
│  ┌─ PRIMARY SALES (Stock Received from Company) ──────────────────────────┐ │
│  │                                                                         │ │
│  │  SUMMARY:                                                               │ │
│  │  Total STOs This Month:         8                                       │ │
│  │  Total Stock Value Received:    Rs. 15,00,000                           │ │
│  │  Total Units Received:          4,200 units                             │ │
│  │  Avg STO Value:                 Rs. 1,87,500                            │ │
│  │                                                                         │ │
│  │  RECENT STOCK TRANSFERS:                                                │ │
│  │  # | STO Number   | Date       | Items | Value      | Status           │ │
│  │  1 | STO-2026-012 | 2026-03-28 | 4     | 2,45,000   | COMPLETED        │ │
│  │  2 | STO-2026-010 | 2026-03-22 | 3     | 1,89,500   | COMPLETED        │ │
│  │  3 | STO-2026-008 | 2026-03-15 | 5     | 3,12,000   | COMPLETED        │ │
│  │  4 | STO-2026-014 | 2026-04-01 | 3     | 2,10,000   | IN_TRANSIT       │ │
│  │  [View All Stock Transfers →]                                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─ SECONDARY SALES (Sold on Platforms to End Customers) ─────────────────┐ │
│  │                                                                         │ │
│  │  SUMMARY:                                                               │ │
│  │  Total Orders This Month:       508                                     │ │
│  │  Total Gross Revenue:           Rs. 22,00,000                           │ │
│  │  Total Platform Fees:           Rs. -2,84,440                           │ │
│  │  Total Returns Value:           Rs. -1,39,920                           │ │
│  │  Net Revenue After Fees:        Rs. 17,75,640                           │ │
│  │  Units Sold:                    1,850 units                             │ │
│  │  Avg Order Value:               Rs. 4,331                              │ │
│  │                                                                         │ │
│  │  PLATFORM-WISE BREAKDOWN:                                               │ │
│  │  Platform  | Orders | Gross Sale  | Fees      | Returns | Net Revenue  │ │
│  │  Amazon    | 195    | 9,10,000    | -1,09,200 | -45,500 | 7,55,300    │ │
│  │  Flipkart  | 163    | 7,50,000    | -1,12,500 | -52,500 | 5,85,000    │ │
│  │  JioMart   | 150    | 5,40,000    | -62,740   | -41,920 | 4,35,340    │ │
│  │  ──────────────────────────────────────────────────────────────────     │ │
│  │  TOTAL     | 508    | 22,00,000   | -2,84,440 | -1,39,920| 17,75,640  │ │
│  │                                                                         │ │
│  │  TOP SELLING PRODUCTS (This Distributor):                               │ │
│  │  # | SKU     | Product          | Units Sold | Revenue  | Platform     │ │
│  │  1 | SKU-001 | T-Shirt Blue M   | 320        | 2,55,680 | Amz, Flip   │ │
│  │  2 | SKU-003 | Jeans Black 32   | 210        | 3,14,790 | Amz, Jio    │ │
│  │  3 | SKU-007 | Polo White L     | 185        | 1,84,815 | Flip, Jio   │ │
│  │  4 | SKU-012 | Kurta Red M      | 170        | 1,52,830 | Amz, Flip   │ │
│  │  5 | SKU-005 | Shorts Grey XL   | 145        | 1,01,355 | Jio         │ │
│  │  [View All Products →]                                                  │ │
│  │                                                                         │ │
│  │  DAILY SALES TREND (Last 30 Days):                                      │ │
│  │  Orders ▎                                                               │ │
│  │    25   ▎        ▄█                                                     │ │
│  │    20   ▎    ▄█ ▄██ ▄█     ▄█▄█                                        │ │
│  │    15   ▎▄█ ▄██ ███ ██ ▄█ ▄████ ▄█                                     │ │
│  │    10   ▎██ ███ ███ ██ ██ █████ ██ ▄█                                   │ │
│  │     5   ▎██ ███ ███ ██ ██ █████ ██ ██                                   │ │
│  │     0   ▎──────────────────────────────                                 │ │
│  │          Mar-02   Mar-09   Mar-16   Mar-23   Mar-30                     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─ STOCK UTILIZATION ────────────────────────────────────────────────────┐ │
│  │  Stock Received (All Time):      Rs. 85,00,000                          │ │
│  │  Stock Sold (All Time):          Rs. 72,00,000                          │ │
│  │  Utilization Rate:               84.7%                                  │ │
│  │  Current Unsold Stock Value:     Rs. 13,00,000                          │ │
│  │  Avg Days to Sell (Turnover):    18 days                                │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### 10.2.3 Inventory Tab — What Stock This Distributor Currently Holds

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  TAB: INVENTORY                                    [Sync Stock] [Export]     │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  SEARCH: [______________]   FILTER: [Category v] [Stock Level v]            │
│                                                                              │
│  ┌─ STOCK SUMMARY ───────────────────────────────────────────────────────┐  │
│  │  Total SKUs Held:          85                                          │  │
│  │  Total Units in Stock:     3,200                                       │  │
│  │  Total Stock Value:        Rs. 13,00,000                               │  │
│  │  Low Stock Items:          12 SKUs (below threshold)                   │  │
│  │  Out of Stock:             3 SKUs                                      │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ PRODUCT-WISE INVENTORY ──────────────────────────────────────────────┐  │
│  │ # | SKU     | Product        | In Stock | Committed | Available | Lvl │  │
│  │ 1 | SKU-001 | T-Shirt Blue M | 180      | 25        | 155      | OK  │  │
│  │ 2 | SKU-002 | T-Shirt Blue L | 90       | 12        | 78       | OK  │  │
│  │ 3 | SKU-003 | Jeans Black 32 | 15       | 8         | 7        | LOW │  │
│  │ 4 | SKU-005 | Shorts Grey XL | 0        | 0         | 0        | OUT │  │
│  │ 5 | SKU-007 | Polo White L   | 45       | 10        | 35       | OK  │  │
│  │ 6 | SKU-012 | Kurta Red M    | 22       | 5         | 17       | LOW │  │
│  │ ...                                                                    │  │
│  │                                                                        │  │
│  │ In Stock   = Physical units at distributor warehouse                   │  │
│  │ Committed  = Reserved for confirmed orders not yet shipped             │  │
│  │ Available  = Free to list/sell on platforms                            │  │
│  │ Lvl: OK (>50), LOW (<threshold), OUT (0)                              │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ PLATFORM-WISE STOCK ALLOCATION ─────────────────────────────────────┐   │
│  │  Shows how this distributor's stock is listed across platforms:        │   │
│  │                                                                        │   │
│  │  SKU-001 (T-Shirt Blue M) — Total Available: 155                      │   │
│  │  ├── Amazon:    Listed 60  | Buffer: 5  | Sellable: 55               │   │
│  │  ├── Flipkart:  Listed 50  | Buffer: 5  | Sellable: 45               │   │
│  │  ├── JioMart:   Listed 45  | Buffer: 5  | Sellable: 40               │   │
│  │  └── Unallocated: 15                                                  │   │
│  │                                                                        │   │
│  │  SKU-003 (Jeans Black 32) — Total Available: 7   ⚠ LOW STOCK         │   │
│  │  ├── Amazon:    Listed 3   | Buffer: 0  | Sellable: 3                │   │
│  │  ├── Flipkart:  Listed 2   | Buffer: 0  | Sellable: 2                │   │
│  │  ├── JioMart:   Listed 2   | Buffer: 0  | Sellable: 2                │   │
│  │  └── Unallocated: 0                                                   │   │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ INCOMING STOCK (In Transit) ─────────────────────────────────────────┐  │
│  │  # | STO Number   | Expected Date | Items | Value     | Status        │  │
│  │  1 | STO-2026-014 | 2026-04-03    | 3     | 2,10,000  | IN_TRANSIT    │  │
│  │  2 | STO-2026-016 | 2026-04-07    | 5     | 3,45,000  | SHIPPED       │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### 10.2.4 Shipping Tab — Where This Distributor Ships & Shipping Activity

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  TAB: SHIPPING                                                   [Export]   │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ┌─ SHIPPING ZONES / COVERAGE ───────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  This distributor ships to the following regions/zones:                 │  │
│  │                                                                        │  │
│  │  Zone        | States Covered                  | Avg Delivery | Orders │  │
│  │  Zone A      | Delhi, Haryana, Punjab          | 1-2 days     | 210    │  │
│  │  (Local)     |                                  |              |        │  │
│  │  Zone B      | UP, Rajasthan, Uttarakhand      | 2-3 days     | 165    │  │
│  │  (Regional)  |                                  |              |        │  │
│  │  Zone C      | MP, Gujarat, Maharashtra        | 3-5 days     | 88     │  │
│  │  (National)  |                                  |              |        │  │
│  │  Zone D      | South & East India              | 5-7 days     | 45     │  │
│  │  (Far)       |                                  |              |        │  │
│  │                                                                        │  │
│  │  Total Pincodes Serviceable: 12,500+                                   │  │
│  │  Warehouse Origin PIN: 110020 (Okhla, Delhi)                           │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ SHIPPING PROVIDERS USED ─────────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  Provider       | Platform      | Shipments | Avg Cost | Delivery %   │  │
│  │  Amazon Easy Ship| Amazon       | 195       | Rs. 45   | 98.2%        │  │
│  │  Flipkart Ekart | Flipkart     | 163       | Rs. 40   | 97.5%        │  │
│  │  Delhivery      | JioMart      | 80        | Rs. 55   | 96.8%        │  │
│  │  Ecom Express   | JioMart      | 70        | Rs. 50   | 95.0%        │  │
│  │                                                                        │  │
│  │  Delivery % = Delivered on time / Total shipped                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ SHIPMENT SUMMARY (This Month) ──────────────────────────────────────┐   │
│  │                                                                        │   │
│  │  Total Shipments:               508                                    │   │
│  │  Shipped On Time (before SLA):  482 (94.9%)                            │   │
│  │  Shipped Late (SLA breach):     18 (3.5%)                              │   │
│  │  Pending Shipment:              8 (1.6%)                               │   │
│  │  Avg Time to Ship:              6.2 hours from order confirmation      │   │
│  │  Avg Delivery Time:             3.1 days                               │   │
│  │  Total Shipping Cost:           Rs. 24,500                             │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ RECENT SHIPMENTS ────────────────────────────────────────────────────┐   │
│  │  # | Order ID        | Platform | Ship Date  | Destination  | Status  │   │
│  │  1 | AMZ-114-2678432 | Amazon   | 2026-03-31 | Delhi 110001 | Delivrd │   │
│  │  2 | OD427612345678  | Flipkart | 2026-03-31 | Jaipur 30201 | Transit │   │
│  │  3 | JIO-55667788    | JioMart  | 2026-03-31 | Noida 201301 | Delivrd │   │
│  │  4 | AMZ-114-2678435 | Amazon   | 2026-04-01 | Lucknow 2260 | Packed  │   │
│  │  5 | OD427612345680  | Flipkart | 2026-04-01 | Chandigrh 16 | Pending │   │
│  │  [View All Shipments →]                                                │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─ TOP SHIPPING DESTINATIONS (By Order Volume) ─────────────────────────┐  │
│  │  # | City / State         | Orders | % of Total | Avg Delivery Days   │  │
│  │  1 | Delhi NCR            | 125    | 24.6%      | 1.2 days            │  │
│  │  2 | Jaipur, Rajasthan    | 48     | 9.4%       | 2.5 days            │  │
│  │  3 | Lucknow, UP          | 42     | 8.3%       | 2.8 days            │  │
│  │  4 | Chandigarh           | 38     | 7.5%       | 1.8 days            │  │
│  │  5 | Gurugram, Haryana    | 35     | 6.9%       | 1.0 days            │  │
│  │  6 | Noida, UP            | 32     | 6.3%       | 1.1 days            │  │
│  │  7 | Ahmedabad, Gujarat   | 28     | 5.5%       | 3.5 days            │  │
│  │  8 | Dehradun, Uttarakhand| 22     | 4.3%       | 3.0 days            │  │
│  │  [View All Destinations →]                                             │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### 10.2.5 Payments Tab — All Money In & Out for This Distributor

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  TAB: PAYMENTS                                          [Sync] [Export]     │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  PERIOD: [This Month v]                                                      │
│                                                                              │
│  ┌─ PAYMENT TO COMPANY (Primary Sales — What Distributor Owes) ──────────┐  │
│  │                                                                        │  │
│  │  Total Stock Received (All Time):    Rs. 85,00,000                     │  │
│  │  Total Payments Made (All Time):     Rs. 81,50,000                     │  │
│  │  Current Outstanding Balance:        Rs. 3,50,000                      │  │
│  │  Credit Limit:                       Rs. 25,00,000                     │  │
│  │  Available Credit:                   Rs. 21,50,000                     │  │
│  │                                                                        │  │
│  │  PAYMENT AGING:                                                        │  │
│  │  ┌──────────────────────────────────────────────────────────────┐      │  │
│  │  │ Age Bucket      | Amount     | Status                       │      │  │
│  │  │ 0-15 days       | 1,50,000   | Within terms (Net 30)        │      │  │
│  │  │ 16-30 days      | 50,000     | Within terms (Net 30)        │      │  │
│  │  │ 31-60 days      | 1,00,000   | OVERDUE ⚠                   │      │  │
│  │  │ 60+ days        | 50,000     | CRITICAL OVERDUE ⛔          │      │  │
│  │  │ ─────────────────────────────────────────────────────────── │      │  │
│  │  │ TOTAL OUTSTANDING| 3,50,000  |                              │      │  │
│  │  └──────────────────────────────────────────────────────────────┘      │  │
│  │                                                                        │  │
│  │  RECENT PAYMENTS TO COMPANY:                                           │  │
│  │  # | Date       | Amount    | Invoice(s)     | Mode    | Status       │  │
│  │  1 | 2026-03-25 | 2,00,000  | STO-008,009    | NEFT    | CONFIRMED    │  │
│  │  2 | 2026-03-15 | 3,50,000  | STO-005,006,007| RTGS    | CONFIRMED    │  │
│  │  3 | 2026-03-01 | 2,50,000  | STO-003,004    | NEFT    | CONFIRMED    │  │
│  │  [View All Payments →]                                                 │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ PLATFORM SETTLEMENTS (Money Received from Platforms) ────────────────┐  │
│  │                                                                        │  │
│  │  SUMMARY (This Month):                                                 │  │
│  │  Platform  | Gross Sales | Fees       | Returns   | Net Settlement    │  │
│  │  Amazon    | 9,10,000    | -1,09,200  | -45,500   | 7,55,300          │  │
│  │  Flipkart  | 7,50,000    | -1,12,500  | -52,500   | 5,85,000          │  │
│  │  JioMart   | 5,40,000    | -62,740    | -41,920   | 4,35,340          │  │
│  │  ────────────────────────────────────────────────────────────────      │  │
│  │  TOTAL     | 22,00,000   | -2,84,440  | -1,39,920 | 17,75,640         │  │
│  │                                                                        │  │
│  │  SETTLEMENT TRANSACTIONS:                                              │  │
│  │  # | Date       | Platform  | Settlement ID | Amount    | Status      │  │
│  │  1 | 2026-03-28 | Amazon    | SETT-AMZ-012  | 1,85,000  | RECEIVED    │  │
│  │  2 | 2026-03-28 | Flipkart  | SETT-FK-009   | 1,42,000  | RECEIVED    │  │
│  │  3 | 2026-03-25 | JioMart   | SETT-JIO-006  | 95,000    | RECEIVED    │  │
│  │  4 | 2026-04-04 | Amazon    | SETT-AMZ-013  | 1,92,000  | PENDING     │  │
│  │  5 | 2026-04-04 | Flipkart  | SETT-FK-010   | 1,50,000  | PENDING     │  │
│  │  [View All Settlements →]                                              │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ FEE BREAKDOWN (This Month) ──────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  Fee Type           | Amazon    | Flipkart  | JioMart   | Total       │  │
│  │  Commission         | -72,800   | -82,500   | -37,800   | -1,93,100  │  │
│  │  Shipping Fee       | -18,000   | -15,200   | -12,960   | -46,160    │  │
│  │  Fixed/Closing Fee  | -3,900    | -3,260    | -3,000    | -10,160    │  │
│  │  GST on Fees        | -11,500   | -9,540    | -7,480    | -28,520    │  │
│  │  TCS/TDS            | -3,000    | -2,000    | -1,500    | -6,500     │  │
│  │  ────────────────────────────────────────────────────────────────     │  │
│  │  TOTAL FEES         | -1,09,200 | -1,12,500 | -62,740   | -2,84,440  │  │
│  │  Fees as % of Sales | 12.0%     | 15.0%     | 11.6%     | 12.9%      │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ PROFIT & LOSS (This Month) ──────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  Gross Sales (All Platforms):        Rs. 22,00,000                     │  │
│  │  - Platform Fees:                    Rs. -2,84,440                     │  │
│  │  - Return Losses:                    Rs. -1,39,920                     │  │
│  │  - Cost of Goods (paid to Company):  Rs. -13,50,000                    │  │
│  │  - Shipping Costs (self-ship):       Rs. -5,500                        │  │
│  │  ────────────────────────────────────────────────                      │  │
│  │  NET PROFIT:                         Rs. 4,20,140                      │  │
│  │  Margin:                             19.1%                             │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### 10.2.6 Returns Tab — All Returns for This Distributor

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  TAB: RETURNS                                                    [Export]   │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  PERIOD: [This Month v]   PLATFORM: [All v]   STATUS: [All v]               │
│                                                                              │
│  ┌─ RETURN SUMMARY ──────────────────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  Total Orders This Month:       508                                    │  │
│  │  Total Returns:                 38                                     │  │
│  │  Return Rate:                   7.5%                                   │  │
│  │  Return Value:                  Rs. 1,39,920                           │  │
│  │                                                                        │  │
│  │  BY PLATFORM:                                                          │  │
│  │  Platform  | Orders | Returns | Return % | Return Value | Refunded    │  │
│  │  Amazon    | 195    | 14      | 7.2%     | 52,500       | 48,000      │  │
│  │  Flipkart  | 163    | 12      | 7.4%     | 45,420       | 42,000      │  │
│  │  JioMart   | 150    | 12      | 8.0%     | 42,000       | 38,500      │  │
│  │  ─────────────────────────────────────────────────────────────         │  │
│  │  TOTAL     | 508    | 38      | 7.5%     | 1,39,920     | 1,28,500    │  │
│  │                                                                        │  │
│  │  BY REASON:                                                            │  │
│  │  Reason                | Count | % of Returns                          │  │
│  │  Size/Fit Issue        | 12    | 31.6%                                 │  │
│  │  Quality Defect        | 8     | 21.1%                                 │  │
│  │  Wrong Item Received   | 5     | 13.2%                                 │  │
│  │  Customer Changed Mind | 7     | 18.4%                                 │  │
│  │  Damaged in Transit    | 4     | 10.5%                                 │  │
│  │  Other                 | 2     | 5.3%                                  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ RECENT RETURNS ──────────────────────────────────────────────────────┐  │
│  │  # | Order ID        | Platform | Product      | Reason    | Status   │  │
│  │  1 | AMZ-114-2678450 | Amazon   | T-Shirt Blue | Size Issue| Received │  │
│  │  2 | OD427612345690  | Flipkart | Jeans Black  | Defect    | Refunded │  │
│  │  3 | JIO-55667800    | JioMart  | Polo White   | Wrong Item| In Transit│ │
│  │  4 | AMZ-114-2678455 | Amazon   | Kurta Red    | Damaged   | QC Check │  │
│  │  5 | OD427612345695  | Flipkart | Shorts Grey  | Changed   | Refunded │  │
│  │  [View All Returns →]                                                  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ RETURN DISPOSITION ──────────────────────────────────────────────────┐  │
│  │  After QC check, returned items are:                                   │  │
│  │                                                                        │  │
│  │  Disposition         | Count | % of Returns | Value                    │  │
│  │  Restocked (Good)    | 20    | 52.6%        | 72,000                   │  │
│  │  Liquidated (Damaged)| 10    | 26.3%        | 38,000                   │  │
│  │  Pending QC          | 5     | 13.2%        | 18,920                   │  │
│  │  Lost in Transit     | 3     | 7.9%         | 11,000                   │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### 10.2.7 Platform Performance Tab — Per-Platform Deep Dive

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  TAB: PLATFORM PERFORMANCE                                       [Export]   │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  PERIOD: [This Month v]                                                      │
│                                                                              │
│  ┌─ PLATFORM COMPARISON (This Distributor) ──────────────────────────────┐  │
│  │                                                                        │  │
│  │  Metric          | Amazon    | Flipkart  | JioMart   | TOTAL          │  │
│  │  ─────────────────────────────────────────────────────────────────    │  │
│  │  Orders          | 195       | 163       | 150       | 508            │  │
│  │  Gross Revenue   | 9,10,000  | 7,50,000  | 5,40,000  | 22,00,000     │  │
│  │  Avg Order Value | 4,667     | 4,601     | 3,600     | 4,331          │  │
│  │  Platform Fees   | 1,09,200  | 1,12,500  | 62,740    | 2,84,440      │  │
│  │  Fee %           | 12.0%     | 15.0%     | 11.6%     | 12.9%         │  │
│  │  Returns         | 14        | 12        | 12        | 38             │  │
│  │  Return %        | 7.2%      | 7.4%      | 8.0%      | 7.5%          │  │
│  │  Net Revenue     | 7,55,300  | 5,85,000  | 4,35,340  | 17,75,640     │  │
│  │  COGS            | 5,10,000  | 4,50,000  | 3,90,000  | 13,50,000     │  │
│  │  Net Profit      | 2,45,300  | 1,35,000  | 45,340    | 4,20,140*     │  │
│  │  Margin          | 26.9%     | 18.0%     | 8.4%      | 19.1%         │  │
│  │  ─────────────────────────────────────────────────────────────────    │  │
│  │  SLA Compliance  | 96.4%     | 95.1%     | 93.3%     | 95.1%         │  │
│  │  Avg Ship Time   | 5.2 hrs   | 6.8 hrs   | 7.1 hrs   | 6.2 hrs       │  │
│  │  Avg Delivery    | 2.8 days  | 3.0 days  | 3.5 days  | 3.1 days      │  │
│  │  Penalties       | Rs. 0     | Rs. 500   | Rs. 200   | Rs. 700        │  │
│  │                                                                        │  │
│  │  * Total includes shipping cost deduction                              │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ BEST SELLING ON EACH PLATFORM (This Distributor) ────────────────────┐  │
│  │                                                                        │  │
│  │  AMAZON — Top 3:                                                       │  │
│  │  1. SKU-003 Jeans Black 32   — 85 units  — Rs. 1,27,415              │  │
│  │  2. SKU-001 T-Shirt Blue M   — 72 units  — Rs. 57,528               │  │
│  │  3. SKU-012 Kurta Red M      — 55 units  — Rs. 49,445               │  │
│  │                                                                        │  │
│  │  FLIPKART — Top 3:                                                     │  │
│  │  1. SKU-001 T-Shirt Blue M   — 68 units  — Rs. 54,332               │  │
│  │  2. SKU-007 Polo White L     — 60 units  — Rs. 59,940               │  │
│  │  3. SKU-003 Jeans Black 32   — 52 units  — Rs. 77,948               │  │
│  │                                                                        │  │
│  │  JIOMART — Top 3:                                                      │  │
│  │  1. SKU-005 Shorts Grey XL   — 65 units  — Rs. 45,435               │  │
│  │  2. SKU-007 Polo White L     — 48 units  — Rs. 47,952               │  │
│  │  3. SKU-001 T-Shirt Blue M   — 40 units  — Rs. 31,960               │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ LISTING HEALTH (Per Platform) ───────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  Platform  | Active Listings | Suppressed | Out of Stock | Total       │  │
│  │  Amazon    | 62              | 3          | 5            | 70          │  │
│  │  Flipkart  | 58              | 2          | 4            | 64          │  │
│  │  JioMart   | 50              | 1          | 6            | 57          │  │
│  │                                                                        │  │
│  │  Suppressed = listing hidden by platform due to pricing/quality issues │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### 10.2.8 Activity Log Tab — Complete Audit Trail for This Distributor

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  TAB: ACTIVITY LOG                                     [Filter] [Export]    │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  Shows EVERY action related to this distributor — orders, shipments,         │
│  stock transfers, payments, returns, platform events, user actions.          │
│                                                                              │
│  FILTERS: [Date From] [Date To] [Activity Type v] [Platform v] [User v]    │
│                                                                              │
│  Activity Types: [All] [Orders] [Shipments] [Stock Transfers] [Payments]    │
│                  [Returns] [Platform Events] [Inventory Changes] [User]     │
│                                                                              │
│  ┌─ ACTIVITY FEED ───────────────────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  TODAY (2026-04-01)                                                    │  │
│  │  ─────────────────                                                     │  │
│  │  14:32  ORDER     AMZ-114-2678460 received from Amazon (Rs. 1,598)    │  │
│  │                   2 items — T-Shirt Blue M x1, Jeans Black 32 x1      │  │
│  │                                                                        │  │
│  │  14:15  SHIPMENT  OD427612345680 shipped via Ekart (Flipkart)         │  │
│  │                   Tracking: FMPP1234567890 → Chandigarh 160017        │  │
│  │                                                                        │  │
│  │  13:45  INVENTORY SKU-003 stock updated: 18 → 15 (3 committed)        │  │
│  │                   Reason: Order AMZ-114-2678458 confirmed              │  │
│  │                                                                        │  │
│  │  12:00  STOCK_IN  STO-2026-014 dispatched from Company warehouse      │  │
│  │                   3 items, Rs. 2,10,000 — Expected: 2026-04-03        │  │
│  │                                                                        │  │
│  │  11:30  ORDER     JIO-55667810 received from JioMart (Rs. 749)        │  │
│  │                   1 item — Polo White L x1                             │  │
│  │                                                                        │  │
│  │  10:45  RETURN    AMZ-114-2678450 return received & QC passed         │  │
│  │                   T-Shirt Blue (Size Issue) — Restocked               │  │
│  │                                                                        │  │
│  │  10:00  SHIPMENT  AMZ-114-2678455 shipped via Amazon Easy Ship        │  │
│  │                   Tracking: AMZN1234567 → Delhi 110001                │  │
│  │                                                                        │  │
│  │  09:30  PAYMENT   Platform settlement received from Amazon            │  │
│  │                   SETT-AMZ-012: Rs. 1,85,000 credited to bank         │  │
│  │                                                                        │  │
│  │  09:00  ORDER     15 new orders synced (Amz: 8, Flip: 4, Jio: 3)     │  │
│  │                   Total value: Rs. 58,450                              │  │
│  │                                                                        │  │
│  │  YESTERDAY (2026-03-31)                                                │  │
│  │  ──────────────────────                                                │  │
│  │  18:00  PLATFORM  Flipkart sync completed — 6 new orders pulled       │  │
│  │  17:30  SHIPMENT  22 orders shipped today (Amz: 10, Flip: 8, Jio: 4) │  │
│  │  16:00  INVENTORY Auto-stock sync pushed to all platforms              │  │
│  │  15:00  PAYMENT   Rs. 2,00,000 paid to Company (NEFT) for STO-008,009│  │
│  │  14:00  RETURN    OD427612345690 return initiated by customer         │  │
│  │  10:00  USER      Rahul Sharma logged in                              │  │
│  │  09:00  ORDER     18 new orders synced across all platforms            │  │
│  │                                                                        │  │
│  │  [Load More ↓]                                                         │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ ACTIVITY SUMMARY (This Month) ──────────────────────────────────────┐   │
│  │                                                                        │   │
│  │  Activity Type      | Count  | Key Stats                              │   │
│  │  Orders Received    | 508    | Avg 16.9/day                           │   │
│  │  Shipments Made     | 500    | 94.9% on-time SLA                     │   │
│  │  Returns Processed  | 38     | 7.5% return rate                      │   │
│  │  Stock Transfers    | 8      | Rs. 15L received                      │   │
│  │  Payments to Company| 3      | Rs. 8L paid                           │   │
│  │  Platform Settlements| 12    | Rs. 17.75L received                   │   │
│  │  Inventory Updates  | 1,240  | Avg 41/day (auto + manual)            │   │
│  │  Platform Syncs     | 2,700  | Avg 90/day (every 5 min x 3 platforms)│   │
│  │  User Logins        | 45     | 3 active users                        │   │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 10.3 Add Distributor Flow

```
START
  |
  +-- Company Admin clicks "+ Add Distributor"
  |
  +-- Fill distributor form:
  |     - Business name, GSTIN, PAN
  |     - Region / coverage area
  |     - Warehouse address(es)
  |     - Contact details
  |     - Bank details (for payment tracking)
  |     - Credit limit (max outstanding amount allowed)
  |     - Payment terms (e.g., Net 30, Net 60)
  |
  +-- System validates:
  |     +-- GSTIN format valid?
  |     +-- GSTIN not already registered?
  |     +-- All required fields filled?
  |
  +-- Create distributor record
  |
  +-- Create default user accounts:
  |     - Distributor Manager account (auto-generated credentials)
  |     - Send login credentials via email
  |
  +-- Distributor can now:
  |     - Login to the app
  |     - Connect their platform accounts
  |     - Receive stock transfers
  |     - Start processing orders
  |
  END
```

---

## 11. Module 4: Platform Management

### 11.1 Platform Connection Dashboard

```
┌──────────────────────────────────────────────────────────────────────────┐
│  PLATFORM CONNECTIONS  (Distributor: NorthStar Distribution)             │
│  ────────────────────────────────────────────────────────────            │
│                                                                          │
│  ┌─────────────────────────┐  ┌─────────────────────────┐              │
│  │  AMAZON                 │  │  FLIPKART               │              │
│  │  Status: CONNECTED      │  │  Status: CONNECTED      │              │
│  │  Seller ID: A2XXXXX     │  │  Seller ID: FKXXXXX     │              │
│  │  Last Sync: 2 min ago   │  │  Last Sync: 5 min ago   │              │
│  │  Orders Today: 23       │  │  Orders Today: 18       │              │
│  │  [Configure] [Sync Now] │  │  [Configure] [Sync Now] │              │
│  └─────────────────────────┘  └─────────────────────────┘              │
│                                                                          │
│  ┌─────────────────────────┐  ┌─────────────────────────┐              │
│  │  MEESHO                 │  │  MYNTRA                  │              │
│  │  Status: NOT CONNECTED  │  │  Status: CONNECTED       │              │
│  │                         │  │  Partner ID: MYNXXXXX    │              │
│  │  [Connect Now]          │  │  Last Sync: 10 min ago   │              │
│  │                         │  │  Orders Today: 12        │              │
│  │                         │  │  [Configure] [Sync Now]  │              │
│  └─────────────────────────┘  └─────────────────────────┘              │
│                                                                          │
│  ┌─────────────────────────┐  ┌─────────────────────────┐              │
│  │  JIOMART                │  │  SNAPDEAL                │              │
│  │  Status: CONNECTED      │  │  Status: ERROR           │              │
│  │  Seller ID: JIOXXXXX    │  │  Last Error: Token Expd  │              │
│  │  Last Sync: 3 min ago   │  │  [Reconnect] [View Logs] │              │
│  │  Orders Today: 8        │  │                          │              │
│  │  [Configure] [Sync Now] │  │                          │              │
│  └─────────────────────────┘  └─────────────────────────┘              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Platform Connection Flow

```
START
  |
  +-- Distributor Manager clicks "Connect Now" for a platform
  |
  +-- System shows platform-specific connection form:
  |
  |     AMAZON:
  |     - Seller Central Credentials / SP-API keys
  |     - Marketplace ID (IN = A21TJRUUN4KGV)
  |     - Refresh Token
  |     - Client ID / Client Secret
  |
  |     FLIPKART:
  |     - Seller API Key
  |     - Seller API Secret
  |     - Seller Account ID
  |
  |     MEESHO:
  |     - Supplier API Token
  |     - Supplier ID
  |
  |     (Each platform has different credentials)
  |
  +-- User enters credentials
  |
  +-- System validates by making a test API call:
  |     +-- SUCCESS -> Store credentials (encrypted)
  |     |              Mark platform as CONNECTED
  |     |              Start initial sync (pull orders, listings)
  |     |
  |     +-- FAILURE -> Show error: "Invalid credentials. Please check and retry."
  |
  +-- Initial Sync:
  |     1. Pull existing listings from platform
  |     2. Map platform listings to product catalog
  |     3. Pull recent orders (last 30 days)
  |     4. Pull return/refund data
  |     5. Set up webhook/polling for new orders
  |
  END
```

### 11.3 Platform Configuration

```
PER-PLATFORM SETTINGS:

  GENERAL:
  - Sync frequency (how often to pull new orders)
  - Auto-accept orders (yes/no)
  - Default warehouse for fulfillment
  - Shipping provider preferences

  LISTING SETTINGS:
  - Auto-sync product catalog to platform (yes/no)
  - Price markup rules (e.g., Distributor price + 40% margin)
  - Listing template (title format, description format)

  INVENTORY SETTINGS:
  - Inventory buffer (e.g., keep 5 units reserved, don't list all)
  - Auto-sync stock levels to platform
  - Low stock threshold per platform

  SHIPPING SETTINGS:
  - Shipping provider (platform fulfillment vs self-ship)
  - Shipping zone restrictions
  - Packaging preferences

  RETURN SETTINGS:
  - Auto-accept returns (yes/no)
  - Return quality check required (yes/no)
  - Restocking rules
```

---

## 12. Module 5: Primary Sales (Company to Distributor)

### 12.1 Overview

```
PRIMARY SALES = Company sending stock to Distributors.

This is how distributors GET their inventory.
Without Primary Sales, distributors have nothing to sell on platforms.

FLOW:
  Company decides to send stock to Distributor
       |
       v
  Create Stock Transfer Order (STO)
       |
       v
  Prepare shipment at Company warehouse
       |
       v
  Ship to Distributor warehouse
       |
       v
  Distributor receives and acknowledges
       |
       v
  Distributor's inventory updated
       |
       v
  Distributor can now list/sell on platforms
```

### 12.2 Stock Transfer Order (STO) Creation

```
START
  |
  +-- Company Admin clicks "Create Stock Transfer"
  |
  +-- Select Distributor: [NorthStar Distribution v]
  |
  +-- Add Products:
  |     +-------------------------------------------------+
  |     | # | SKU     | Product        | Avail | Qty | Price |
  |     | 1 | SKU-001 | T-Shirt Blue M | 500   | 100 | 399   |
  |     | 2 | SKU-002 | T-Shirt Blue L | 300   | 80  | 399   |
  |     | 3 | SKU-003 | Jeans Black 32 | 200   | 50  | 749   |
  |     +-------------------------------------------------+
  |
  |     Avail = Stock available in Company warehouse
  |     Qty = Quantity to transfer to Distributor
  |     Price = Distributor price from product catalog
  |
  +-- Auto-calculated:
  |     Subtotal:     100x399 + 80x399 + 50x749 = Rs. 1,09,370
  |     GST (18%):    Rs. 19,686.60
  |     Grand Total:  Rs. 1,29,056.60
  |
  +-- Payment Terms: [Net 30 v]
  |
  +-- System validates:
  |     +-- All quantities > 0?
  |     +-- Sufficient stock in Company warehouse?
  |     +-- Distributor within credit limit?
  |     +-- Distributor account active?
  |
  +-- Create STO (status = CREATED)
  |
  +-- Generate Invoice (PDF)
  |
  +-- Notify Distributor: "New stock transfer STO-2026-001 created"
  |
  END
```

### 12.3 Stock Transfer Lifecycle

```
  ┌──────────┐
  │ CREATED  │  (Company creates STO)
  └────┬─────┘
       |
       v
  ┌──────────┐
  │ APPROVED │  (Company Admin approves)
  └────┬─────┘
       |
       v
  ┌──────────┐
  │ PACKED   │  (Warehouse packs items)
  └────┬─────┘
       |
       v
  ┌──────────┐
  │ SHIPPED  │  (Dispatched from Company warehouse)
  └────┬─────┘
       |     Tracking number + logistics details
       v
  ┌──────────┐
  │IN_TRANSIT│  (On the way to Distributor)
  └────┬─────┘
       |
       v
  ┌──────────┐
  │ RECEIVED │  (Distributor acknowledges receipt)
  └────┬─────┘
       |     Distributor verifies quantities
       |     Any discrepancy flagged
       v
  ┌──────────┐
  │COMPLETED │  (Stock added to Distributor inventory)
  └──────────┘

  At any point:
  ┌──────────┐
  │CANCELLED │  (Before SHIPPED — can cancel)
  └──────────┘
```

### 12.4 Distributor Receives Stock

```
START
  |
  +-- Distributor receives physical shipment
  |
  +-- Distributor Manager opens app -> "Pending Receipts"
  |
  +-- Sees STO-2026-001 (status: SHIPPED)
  |
  +-- Clicks "Acknowledge Receipt"
  |
  +-- Verifies each item:
  |     +----------------------------------------------------+
  |     | SKU     | Expected | Received | Condition | Status  |
  |     | SKU-001 | 100      | 100      | Good      | OK      |
  |     | SKU-002 | 80       | 78       | Good      | Short-2 |
  |     | SKU-003 | 50       | 50       | 3 Damaged | Damaged |
  |     +----------------------------------------------------+
  |
  +-- If discrepancy:
  |     +-- Create discrepancy report
  |     +-- Upload photos of damaged items
  |     +-- Notify Company Admin
  |     +-- Only GOOD items added to Distributor inventory
  |
  +-- START DATABASE TRANSACTION:
  |     Step A: Deduct from Company warehouse inventory
  |             (already done at SHIPPED stage)
  |     Step B: Add to Distributor warehouse inventory
  |             SKU-001: +100 units
  |             SKU-002: +78 units (2 short)
  |             SKU-003: +47 units (3 damaged)
  |     Step C: Update STO status = COMPLETED
  |     Step D: Log in audit trail
  |     COMMIT
  |
  +-- Distributor now has stock to sell on platforms
  |
  END
```

### 12.5 Primary Sales List View

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  STOCK TRANSFERS (Primary Sales)                   [+ Create Transfer]     │
│  ────────────────────────────────────────────────────────────               │
│                                                                              │
│  FILTERS: [Distributor v] [Status v] [Date From] [Date To] [Search]        │
│                                                                              │
│  #  | STO Number    | Distributor    | Items | Total Value  | Status    |Act│
│  1  | STO-2026-001  | NorthStar      | 3     | 1,29,056     | COMPLETED |[V]│
│  2  | STO-2026-002  | SouthWave      | 5     | 2,45,000     | IN_TRANSIT|[V]│
│  3  | STO-2026-003  | WestEnd        | 2     | 89,500       | APPROVED  |[V]│
│  4  | STO-2026-004  | NorthStar      | 4     | 1,78,200     | CREATED   |[V]│
│                                                                              │
│  Showing 1-20 of 45       [<- Prev] [1] [2] [3] [Next ->]                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Module 6: Secondary Sales / Order Management (Platform Orders)

### 13.1 Unified Order View

```
THIS IS THE CORE VALUE: All platform orders in ONE place.

┌──────────────────────────────────────────────────────────────────────────────┐
│  ALL ORDERS (Unified View)                                [Export] [Sync]   │
│  ────────────────────────────────────────────────────────────────           │
│                                                                              │
│  FILTERS:                                                                    │
│  [Platform v] [Distributor v] [Status v] [Date From] [Date To] [Search]    │
│                                                                              │
│  PLATFORM TABS:  [All(85)] [Amazon(23)] [Flipkart(18)] [Meesho(15)]       │
│                  [Myntra(12)] [JioMart(8)] [Snapdeal(9)]                   │
│                                                                              │
│  # |Platform |Order ID        |Customer     |Items|Amount |Status   |Action │
│  1 |Amazon   |AMZ-114-2678432 |Priya S.     |2    |1,598  |PENDING  |[View] │
│  2 |Flipkart |OD427612345678  |Rahul M.     |1    |1,499  |CONFIRMED|[View] │
│  3 |Meesho   |MSH-98765432    |Anita K.     |3    |2,397  |PENDING  |[View] │
│  4 |Myntra   |MYN-11223344    |Deepak R.    |1    |799    |SHIPPED  |[View] │
│  5 |Amazon   |AMZ-114-2678433 |Suresh P.    |2    |2,998  |DELIVERED|[View] │
│  6 |JioMart  |JIO-55667788    |Kavita D.    |1    |1,249  |PENDING  |[View] │
│  7 |Flipkart |OD427612345679  |Amit T.      |1    |799    |RETURNED |[View] │
│  8 |Snapdeal |SD-44332211     |Neha G.      |2    |1,598  |CONFIRMED|[View] │
│                                                                              │
│  Showing 1-20 of 85       [<- Prev] [1] [2] [3] [Next ->]                  │
│                                                                              │
│  Color coding: Amazon=Orange, Flipkart=Blue, Meesho=Pink,                   │
│                Myntra=Red, JioMart=Green, Snapdeal=Yellow                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 13.2 How Orders Are Pulled from Platforms

```
ORDER SYNC PROCESS:

  ┌──────────────────────────────────────────────────────────────────────┐
  │                                                                      │
  │  PLATFORM APIs                      OUR SYSTEM                      │
  │                                                                      │
  │  Amazon SP-API ──────┐                                              │
  │  Flipkart API ───────┤                                              │
  │  Meesho API ─────────┤         ┌──────────────────┐                 │
  │  Myntra API ─────────┼────────►│  SYNC SERVICE    │                 │
  │  JioMart API ────────┤         │  (Runs every     │                 │
  │  Snapdeal API ───────┘         │   5 minutes)     │                 │
  │                                └────────┬─────────┘                 │
  │                                         │                           │
  │                                         │ For each platform:        │
  │                                         │ 1. Call GET orders API    │
  │                                         │ 2. Transform to unified  │
  │                                         │    format                 │
  │                                         │ 3. Check if order exists │
  │                                         │    (by platform_order_id)│
  │                                         │ 4. If new -> INSERT      │
  │                                         │ 5. If exists -> UPDATE   │
  │                                         │    status if changed     │
  │                                         │                           │
  │                                         ▼                           │
  │                                ┌──────────────────┐                 │
  │                                │  UNIFIED ORDERS  │                 │
  │                                │  TABLE           │                 │
  │                                └──────────────────┘                 │
  │                                                                      │
  └──────────────────────────────────────────────────────────────────────┘

SYNC FREQUENCY:
  - Orders:    Every 5 minutes (configurable per platform)
  - Inventory: Push to platforms when stock changes
  - Returns:   Every 15 minutes
  - Payments:  Every 6 hours
```

### 13.3 Order Detail Page

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ORDER DETAIL                                                            │
│  ────────────                                                            │
│                                                                          │
│  Platform: AMAZON          Platform Order ID: AMZ-114-2678432            │
│  Unified Order ID: ORD-2026-04-001                                       │
│  Distributor: NorthStar Distribution                                     │
│  Status: CONFIRMED                                                       │
│                                                                          │
│  CUSTOMER DETAILS (from platform):                                       │
│  Name:     Priya Sharma                                                  │
│  Address:  123, MG Road, New Delhi - 110001                              │
│  Phone:    +91-98XXXXXXXX (masked per platform rules)                    │
│                                                                          │
│  ORDER ITEMS:                                                            │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │ # | SKU     | Product        | Qty | Price  | Platform Fee | Net│     │
│  │ 1 | SKU-001 | T-Shirt Blue M | 1   | 799    | 95.88 (12%) | 703│     │
│  │ 2 | SKU-003 | Jeans Black 32 | 1   | 1,499  | 179.88 (12%)| 1319│    │
│  │                                                                 │     │
│  │ Subtotal:        2,298                                          │     │
│  │ Platform Fees:   -275.76                                        │     │
│  │ Shipping Fee:    -50.00                                         │     │
│  │ Net Receivable:  1,972.24                                       │     │
│  └─────────────────────────────────────────────────────────────────┘     │
│                                                                          │
│  TIMELINE:                                                               │
│  +-- 2026-04-01 09:15 - Order placed by customer on Amazon               │
│  +-- 2026-04-01 09:20 - Synced to MPEMS                                  │
│  +-- 2026-04-01 10:00 - Status: CONFIRMED                                │
│                                                                          │
│  ACTIONS:                                                                │
│  [Accept Order] [Process Fulfillment] [Cancel Order] [View on Platform]  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 13.4 Order Status Lifecycle (Unified)

```
  Platform sends order
       |
       v
  ┌──────────┐
  │ PENDING  │  (Order received, awaiting confirmation)
  └────┬─────┘
       |
       v
  ┌──────────┐
  │CONFIRMED │  (Accepted for processing)
  └────┬─────┘
       |
       v
  ┌──────────┐
  │PROCESSING│  (Being picked and packed)
  └────┬─────┘
       |
       v
  ┌──────────┐
  │ SHIPPED  │  (Handed to courier, tracking generated)
  └────┬─────┘
       |
       v
  ┌──────────┐
  │IN_TRANSIT│  (On the way to customer)
  └────┬─────┘
       |
       +---------+
       |         |
       v         v
  ┌──────────┐ ┌──────────┐
  │DELIVERED │ │  FAILED  │  (Delivery attempt failed)
  └────┬─────┘ └────┬─────┘
       |             |
       |        Retry or Return
       |             |
       v             v
  ┌──────────┐ ┌──────────┐
  │ COMPLETE │ │ RTO      │  (Return to Origin)
  └──────────┘ └──────────┘

  At any point before SHIPPED:
  ┌──────────┐
  │CANCELLED │
  └──────────┘

  After DELIVERED:
  ┌──────────┐
  │ RETURNED │  (Customer initiated return)
  └──────────┘

  NOTE: Each platform uses different status names.
  The Integration Layer maps them to this unified lifecycle.
```

---

## 14. Module 7: Inventory Management (Multi-Level)

### 14.1 Three Levels of Inventory

```
INVENTORY EXISTS AT THREE LEVELS:

  LEVEL 1: COMPANY WAREHOUSE (Central Stock)
  ────────────────────��────────────────────
  This is the manufacturing/central stock.
  Company ships FROM here to Distributors.

  LEVEL 2: DISTRIBUTOR WAREHOUSE (Regional Stock)
  ────────────────────────────────────────────────
  Each distributor has their own warehouse.
  They receive stock from Company (Primary Sale).
  They ship FROM here to fulfill platform orders (Secondary Sale).

  LEVEL 3: PLATFORM-LEVEL INVENTORY (Virtual/Listed Stock)
  ─────────────────────────────────────────────────────────
  Each platform shows available stock for each product.
  This is the quantity listed on Amazon/Flipkart/etc.
  May be different from actual warehouse stock (buffer/reserve).

  RELATIONSHIP:

  ┌───────────────────────────────────────────────────────────────┐
  │  COMPANY WAREHOUSE                                            │
  │  SKU-001: 500 units total                                     │
  │                                                               │
  │     |--- Transferred to Dist A: 200 units                    │
  │     |--- Transferred to Dist B: 150 units                    │
  │     |--- Remaining: 150 units                                │
  │                                                               │
  │  DISTRIBUTOR A WAREHOUSE                                      │
  │  SKU-001: 200 units received                                  │
  │     |--- Listed on Amazon:   80 units                         │
  │     |--- Listed on Flipkart: 60 units                         │
  │     |--- Listed on JioMart:  40 units                         │
  │     |--- Buffer/Reserve:     20 units                         │
  │                                                               │
  │  DISTRIBUTOR B WAREHOUSE                                      │
  │  SKU-001: 150 units received                                  │
  │     |--- Listed on Flipkart: 70 units                         │
  │     |--- Listed on Meesho:   50 units                         │
  │     |--- Listed on Myntra:   20 units                         │
  │     |--- Buffer/Reserve:     10 units                         │
  └───────────────────────────────────────────────────────────────┘
```

### 14.2 Inventory Dashboard

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  INVENTORY MANAGEMENT                              [Sync All] [Export CSV]  │
│  ─────────────────────────────────────────────────────────────               │
│                                                                              │
│  VIEW: [Company Warehouse] [Distributor Warehouse v] [Platform Stock v]     │
│                                                                              │
│  === DISTRIBUTOR WAREHOUSE: NorthStar Distribution ===                      │
│                                                                              │
│  FILTERS: [Category v] [Stock Status v] [Platform v] [Search SKU/Name]     │
│                                                                              │
│  # |SKU     |Product        |Warehouse|Amazon|Flipkart|JioMart|Total |Status│
│  1 |SKU-001 |T-Shirt Blue M |200      |80    |60      |40     |180   |OK    │
│  2 |SKU-002 |T-Shirt Blue L |150      |50    |50      |30     |130   |OK    │
│  3 |SKU-003 |Jeans Black 32 |30       |15    |10      |5      |30    |LOW   │
│  4 |SKU-004 |Sneakers Wht 9 |0        |0     |0       |0      |0     |OUT   │
│                                                                              │
│  "Warehouse" = Physical stock in distributor warehouse                       │
│  "Amazon/Flipkart/JioMart" = Stock listed on each platform                  │
│  "Total" = Sum of platform-listed stock                                      │
│  NOTE: Warehouse >= Total (buffer stock not listed anywhere)                 │
│                                                                              │
│  LEGEND: OK = Above threshold | LOW = Below threshold | OUT = Zero stock    │
│                                                                              │
│  Showing 1-20 of 120       [<- Prev] [1] [2] [3] [Next ->]                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 14.3 Inventory Sync to Platforms

```
WHEN INVENTORY CHANGES, SYNC TO PLATFORMS:

START
  |
  +-- Inventory change occurs (order fulfilled, stock received, adjustment)
  |
  +-- System calculates new available stock per platform:
  |     For each product affected:
  |       warehouse_stock = current physical stock
  |       buffer = configured buffer quantity
  |       total_available = warehouse_stock - buffer
  |
  |       Distribute across platforms based on rules:
  |         Option A: EQUAL SPLIT
  |           Each platform gets total_available / num_platforms
  |
  |         Option B: WEIGHTED SPLIT (by sales velocity)
  |           Amazon (40% of sales)  -> 40% of stock
  |           Flipkart (30%)         -> 30% of stock
  |           JioMart (30%)          -> 30% of stock
  |
  |         Option C: MANUAL ALLOCATION
  |           User manually sets stock per platform
  |
  +-- Push updated inventory to each platform via API:
  |
  |     AMAZON:
  |       POST /feeds (Inventory Feed)
  |       { "sku": "SKU-001", "quantity": 80 }
  |
  |     FLIPKART:
  |       POST /listings/update
  |       { "sku": "SKU-001", "stock": 60 }
  |
  |     (Each platform has different API format)
  |
  +-- Log sync result:
  |     +-- SUCCESS -> Mark as synced, update last_sync_time
  |     +-- FAILURE -> Retry after 5 minutes, alert admin after 3 failures
  |
  END
```

### 14.4 Inventory Adjustment

```
START
  |
  +-- Staff discovers stock discrepancy (damage, loss, miscount)
  |
  +-- Opens Inventory -> Finds item -> Clicks "Adjust Stock"
  |
  +-- Fills adjustment form:
  |     - Adjustment Type: [Add / Deduct]
  |     - Quantity: [number]
  |     - Reason: [Damage / Loss / Miscount / Return Received / Other]
  |     - Notes: [free text with details]
  |     - Upload proof (photo of damaged goods, etc.)
  |
  +-- System validates:
  |     +-- Quantity > 0?
  |     +-- Reason provided?
  |     +-- If deduct: new stock >= 0?
  |
  +-- START TRANSACTION:
  |     Step A: Update warehouse inventory
  |     Step B: Recalculate platform allocations
  |     Step C: Push updated stock to platforms
  |     Step D: Log adjustment in audit trail
  |     COMMIT
  |
  +-- If stock fell below threshold:
  |     +-- Send low stock alert
  |     +-- Check if any platform needs stock update
  |
  END
```

---

## 15. Module 8: Fulfillment Process (Per-Platform Shipping)

### 15.1 Platform-Specific Fulfillment Rules

```
EACH PLATFORM HAS DIFFERENT FULFILLMENT REQUIREMENTS:

┌──────────────────────────────────────────────────────────────────────────┐
│  Platform  │ Ship By SLA    │ Label Format   │ Courier              │
├──────────────────────────────────────────────────────────────────────────┤
│  Amazon    │ Same/Next day  │ Amazon label   │ Easy Ship / FBA /    │
│            │                │ (SP-API gen)   │ Self-Ship             │
├──────────────────────────────────────────────────────────────────────────┤
│  Flipkart  │ 1-2 days       │ Flipkart label │ Flipkart Logistics / │
│            │                │ (API generated)│ Self-Ship             │
├──────────────────────────────────────────────────────────────────────────┤
│  Meesho    │ 2 days         │ Meesho label   │ Meesho Logistics     │
│            │                │ (auto-gen)     │ (mandatory)           │
├──────────────────────────────────────────────────────────────────────────┤
│  Myntra    │ 1 day          │ Myntra label   │ Myntra Logistics     │
│            │                │ (partner API)  │ (mandatory)           │
├──────────────────────────────────────────────────────────────────────────┤
│  JioMart   │ 1-2 days       │ JioMart label  │ JioMart Logistics /  │
│            │                │ (API generated)│ Self-Ship             │
├──────────────────────────────────────────────────────────────────────────┤
│  Snapdeal  │ 2 days         │ Snapdeal label │ Snapdeal Logistics / │
│            │                │ (API generated)│ Self-Ship             │
└──────────────────────────────────────────────────────────────────────────┘
```

### 15.2 Unified Fulfillment Flow

```
START
  |
  +-- Warehouse Staff opens "Orders to Fulfill" page
  |
  +-- System shows orders grouped by platform and priority:
  |
  |     URGENT (Ship by today):
  |     +-- AMZ-114-2678432  | Amazon  | 2 items | Ship by 4:00 PM
  |     +-- OD427612345678   | Flipkart| 1 item  | Ship by 6:00 PM
  |
  |     NORMAL (Ship by tomorrow):
  |     +-- MSH-98765432     | Meesho  | 3 items | Ship by tomorrow 2 PM
  |     +-- JIO-55667788     | JioMart | 1 item  | Ship by tomorrow 4 PM
  |
  +-- Staff selects order(s) to fulfill
  |     (Can select multiple orders for batch processing)
  |
  +-- PICK LIST generated:
  |     ┌──────────────────────────────────────────────────┐
  |     │  PICK LIST                                       │
  |     │  ─────────                                       │
  |     │  Order: AMZ-114-2678432                          │
  |     │                                                  │
  |     │  # | SKU     | Product        | Qty | Location  │
  |     │  1 | SKU-001 | T-Shirt Blue M | 1   | Rack A-3  │
  |     │  2 | SKU-003 | Jeans Black 32 | 1   | Rack B-7  │
  |     │                                                  │
  |     │  [Print Pick List]                               │
  |     └──────────────────────────────────────────────────┘
  |
  +-- Staff picks items from warehouse
  |
  +-- Staff clicks "Items Picked" -> Moves to PACKING
  |
  +-- PACKING:
  |     +-- System generates shipping label via PLATFORM API:
  |     |
  |     |     AMAZON: Call SP-API createFulfillmentOrder or getShipment
  |     |     FLIPKART: Call /shipments/create
  |     |     MEESHO: Call /shipments/generate-label
  |     |     (Each platform has different API for label generation)
  |     |
  |     +-- Print shipping label
  |     +-- Pack items with label
  |     +-- Scan/enter tracking number
  |
  +-- Staff clicks "Packed & Ready"
  |
  +-- DISPATCH:
  |     +-- Generate manifest (per platform requirement)
  |     +-- Hand over to courier
  |     +-- Update status via platform API:
  |     |     AMAZON: POST confirmShipment
  |     |     FLIPKART: POST /shipments/dispatch
  |     |     MEESHO: POST /shipments/dispatch
  |
  +-- START TRANSACTION:
  |     Step A: Deduct from distributor warehouse inventory
  |     Step B: Update platform-level inventory
  |     Step C: Sync updated stock to all platforms
  |     Step D: Update order status = SHIPPED
  |     Step E: Log in audit trail
  |     COMMIT
  |
  +-- Notify: "Order AMZ-114-2678432 shipped. Tracking: XXXXX"
  |
  END
```

### 15.3 Batch Fulfillment

```
FOR HIGH VOLUME DISTRIBUTORS:

  Process multiple orders at once:

  1. Select all orders to fulfill (checkbox selection)
  2. Generate combined PICK LIST (all items across orders)
  3. Pick all items in one warehouse pass
  4. System auto-sorts by platform for labeling
  5. Generate all shipping labels (batch API calls)
  6. Pack and label each order
  7. Generate manifests per platform
  8. Dispatch all at once

  BATCH LIMITS:
  - Amazon:   Up to 50 orders per batch
  - Flipkart: Up to 100 orders per batch
  - Meesho:   Up to 50 orders per batch
  - Others:   As per platform API limits
```

---

## 16. Module 9: Returns & Refunds Management

### 16.1 Platform-Specific Return Policies

```
RETURN RULES VARY BY PLATFORM:

┌──────────────────────────────────────────────────────────────────────────────┐
│  Platform  │ Return Window │ Return Type        │ Refund Method           │
├──────────────────────────────────────────────────────────────────────────────┤
│  Amazon    │ 7-30 days     │ Customer-initiated │ Refund to payment method│
│            │ (by category) │ + Seller-initiated │ or Amazon Pay balance   │
│            │               │                    │ Deducted from settlement│
├──────────────────────────────────────────────────────────────────────────────┤
│  Flipkart  │ 7-30 days     │ Customer-initiated │ Flipkart credits or    │
│            │ (by category) │ Quality check by   │ refund to source       │
│            │               │ Flipkart           │ Deducted from settlement│
├──────────────────────────────────────────────────────────────────────────────┤
│  Meesho    │ 7 days        │ Customer-initiated │ Meesho credits         │
│            │               │ Supplier bears cost│ Deducted from settlement│
│            │               │ for quality issues │                         │
├──────────────────────────────────────────────────────────────────────────────┤
│  Myntra    │ 7-30 days     │ Customer-initiated │ Myntra credits or      │
│            │ (by category) │ Quality check by   │ refund to source       │
│            │               │ Myntra             │ Deducted from settlement│
├──────────────────────────────────────────────────────────────────────────────┤
│  JioMart   │ 7-15 days     │ Customer-initiated │ JioMart credits or     │
│            │               │                    │ refund to source       │
│            │               │                    │ Deducted from settlement│
├──────────────────────────────────────────────────────────────────────────────┤
│  Snapdeal  │ 7 days        │ Customer-initiated │ SD cash / refund       │
│            │               │                    │ Deducted from settlement│
└──────────────────────────────────────────────────────────────────────────────┘
```

### 16.2 Returns Dashboard

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  RETURNS & REFUNDS                                      [Export] [Sync]    │
│  ────────────────────────────────────────────────────────────               │
│                                                                              │
│  SUMMARY CARDS:                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Pending  │ │Received  │ │Inspected │ │Restocked │ │ Rejected │        │
│  │    8     │ │    5     │ │    3     │ │    2     │ │    1     │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│                                                                              │
│  PLATFORM TABS: [All(19)] [Amazon(6)] [Flipkart(5)] [Meesho(3)]           │
│                 [Myntra(2)] [JioMart(2)] [Snapdeal(1)]                     │
│                                                                              │
│  # |Platform |Return ID      |Order ID       |Reason      |Status   |Action│
│  1 |Amazon   |RET-AMZ-001    |AMZ-114-267843 |Wrong Size  |PENDING  |[View]│
│  2 |Flipkart |RET-FK-001     |OD42761234567  |Defective   |RECEIVED |[View]│
│  3 |Meesho   |RET-MSH-001    |MSH-9876543    |Not as Desc |INSPECTED|[View]│
│  4 |Amazon   |RET-AMZ-002    |AMZ-114-267844 |Changed Mind|RESTOCKED|[View]│
│                                                                              │
│  Showing 1-20 of 19       [<- Prev] [1] [Next ->]                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 16.3 Return Processing Flow

```
START
  |
  +-- Platform notifies of return (via API sync)
  |
  +-- System creates return record:
  |     - Platform return ID
  |     - Original order reference
  |     - Return reason (from platform)
  |     - Expected refund amount
  |     - Status = INITIATED
  |
  +-- Return item in transit (courier brings it back)
  |     Status = IN_TRANSIT
  |
  +-- Item arrives at distributor warehouse
  |     Status = RECEIVED
  |
  +-- Warehouse Staff inspects item:
  |     +-- Opens return in app
  |     +-- Performs quality check:
  |     |
  |     |     CONDITION:                  ACTION:
  |     |     ──────────                  ───────
  |     |     Good / Unused              -> Restock (add back to inventory)
  |     |     Minor damage / Open box    -> Restock at discounted tier
  |     |     Major damage / Defective   -> Mark as damaged, do NOT restock
  |     |     Wrong item returned        -> Flag for dispute with platform
  |     |
  |     +-- Staff selects condition and adds notes + photos
  |     Status = INSPECTED
  |
  +-- If RESTOCK:
  |     +-- START TRANSACTION:
  |     |     Step A: Add back to distributor warehouse inventory
  |     |     Step B: Recalculate platform allocations
  |     |     Step C: Sync updated stock to platforms
  |     |     Step D: Log in audit trail
  |     |     COMMIT
  |     Status = RESTOCKED
  |
  +-- If DAMAGED / NOT RESTOCKABLE:
  |     +-- Log as damaged inventory
  |     +-- Flag for insurance claim or write-off
  |     Status = REJECTED
  |
  +-- Refund processing:
  |     - Platform auto-deducts refund from next settlement
  |     - System records the refund amount
  |     - Links to payment reconciliation
  |
  END
```

---

## 17. Module 10: Payments & Reconciliation

### 17.1 Payment Flow Overview

```
MONEY FLOWS THROUGH MULTIPLE CHANNELS:

  END CUSTOMER
       |
       | (Pays platform: Rs. 799)
       v
  ┌─────────────────────────────────────────────┐
  │  PLATFORM (e.g., Amazon)                     │
  │                                              │
  │  Sale Amount:          Rs. 799.00            │
  │  - Commission (12%):   Rs. -95.88            │
  │  - Shipping Fee:       Rs. -50.00            │
  │  - Fixed Fee:          Rs. -20.00            │
  │  - GST on Fees:        Rs. -29.86            │
  │  - TCS (1%):           Rs. -7.99             │
  │  ─────────────────────────────────           │
  │  NET SETTLEMENT:       Rs. 595.27            │
  │                                              │
  │  Settlement Cycle: Every 7 days              │
  └─────────────────────┬───────────────────────┘
                        |
                        v
  ┌─────────────────────────────────────────────┐
  │  DISTRIBUTOR BANK ACCOUNT                    │
  │                                              │
  │  Receives: Rs. 595.27 from Amazon            │
  │  Receives: Rs. XXX from Flipkart             │
  │  Receives: Rs. XXX from Meesho               │
  │  ─────────────────────────────────           │
  │  Total Settlements this month: Rs. X,XX,XXX  │
  │                                              │
  │  MINUS:                                      │
  │  Cost of goods (paid to Company): Rs. X,XX,XXX │
  │  ─────────────────────────────────           │
  │  Net Profit: Rs. XX,XXX                      │
  └─────────────────────────────────────────────┘
```

### 17.2 Reconciliation Dashboard

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  PAYMENTS & RECONCILIATION                              [Sync] [Export]    │
│  ──────────────────────────────────────────────────────────                  │
│                                                                              │
│  PERIOD: [April 2026 v]    DISTRIBUTOR: [NorthStar v]                       │
│                                                                              │
│  PLATFORM SETTLEMENT SUMMARY:                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ Platform  | Orders | Gross Sale  | Fees      | Returns | Net      │     │
│  │ Amazon    | 145    | 2,15,000    | -32,250   | -12,500 | 1,70,250 │     │
│  │ Flipkart  | 98     | 1,45,000    | -24,650   | -8,700  | 1,11,650 │     │
│  │ Meesho    | 210    | 1,89,000    | -18,900   | -15,120 | 1,54,980 │     │
│  │ JioMart   | 55     | 72,000      | -8,640    | -3,600  | 59,760   │     │
│  │ ─────────────────────────────────────────────────────────────────  │     │
│  │ TOTAL     | 508    | 6,21,000    | -84,440   | -39,920 | 4,96,640 │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  PRIMARY SALES (Company owed by this Distributor):                           │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ Stock Received Value:    Rs. 3,50,000                              │     │
│  │ Payments Made:           Rs. 2,00,000                              │     │
│  │ Outstanding:             Rs. 1,50,000                              │     │
│  │ Due Date:                2026-04-30 (Net 30)                       │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  SETTLEMENT TRANSACTIONS:                                                   │
│  # | Date       | Platform  | Settlement ID | Amount    | Status           │
│  1 | 2026-04-07 | Amazon    | SETT-AMZ-001  | 45,000    | RECEIVED         │
│  2 | 2026-04-07 | Flipkart  | SETT-FK-001   | 32,000    | RECEIVED         │
│  3 | 2026-04-14 | Amazon    | SETT-AMZ-002  | 52,000    | PENDING          │
│  4 | 2026-04-10 | Meesho    | SETT-MSH-001  | 38,000    | RECEIVED         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 17.3 Fee Tracking Per Platform

```
THE SYSTEM TRACKS ALL PLATFORM FEES AT ORDER LEVEL:

  For each order, the system records:
  ┌───────────────────────────────────────────┐
  │  Order: AMZ-114-2678432                    │
  │  ─────────────────────                     │
  │  Gross Sale:           Rs. 2,298.00        │
  │                                            │
  │  DEDUCTIONS:                               │
  │  Commission:           Rs. -275.76         │
  │  Closing Fee:          Rs. -20.00          │
  │  Shipping Fee:         Rs. -50.00          │
  │  Weight Handling:      Rs. -15.00          │
  │  GST on Fees (18%):   Rs. -64.94          │
  │  TCS (1%):            Rs. -22.98          │
  │  ────────────────────────────              │
  │  Total Deductions:     Rs. -448.68         │
  │  NET RECEIVABLE:       Rs. 1,849.32        │
  └───────────────────────────────────────────┘

  RECONCILIATION CHECK:
  - System calculates expected settlement per platform rules
  - When platform settles, compare EXPECTED vs ACTUAL
  - Flag any discrepancy > Rs. 1 for investigation
  - Common discrepancies:
    - Late delivery penalty deducted
    - Return refund deducted
    - Promotional discount absorbed
    - Weight dispute (actual vs declared)
```

### 17.4 Distributor Payment to Company

```
TRACKING WHAT DISTRIBUTORS OWE TO COMPANY:

START
  |
  +-- Stock Transfer completed (Primary Sale)
  |     STO-2026-001: Rs. 1,29,056.60
  |     Payment Terms: Net 30
  |     Due Date: 2026-05-01
  |
  +-- System adds to Distributor's outstanding balance
  |
  +-- Distributor makes payment:
  |     - Via bank transfer / NEFT / RTGS
  |     - Distributor records payment in app:
  |       Amount: Rs. 1,29,056.60
  |       Reference: NEFT-XXXX-XXXX
  |       Date: 2026-04-25
  |
  +-- Company Admin verifies and confirms payment
  |
  +-- Outstanding balance updated
  |
  +-- If payment overdue:
  |     - Day 1 past due: Reminder notification
  |     - Day 7 past due: Warning notification
  |     - Day 15 past due: Alert + pause new stock transfers
  |     - Day 30 past due: Escalate to Company Admin
  |
  END
```

---

## 18. Module 11: Dashboard (Unified + Per-Platform)

### 18.1 Company Admin Dashboard (Full Visibility — All Stock, All Distributors, Everything)

Admin sees EVERYTHING — their own company stock (from SAP), every distributor's
stock, every distributor's sales, shipping, payments, returns — all in one dashboard.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HEADER: MPEMS | Welcome, Admin | SAP: ●Connected | Notif (7) | [Logout]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════    │
│  OVERALL SUMMARY (All Distributors, All Platforms):                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Total    │ │ Primary  │ │Secondary │ │ Returns  │ │  Revenue │        │
│  │ Products │ │ Sales    │ │ Sales    │ │ Pending  │ │ (Month)  │        │
│  │   350    │ │ 12.5L    │ │ 28.3L    │ │   19     │ │  28.3L   │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                                  │
│  │ Total    │ │ Total    │ │ SAP Sync │                                  │
│  │Outstanding│ │ Overdue  │ │ Status   │                                  │
│  │  8.15L   │ │  2.25L   │ │ ● OK     │                                  │
│  └──────────┘ └──────────┘ └──────────┘                                  │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════    │
│  COMPANY STOCK (From SAP — Real-time):                                      │
│  ─────────────────────────────────────                                      │
│  Admin sees total company warehouse stock (synced from SAP WM module)       │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ SKU     | Product        | Company Stock| Allocated | Available │      │
│  │         |                | (SAP WM)     | to Distrs | to Send   │      │
│  │ SKU-001 | T-Shirt Blue M | 2,500        | 1,800     | 700       │      │
│  │ SKU-002 | T-Shirt Blue L | 1,800        | 1,200     | 600       │      │
│  │ SKU-003 | Jeans Black 32 | 1,200        | 950       | 250       │      │
│  │ SKU-005 | Shorts Grey XL | 800          | 800       | 0  ⚠     │      │
│  │ SKU-007 | Polo White L   | 1,500        | 1,100     | 400       │      │
│  │ SKU-012 | Kurta Red M    | 600          | 450       | 150       │      │
│  │ ...                                                              │      │
│  │ ─────────────────────────────────────────────────────────────── │      │
│  │ TOTAL   |                | 42,500       | 31,200    | 11,300    │      │
│  │                                                                  │      │
│  │ Company Stock    = Physical stock in Company warehouse (SAP)     │      │
│  │ Allocated        = Already sent/committed to all distributors    │      │
│  │ Available        = Free to allocate to any distributor           │      │
│  │ [View Full Inventory →] [Sync from SAP →]                       │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════    │
│  ALL DISTRIBUTORS STOCK (Admin sees every distributor's inventory):         │
│  ─────────────────────────────────────────────────────────────────          │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ Distributor  | Total Stock | Sold (Month)| In Stock | Utilzn %  │      │
│  │              | Received    |             | Now      |           │      │
│  │ NorthStar    | 15.0L       | 10.5L       | 3,200 u  | 84.7%    │      │
│  │ SouthWave    | 10.0L       | 7.2L        | 2,100 u  | 78.5%    │      │
│  │ WestEnd      | 6.5L        | 4.3L        | 1,500 u  | 72.0%    │      │
│  │ EastLink     | 3.0L        | 1.8L        | 900 u    | 65.0%    │      │
│  │ ─────────────────────────────────────────────────────────────── │      │
│  │ TOTAL ALL    | 34.5L       | 23.8L       | 7,700 u  | 76.8%    │      │
│  │                                                                  │      │
│  │ Click any distributor row → opens Distributor Detail View        │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌─ DISTRIBUTOR STOCK DRILL-DOWN (SKU Level — All Distributors) ────┐     │
│  │                                                                    │     │
│  │  FILTER: [Select Product / SKU v]  Showing: SKU-001 T-Shirt Blue  │     │
│  │                                                                    │     │
│  │  Location          | Qty    | Listed Platforms      | Status       │     │
│  │  Company Warehouse | 700    | —                     | Available    │     │
│  │  NorthStar (Delhi) | 155    | Amz:60 FK:50 Jio:45  | OK           │     │
│  │  SouthWave (Chennai)| 120   | FK:50 Meesho:40 Myn:30| OK          │     │
│  │  WestEnd (Mumbai)  | 80     | Amz:35 Snap:25 Jio:20| OK           │     │
│  │  EastLink (Kolkata)| 45     | FK:25 Meesho:20      | LOW          │     │
│  │  ──────────────────────────────────────────────────────────────   │     │
│  │  TOTAL IN SYSTEM   | 1,100  |                       |             │     │
│  │  SAP Stock (MM)    | 1,100  | ← Matches ✓           |             │     │
│  │                                                                    │     │
│  │  Admin can see: for any product, where is every unit sitting —    │     │
│  │  in company warehouse, at which distributor, listed on which       │     │
│  │  platform. Full traceability.                                      │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════    │
│  DISTRIBUTOR PERFORMANCE (Expanded — Admin sees all details):               │
│  ────────────────────────────────────────────────────────────                │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │Distributor |Stock |Orders|Revenue|Returns|Overdue |Ship |Margin │      │
│  │            |Sent  |      |       |  %    |Payment |SLA% |       │      │
│  │NorthStar   |7.5L  | 320  | 15.2L | 7.5%  | 1.50L  |95%  | 19%  │      │
│  │SouthWave   |5.0L  | 188  | 8.8L  | 6.2%  | 0.50L  |93%  | 18%  │      │
│  │WestEnd     |3.2L  | 95   | 4.3L  | 5.0%  | 0.25L  |91%  | 17%  │      │
│  │EastLink    |1.5L  | 42   | 1.8L  | 8.1%  | 0      |88%  | 15%  │      │
│  │ ─────────────────────────────────────────────────────────────── │      │
│  │TOTAL       |17.2L | 645  | 30.1L | 6.7%  | 2.25L  |93%  | 18%  │      │
│  │                                                                  │      │
│  │ Stock Sent   = Primary sales value sent to distributor           │      │
│  │ Overdue Pmt  = Amount past payment terms (Net 30/60)            │      │
│  │ Ship SLA%    = Orders shipped before platform deadline           │      │
│  │ Click any row → Full Distributor Detail (8-tab view)             │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════    │
│  ALL DISTRIBUTORS — SHIPPING OVERVIEW:                                      │
│  ─────────────────────────────────────                                      │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │Distributor |Pending|Shipped |Delivered|SLA     |Avg Delivery    │      │
│  │            |Ship   |Today   |(Month)  |Breach  |Time            │      │
│  │NorthStar   | 8     | 23     | 482     | 18     | 3.1 days       │      │
│  │SouthWave   | 5     | 15     | 310     | 12     | 3.5 days       │      │
│  │WestEnd     | 3     | 8      | 165     | 8      | 3.8 days       │      │
│  │EastLink    | 2     | 4      | 78      | 5      | 4.2 days       │      │
│  │ ─────────────────────────────────────────────────────────────── │      │
│  │TOTAL       | 18    | 50     | 1,035   | 43     | 3.4 days       │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════    │
│  ALL DISTRIBUTORS — PAYMENT STATUS:                                         │
│  ──────────────────────────────────                                         │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │Distributor |Credit |Stock     |Paid     |Outstanding|Overdue   │      │
│  │            |Limit  |Received  |(All Time)|(Current)  |(Past Due)│      │
│  │NorthStar   |25.0L  |85.0L     |81.50L   | 3.50L     | 1.50L ⚠ │      │
│  │SouthWave   |20.0L  |52.0L     |49.90L   | 2.10L     | 0.50L ⚠ │      │
│  │WestEnd     |15.0L  |35.0L     |33.20L   | 1.80L     | 0.25L ⚠ │      │
│  │EastLink    |10.0L  |18.0L     |17.25L   | 0.75L     | 0       │      │
│  │ ─────────────────────────────────────────────────────────────── │      │
│  │TOTAL       |70.0L  |190.0L    |181.85L  | 8.15L     | 2.25L   │      │
│  │                                                                  │      │
│  │ SAP FI Balance (Accounts Receivable): Rs. 8,15,000 ✓ Matches    │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════    │
│  PLATFORM BREAKDOWN (All Distributors Combined):                            │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ Platform  | Orders | Revenue  | Avg Order | Return % | Margin   │      │
│  │ Amazon    | 210    | 9.8L     | 467       | 3.8%     | 22%      │      │
│  │ Flipkart  | 165    | 7.2L     | 436       | 4.2%     | 20%      │      │
│  │ Meesho    | 280    | 6.5L     | 232       | 5.0%     | 18%      │      │
│  │ Myntra    | 45     | 2.8L     | 622       | 3.5%     | 24%      │      │
│  │ JioMart   | 55     | 1.5L     | 273       | 2.1%     | 19%      │      │
│  │ Snapdeal  | 48     | 0.5L     | 104       | 6.2%     | 15%      │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════    │
│  RETURNS OVERVIEW (All Distributors):                                       │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │Distributor |Orders|Returns|Return%|Return Value |Top Reason      │      │
│  │NorthStar   | 320  | 38    | 7.5%  | 1,39,920    | Size Issue     │      │
│  │SouthWave   | 188  | 22    | 6.2%  | 78,500      | Quality Defect │      │
│  │WestEnd     | 95   | 10    | 5.0%  | 42,000      | Changed Mind   │      │
│  │EastLink    | 42   | 5     | 8.1%  | 18,000      | Wrong Item     │      │
│  │ ─────────────────────────────────────────────────────────────── │      │
│  │TOTAL       | 645  | 75    | 6.7%  | 2,78,420    |                │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  LOW STOCK ALERTS:                    PENDING ACTIONS:                      │
│  ┌──────────────────────────┐        ┌─────────────────────────────┐      │
│  │ COMPANY WAREHOUSE:       │        │ 3 STOs awaiting approval    │      │
│  │ SKU-005: 0 available ⛔ │        │ 2 payments overdue (2.25L)  │      │
│  │ SKU-003: 250 available  │        │ 19 returns pending          │      │
│  │                          │        │ 1 SAP sync error            │      │
│  │ DISTRIBUTOR WAREHOUSES:  │        │ 18 orders pending shipment  │      │
│  │ NorthStar SKU-003: 15 u │        │ [View All →]                │      │
│  │ NorthStar SKU-005: 0 u  │        └─────────────────────────────┘      │
│  │ SouthWave SKU-012: 8 u  │                                             │
│  │ EastLink SKU-001: 45 u  │        SAP HEALTH:                          │
│  │ [View All →]             │        ┌─────────────────────────────┐      │
│  └──────────────────────────┘        │ ● Connected (2 min ago)    │      │
│                                       │ Products: 350/350 synced  │      │
│                                       │ Stock: In sync ✓          │      │
│                                       │ Ledger: Matched ✓         │      │
│                                       │ [Open SAP Dashboard →]    │      │
│                                       └─────────────────────────────┘      │
│                                                                             │
│  SIDEBAR:                                                                   │
│  +-- Dashboard                                                              │
│  +-- Products (SAP synced)                                                  │
│  +-- Distributors                                                           │
│  +-- Platforms                                                              │
│  +-- Primary Sales (Stock Transfers)                                        │
│  +-- Orders (All Platforms)                                                 │
│  +-- Inventory (Company + All Distributors)                                 │
│  +-- Returns                                                                │
│  +-- Payments & Reconciliation                                              │
│  +-- SAP Integration                                                        │
│  +-- Reports                                                                │
│  +-- Audit Log                                                              │
│  +-- Users                                                                  │
│  +-- Settings                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 18.2 Distributor Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HEADER: MPEMS | NorthStar Distribution | Notifications (4) | [Logout]     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MY SUMMARY (This Month):                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Pending  │ │ To Ship  │ │ Shipped  │ │ Returns  │ │ Revenue  │        │
│  │ Orders   │ │ Today    │ │ (Month)  │ │ Pending  │ │ (Month)  │        │
│  │   15     │ │   23     │ │   297    │ │   8      │ │  15.2L   │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                                  │
│  │ My Stock │ │Outstanding│ │ Net      │                                  │
│  │ Value    │ │ to Company│ │ Profit   │                                  │
│  │  13.0L   │ │  3.50L   │ │  4.2L    │                                  │
│  └──────────┘ └──────────┘ └──────────┘                                  │
│                                                                             │
│  MY INVENTORY SNAPSHOT:                                                     │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ Total SKUs: 85 | In Stock: 3,200 units | Low: 12 | Out: 3      │      │
│  │                                                                  │      │
│  │ Platform Stock Allocation:                                       │      │
│  │ Amazon:   820 units listed  |  Flipkart: 680 units listed      │      │
│  │ JioMart:  520 units listed  |  Unallocated: 1,180 units        │      │
│  │ [View Full Inventory →]                                          │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ORDERS BY PLATFORM (Today):                                                │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ Amazon:    8 new  | 5 to ship  | 12 shipped  | 1 return        │      │
│  │ Flipkart:  6 new  | 4 to ship  | 8 shipped   | 2 returns       │      │
│  │ JioMart:   3 new  | 2 to ship  | 5 shipped   | 0 returns       │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  URGENT: SHIP TODAY (SLA Breach Risk)                                       │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ AMZ-114-2678432  | Amazon  | Ship by 4:00 PM | 2 items         │      │
│  │ OD427612345678   | Flipkart| Ship by 6:00 PM | 1 item          │      │
│  │ AMZ-114-2678435  | Amazon  | Ship by 4:00 PM | 3 items         │      │
│  │ [View All Orders to Ship →]                                     │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  SHIPPING TODAY:                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │ Shipped: 15 | Pending: 8 | SLA at risk: 3                      │      │
│  │ Top Destinations Today: Delhi(5), Jaipur(3), Lucknow(2)        │      │
│  │ Avg Ship Time: 5.8 hours | On-time: 94.9%                      │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  PAYMENT STATUS:                      INCOMING STOCK:                       │
│  ┌──────────────────────────┐        ┌─────────────────────────────┐      │
│  │ Owed to Company: 3.50L  │        │ STO-2026-014 in transit     │      │
│  │ Overdue: 1.50L ⚠       │        │ Expected: 2026-04-03        │      │
│  │ Next Due: 2026-04-15    │        │ Items: 3 | Value: 2.1L     │      │
│  │ Platform settlements:   │        │                              │      │
│  │  Pending: 3.42L         │        │ STO-2026-016 shipped        │      │
│  │ [View Payments →]       │        │ Expected: 2026-04-07        │      │
│  └──────────────────────────┘        │ Items: 5 | Value: 3.45L    │      │
│                                       └─────────────────────────────┘      │
│  STOCK STATUS:                                                              │
│  ┌──────────────────────────┐        RETURNS PENDING:                      │
│  │ 12 products low stock   │        ┌─────────────────────────────┐      │
│  │ 3 products out of stock │        │ 5 returns in transit        │      │
│  │ Top low: SKU-003 (7 u)  │        │ 3 returns at QC check       │      │
│  │ [View Inventory →]      │        │ Return rate: 7.5%           │      │
│  └──────────────────────────┘        │ [View Returns →]            │      │
│                                       └─────────────────────────────┘      │
│                                                                             │
│  SIDEBAR:                                                                   │
│  +-- Dashboard                                                              │
│  +-- My Orders (All Platforms)                                              │
│  +-- Inventory                                                              │
│  +-- Shipments                                                              │
│  +-- Stock Transfers (from Company)                                         │
│  +-- Returns                                                                │
│  +-- Payments & Settlements                                                 │
│  +-- Platform Performance                                                   │
│  +-- Activity Log                                                           │
│  +-- Settings                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 19. Module 12: Reports & Analytics

### 19.1 Available Reports

#### Report 1: Cross-Platform Sales Comparison
```
Shows:
- Sales volume, revenue, and growth across all platforms
- Side-by-side comparison: Amazon vs Flipkart vs Meesho vs others
- Trends over time (daily / weekly / monthly)
- Best performing platform by category

Data Source: orders table + order_items table + platform_fees table
```

#### Report 2: Distributor Performance Report
```
Shows:
- Per distributor: orders processed, revenue, return rate
- Stock utilization (stock sent vs stock sold)
- Platform-wise breakdown per distributor
- Payment compliance (on-time payments vs overdue)

Data Source: stock_transfers + orders + returns + payments
```

#### Report 3: Product Performance Report
```
Shows:
- Per product: units sold, revenue, return rate across ALL platforms
- Which platform sells which product best
- Slow-moving inventory alerts
- Product-wise margin analysis

Data Source: order_items + returns + inventory + product_catalog
```

#### Report 4: Platform Fee Analysis
```
Shows:
- Total fees paid to each platform (commissions, shipping, penalties)
- Fee as % of revenue per platform
- Fee trend over time
- Hidden costs (weight disputes, late penalties, etc.)

Data Source: platform_fees table + settlement_transactions
```

#### Report 5: Inventory Aging Report
```
Shows:
- How long stock has been sitting at each level (Company / Distributor)
- Fast-moving vs slow-moving by platform
- Dead stock alerts
- Recommended stock reallocation

Data Source: inventory_log + stock_transfers + order_items
```

#### Report 6: Returns Analysis
```
Shows:
- Return rate per platform
- Top return reasons
- Return rate per product/category
- Financial impact of returns (refund amount + shipping cost)

Data Source: returns table + orders table
```

#### Report 7: Primary Sales Report
```
Shows:
- Stock transfers to each distributor (volume, value)
- Outstanding payments per distributor
- Transfer frequency and trends
- Credit utilization per distributor

Data Source: stock_transfers + distributor_payments
```

#### Report 8: Settlement Reconciliation Report
```
Shows:
- Expected settlement vs actual settlement per platform
- Discrepancies flagged
- Pending settlements
- Settlement delay analysis

Data Source: settlement_transactions + platform_fees + orders
```

---

## 20. Module 13: Notifications System

### 20.1 Notification Triggers

| Trigger                                      | Who Gets Notified             | Channel         |
|----------------------------------------------|-------------------------------|-----------------|
| New order received from any platform         | Distributor Mgr + Warehouse   | In-App + Push   |
| Order SLA breach approaching (2 hours left)  | Distributor Mgr + Warehouse   | In-App + Push   |
| Order SLA breached                           | Distributor Mgr + Company     | In-App + Email  |
| Return initiated by customer                 | Distributor Mgr               | In-App          |
| Return received at warehouse                 | Distributor Mgr               | In-App          |
| Stock falls below threshold                  | Distributor Mgr + Company     | In-App + Email  |
| Stock reaches zero on any platform           | Distributor Mgr + Company     | In-App + Email  |
| Stock transfer created (Primary Sale)        | Distributor Mgr               | In-App + Email  |
| Stock transfer shipped                       | Distributor Mgr               | In-App + Push   |
| Settlement received from platform            | Distributor Mgr               | In-App          |
| Settlement discrepancy detected              | Distributor Mgr + Company     | In-App + Email  |
| Distributor payment overdue                  | Company Admin + Distributor   | In-App + Email  |
| Platform connection error                    | Distributor Mgr + Company     | In-App + Email  |
| Platform API rate limit reached              | System Admin                  | Email           |
| Failed login attempts (5+)                   | Company Admin                 | Email           |
| New distributor onboarded                    | Company Admin                 | In-App          |

### 20.2 Notification Flow

```
START
  |
  +-- Event occurs (e.g., new order from Amazon)
  |
  +-- System determines:
  |     - Who should be notified (based on role + scope)
  |     - Which channels (in-app, email, push)
  |
  +-- Create notification record:
  |     INSERT INTO notifications (
  |         user_id, type, title, message,
  |         reference_type, reference_id,
  |         platform, severity,
  |         is_read, created_at
  |     )
  |
  +-- IN-APP: Push via WebSocket to connected users
  |     Bell icon shows unread count: (7)
  |
  +-- EMAIL: Add to email queue for async sending
  |     Background job processes queue via SMTP/SendGrid
  |
  +-- PUSH: Send push notification (if mobile app / PWA)
  |
  END
```

---

## 21. Module 14: Audit Trail

### 21.1 What Gets Logged

| Event Category              | Logged Data                                                    |
|-----------------------------|----------------------------------------------------------------|
| Authentication              | Login, logout, failed login, password change, account lock     |
| Product Catalog             | Product created, updated, discontinued, pricing changed        |
| Distributor                 | Created, updated, paused, platform connected/disconnected      |
| Stock Transfer (Primary)    | Created, approved, shipped, received, completed, discrepancy   |
| Order (Secondary)           | Synced, accepted, fulfilled, shipped, delivered, cancelled     |
| Inventory                   | Stock added, deducted, adjusted, synced to platform            |
| Returns                     | Initiated, received, inspected, restocked, rejected            |
| Payments                    | Settlement received, payment recorded, payment confirmed       |
| Platform                    | Connected, disconnected, sync success, sync failure, API error |
| User Management             | User created, role changed, deactivated                        |

### 21.2 Audit Log Rules

```
- Logs are NEVER deleted (append-only)
- Logs are NEVER modified
- Each log entry contains:
    - Timestamp
    - User who performed action
    - User's role and scope
    - Action type
    - Entity type and ID
    - Old value (before change)
    - New value (after change)
    - IP address
    - Platform (if platform-related)
    - Distributor (if distributor-scoped)
- Company Admin can view all logs
- Distributor Manager can view own distributor's logs
- Other roles can view only their own actions
- Logs older than 3 years can be archived but never deleted
```

---

## 22. Module 15: SAP Integration (ERP Connectivity)

### 22.1 Why SAP Integration?

```
THE PROBLEM WITHOUT SAP:

  Company already uses SAP ERP for:
  - Product Master Data (Material Master — MM01)
  - Pricing & Cost Structures
  - Finance & Accounting (FI/CO)
  - Warehouse Management (WM)
  - Sales & Distribution (SD)
  - Vendor / Customer Ledgers

  WITHOUT SAP integration:
  ┌──────────────────────────────────────────────────────────────┐
  │  SAP ERP                         MPEMS (Our App)            │
  │  ─────────                       ──────────────             │
  │  Products in SAP    ╳    Products entered again manually    │
  │  Stock in SAP       ╳    Stock tracked separately           │
  │  Invoices in SAP    ╳    Invoices also in MPEMS             │
  │  Payments in SAP    ╳    Payments also tracked in MPEMS     │
  │  Ledger in SAP      ╳    Ledger also in MPEMS               │
  │                                                              │
  │  RESULT: Double data entry, mismatch, reconciliation hell   │
  └──────────────────────────────────────────────────────────────┘

  WITH SAP integration:
  ┌──────────────────────────────────────────────────────────────┐
  │  SAP ERP  ◄──────  TWO-WAY SYNC  ──────►  MPEMS            │
  │  ─────────                                 ──────────────   │
  │  Products (MM)  ────────────────►  Auto-synced to MPEMS     │
  │  Pricing (SD)   ────────────────►  Pricing always in sync   │
  │  Stock (WM)     ◄───────────────►  Real-time stock sync     │
  │  Sales Orders   ◄────────────────  STOs auto-posted to SAP  │
  │  Invoices (FI)  ◄────────────────  Invoices auto-posted     │
  │  Payments (FI)  ◄───────────────►  Payment status synced    │
  │  Dist. Ledger   ◄────────────────  All transactions posted  │
  │                                                              │
  │  RESULT: Single source of truth, no double entry             │
  └──────────────────────────────────────────────────────────────┘
```

### 22.2 SAP Modules Connected

```
SAP MODULES THAT MPEMS CONNECTS TO:

  ┌──────────────────────────────────────────────────────────────────────────┐
  │                                                                          │
  │  SAP MM (Material Management)                                            │
  │  ────────────────────────────                                            │
  │  - Product Master Data (material number, description, weight, HSN)       │
  │  - Bill of Materials (BOM)                                               │
  │  - Purchasing data                                                       │
  │  Direction: SAP → MPEMS (products are mastered in SAP)                   │
  │                                                                          │
  │  SAP SD (Sales & Distribution)                                           │
  │  ───────────────────────────                                             │
  │  - Pricing conditions & discount structures                              │
  │  - Sales orders (STOs posted here)                                       │
  │  - Delivery documents                                                    │
  │  - Customer master (distributors)                                        │
  │  Direction: Bidirectional (pricing from SAP, orders from MPEMS)          │
  │                                                                          │
  │  SAP FI (Financial Accounting)                                           │
  │  ──────────────────────────────                                          │
  │  - Invoice posting (accounts receivable)                                 │
  │  - Payment clearing                                                      │
  │  - Distributor sub-ledger                                                │
  │  - Platform settlement entries                                           │
  │  - GST/Tax postings                                                      │
  │  Direction: MPEMS → SAP (all financial transactions posted)              │
  │                                                                          │
  │  SAP CO (Controlling)                                                    │
  │  ─────────────────────                                                   │
  │  - Cost center posting for platform fees                                 │
  │  - Profitability analysis per platform/distributor                       │
  │  Direction: MPEMS → SAP (cost data posted)                               │
  │                                                                          │
  │  SAP WM (Warehouse Management)                                           │
  │  ──────────────────────────────                                          │
  │  - Company warehouse stock levels                                        │
  │  - Stock transfer postings (goods issue / goods receipt)                 │
  │  - Inventory adjustments                                                 │
  │  Direction: Bidirectional (stock in sync both ways)                      │
  │                                                                          │
  └──────────────────────────────────────────────────────────────────────────┘
```

### 22.3 SAP Connection Architecture

```
CONNECTION METHODS:

  ┌───────────────────────────────────────────────────────────────────────┐
  │                                                                       │
  │  MPEMS App                          SAP ERP                           │
  │  ─────────                          ────────                          │
  │                                                                       │
  │  ┌──────────────────┐              ┌──────────────────┐              │
  │  │  SAP Integration │   METHOD 1   │  SAP RFC / BAPI  │              │
  │  │  Service         │◄────────────►│  Gateway          │              │
  │  │                  │   (RFC Call)  │                  │              │
  │  │                  │              └──────────────────┘              │
  │  │                  │                                                │
  │  │                  │   METHOD 2   ┌──────────────────┐              │
  │  │                  │◄────────────►│  SAP OData API   │              │
  │  │                  │  (REST/OData)│  (SAP Gateway)   │              │
  │  │                  │              └──────────────────┘              │
  │  │                  │                                                │
  │  │                  │   METHOD 3   ┌──────────────────┐              │
  │  │                  │◄────────────►│  SAP IDocs       │              │
  │  │                  │  (Async Msg) │  (EDI Interface)  │              │
  │  └──────────────────┘              └──────────────────┘              │
  │                                                                       │
  │  PREFERRED: OData REST API via SAP Gateway (modern, scalable)        │
  │  FALLBACK:  RFC/BAPI calls for specific transactions                  │
  │  BATCH:     IDocs for bulk data sync (nightly product/price sync)    │
  │                                                                       │
  └───────────────────────────────────────────────────────────────────────┘
```

### 22.4 SAP Data Sync Flows

#### 22.4.1 Product Master Sync (SAP → MPEMS)

```
START
  |
  +-- TRIGGER: Nightly batch sync OR manual "Sync from SAP" button
  |
  +-- MPEMS calls SAP OData API:
  |     GET /sap/opu/odata/sap/API_PRODUCT_SRV/A_Product
  |     (or BAPI_MATERIAL_GETLIST via RFC)
  |
  +-- SAP returns material master data:
  |     - Material Number (becomes SKU in MPEMS)
  |     - Description (short + long)
  |     - Material Group / Category
  |     - HSN Code (for GST)
  |     - Weight (gross / net)
  |     - Unit of Measure
  |     - EAN / Barcode
  |
  +-- MPEMS processes each material:
  |     +-- Material exists in MPEMS?
  |     |     YES → Update existing product record
  |     |     NO  → Create new product in catalog
  |     |
  |     +-- Price changed in SAP?
  |     |     YES → Update distributor price in MPEMS
  |     |     NO  → Skip
  |     |
  |     +-- Material marked as discontinued in SAP?
  |           YES → Mark as inactive in MPEMS
  |                 Alert: "SKU-XXX discontinued in SAP"
  |
  +-- Log sync result:
  |     Products synced: 350
  |     New products: 5
  |     Updated: 12
  |     Discontinued: 1
  |     Errors: 0
  |
  END
```

#### 22.4.2 Stock Sync (SAP ↔ MPEMS — Bidirectional)

```
COMPANY WAREHOUSE STOCK SYNC:

  SAP → MPEMS (Company stock levels):
  ──────────────────────────────────
  START
    |
    +-- Every 15 minutes OR on demand
    |
    +-- MPEMS calls SAP:
    |     GET /MaterialStock (Plant = Company Warehouse)
    |     (or BAPI_MATERIAL_AVAILABILITY)
    |
    +-- SAP returns stock per material per storage location:
    |     Material: SKU-001 | Plant: 1000 | Storage: 0001 | Qty: 500
    |     Material: SKU-002 | Plant: 1000 | Storage: 0001 | Qty: 300
    |     ...
    |
    +-- MPEMS updates Company warehouse inventory
    |
    +-- Admin Dashboard shows LIVE Company stock from SAP
    |
    END

  MPEMS → SAP (Stock Transfer posting):
  ──────────────────────────────────────
  START
    |
    +-- When STO status changes to SHIPPED in MPEMS:
    |
    +-- MPEMS posts Goods Issue to SAP:
    |     BAPI_GOODSMVT_CREATE
    |     Movement Type: 641 (Stock transfer — plant to plant)
    |     From Plant: 1000 (Company)
    |     To Plant: 2000 (Distributor)
    |     Materials + Quantities from STO
    |
    +-- When Distributor RECEIVES stock in MPEMS:
    |
    +-- MPEMS posts Goods Receipt to SAP:
    |     BAPI_GOODSMVT_CREATE
    |     Movement Type: 101 (Goods Receipt)
    |     Plant: 2000 (Distributor)
    |     Materials + Quantities received
    |
    +-- SAP stock updated automatically
    |
    END
```

#### 22.4.3 Invoice & Payment Sync (MPEMS → SAP)

```
INVOICE POSTING TO SAP:

  START
    |
    +-- STO created in MPEMS generates invoice
    |
    +-- MPEMS posts invoice to SAP FI:
    |     BAPI_ACC_DOCUMENT_POST
    |     (or create Sales Order via BAPI_SALESORDER_CREATEFROMDAT2)
    |
    |     Document Type: Invoice
    |     Customer: Distributor (SAP customer number)
    |     Line Items: Products from STO
    |     Amounts: As per distributor pricing
    |     Tax: GST calculated per HSN code
    |
    +-- SAP creates:
    |     - Sales Order (SD)
    |     - Accounting Document (FI)
    |     - Accounts Receivable entry for Distributor
    |
    END

  PAYMENT POSTING TO SAP:

  START
    |
    +-- Distributor payment recorded in MPEMS
    |
    +-- MPEMS posts payment to SAP FI:
    |     BAPI_ACC_DOCUMENT_POST
    |     Document Type: Payment
    |     Customer: Distributor
    |     Amount: Payment amount
    |     Bank: Company bank account
    |     Reference: NEFT/RTGS reference number
    |
    +-- SAP clears:
    |     - Open invoice items against payment
    |     - Updates distributor account balance
    |     - Accounts Receivable reduced
    |
    +-- MPEMS confirms SAP posting successful
    |     Distributor outstanding balance matches in both systems
    |
    END
```

#### 22.4.4 Platform Fee & Settlement Posting (MPEMS → SAP)

```
PLATFORM SETTLEMENT POSTING:

  START
    |
    +-- Platform settlement received (e.g., Amazon pays Rs. 1,85,000)
    |
    +-- MPEMS posts to SAP FI:
    |
    |     DEBIT:  Bank Account (Company/Distributor)      Rs. 1,85,000
    |     CREDIT: Platform Revenue Account                Rs. 2,15,000
    |     DEBIT:  Platform Commission Expense             Rs.    25,800
    |     DEBIT:  Platform Shipping Fee Expense           Rs.     4,200
    |
    +-- Each fee type goes to a separate SAP cost center:
    |     - Commission → Cost Center: CC-PLATFORM-COMM
    |     - Shipping   → Cost Center: CC-PLATFORM-SHIP
    |     - Penalties  → Cost Center: CC-PLATFORM-PENALTY
    |     - TCS/TDS    → Tax Account (auto per SAP config)
    |
    +-- SAP Profitability Analysis (CO-PA) updated:
    |     Profit per Platform per Distributor per Product
    |
    END
```

### 22.5 SAP Configuration Screen

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  SAP INTEGRATION SETTINGS                              [Test Connection]    │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ┌─ SAP CONNECTION ──────────────────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  Connection Type:    [OData REST API v]                                │  │
│  │  SAP Host:           [sap.company.com        ]                        │  │
│  │  SAP Port:           [443                     ]                        │  │
│  │  SAP Client:         [100                     ]                        │  │
│  │  SAP System ID:      [PRD                     ]                        │  │
│  │  Authentication:     [OAuth 2.0 / Basic v]                             │  │
│  │  Username:           [MPEMS_INTEGRATION        ]                       │  │
│  │  Password:           [••••••••••••             ]                        │  │
│  │                                                                        │  │
│  │  Status: ● CONNECTED (last successful call: 2 min ago)                │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ SAP MAPPING ─────────────────────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  Company Plant (SAP):          [1000 — Main Factory     ]             │  │
│  │  Company Storage Location:     [0001 — Finished Goods   ]             │  │
│  │                                                                        │  │
│  │  DISTRIBUTOR PLANT MAPPING:                                            │  │
│  │  Distributor (MPEMS)    | SAP Plant | SAP Customer # | Storage Loc    │  │
│  │  NorthStar Distribution | 2000      | CUST-NS-001    | 0001           │  │
│  │  SouthWave Distribution | 2100      | CUST-SW-002    | 0001           │  │
│  │  WestEnd Traders        | 2200      | CUST-WE-003    | 0001           │  │
│  │  EastLink Supply        | 2300      | CUST-EL-004    | 0001           │  │
│  │                                                                        │  │
│  │  PLATFORM COST CENTER MAPPING:                                         │  │
│  │  Platform  | Revenue Account | Commission CC | Shipping CC | Tax Acct  │  │
│  │  Amazon    | 4000-AMZ        | CC-AMZ-COMM   | CC-AMZ-SHIP | TX-TCS   │  │
│  │  Flipkart  | 4000-FK         | CC-FK-COMM    | CC-FK-SHIP  | TX-TCS   │  │
│  │  Meesho    | 4000-MSH        | CC-MSH-COMM   | CC-MSH-SHIP | TX-TCS   │  │
│  │  JioMart   | 4000-JIO        | CC-JIO-COMM   | CC-JIO-SHIP | TX-TCS   │  │
│  │                                                                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ SYNC SCHEDULE ───────────────────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  Data Type               | Direction    | Frequency      | Last Sync  │  │
│  │  Product Master          | SAP → MPEMS  | Daily 2:00 AM  | Today 2AM  │  │
│  │  Pricing Conditions      | SAP → MPEMS  | Daily 2:00 AM  | Today 2AM  │  │
│  │  Company Stock           | SAP → MPEMS  | Every 15 min   | 2 min ago  │  │
│  │  Stock Transfer (GI/GR)  | MPEMS → SAP  | Real-time      | 14 min ago │  │
│  │  Sales Orders / Invoices | MPEMS → SAP  | Real-time      | 32 min ago │  │
│  │  Payments                | MPEMS → SAP  | Real-time      | 1 hr ago   │  │
│  │  Platform Settlements    | MPEMS → SAP  | Daily 11:00 PM | Yesterday  │  │
│  │  Distributor Master      | SAP ↔ MPEMS  | On change      | 3 days ago │  │
│  │                                                                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ SYNC LOG ────────────────────────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  # | Timestamp           | Type           | Direction | Status | Dtl  │  │
│  │  1 | 2026-04-01 14:30:00 | Stock Level    | SAP→MPEMS | OK     | [V]  │  │
│  │  2 | 2026-04-01 14:15:00 | Stock Level    | SAP→MPEMS | OK     | [V]  │  │
│  │  3 | 2026-04-01 13:45:22 | Goods Issue    | MPEMS→SAP | OK     | [V]  │  │
│  │  4 | 2026-04-01 12:00:00 | Invoice Post   | MPEMS→SAP | OK     | [V]  │  │
│  │  5 | 2026-04-01 02:00:00 | Product Sync   | SAP→MPEMS | OK     | [V]  │  │
│  │  6 | 2026-03-31 23:00:00 | Settlement Post| MPEMS→SAP | ERROR  | [V]  │  │
│  │  [View All Sync Logs →]                                                │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  [Save Settings] [Run Full Sync Now] [View Error Log]                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 22.6 SAP Dashboard View (Inside MPEMS)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  SAP SYNC STATUS                                     [Refresh] [Full Sync]  │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ SAP      │ │ Products │ │ Stock    │ │ Invoices │ │ Payments │        │
│  │ Status   │ │ Synced   │ │ Synced   │ │ Posted   │ │ Posted   │        │
│  │●CONNECTED│ │ 350/350  │ │ 2 min ago│ │ 45 today │ │ 3 today  │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│                                                                              │
│  DATA HEALTH (SAP vs MPEMS Match):                                          │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ Data Type          | SAP Value    | MPEMS Value  | Match | Action │     │
│  │ Product Count      | 350          | 350          | ✓     |        │     │
│  │ Company Stock (SKUs)| 350         | 350          | ✓     |        │     │
│  │ Company Stock (Qty)| 42,500 units | 42,500 units | ✓     |        │     │
│  │ Open Invoices      | Rs. 12,50,000| Rs. 12,50,000| ✓     |        │     │
│  │ NorthStar Balance  | Rs. 3,50,000 | Rs. 3,50,000 | ✓     |        │     │
│  │ SouthWave Balance  | Rs. 2,10,000 | Rs. 2,10,000 | ✓     |        │     │
│  │ WestEnd Balance    | Rs. 1,80,000 | Rs. 1,80,000 | ✓     |        │     │
│  │ EastLink Balance   | Rs. 75,000   | Rs. 75,000   | ✓     |        │     │
│  │ ────────────────────────────────────────────────────────────────── │     │
│  │ MISMATCHES: 0                                    [View History]    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  FAILED POSTINGS (Require Attention):                                       │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ # | Date       | Type       | Reference     | Error        | Act  │     │
│  │ 1 | 2026-03-31 | Settlement | SETT-JIO-007  | Tax code inv | [Fix]│     │
│  │ No other failures.                                                 │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 23. Database Design — Detailed Table Structures

### 22.1 Core Tables

#### Table: companies
```
┌──────────────────────────────────────────────────────────────┐
│  companies (Brand/Manufacturer profile)                      │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  name                VARCHAR(200)  NOT NULL                   │
│  legal_name          VARCHAR(200)  NOT NULL                   │
│  gstin               VARCHAR(15)   UNIQUE, NOT NULL           │
│  pan                 VARCHAR(10)   NOT NULL                   │
│  address             TEXT          NOT NULL                   │
│  city                VARCHAR(100)                             │
│  state               VARCHAR(100)                             │
│  pincode             VARCHAR(6)                               │
│  contact_email       VARCHAR(100)  NOT NULL                   │
│  contact_phone       VARCHAR(15)   NOT NULL                   │
│  bank_account_name   VARCHAR(200)                             │
│  bank_account_number VARCHAR(20)                              │
│  bank_ifsc           VARCHAR(11)                              │
│  bank_name           VARCHAR(100)                             │
│  logo_url            VARCHAR(500)                             │
│  is_active           BOOLEAN       DEFAULT TRUE               │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: app_users
```
┌──────────────────────────────────────────────────────────────┐
│  app_users (All system users)                                │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  company_id          INT           FOREIGN KEY -> companies.id│
│  distributor_id      INT           FOREIGN KEY -> distributors.id (NULL for company users)│
│  username            VARCHAR(50)   UNIQUE, NOT NULL           │
│  email               VARCHAR(100)  UNIQUE, NOT NULL           │
│  password_hash       VARCHAR(255)  NOT NULL                   │
│  full_name           VARCHAR(100)  NOT NULL                   │
│  phone               VARCHAR(15)                              │
│  role                ENUM('company_admin','distributor_manager',│
│                       'warehouse_staff','platform_manager',    │
│                       'viewer')                                │
│  assigned_platforms  JSON          (array of platform_connection IDs, for platform_manager)│
│  is_active           BOOLEAN       DEFAULT TRUE               │
│  failed_login_count  INT           DEFAULT 0                  │
│  locked_until        DATETIME      NULL                       │
│  last_login_at       DATETIME      NULL                       │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: product_categories
```
┌──────────────────────────────────────────────────────────────┐
│  product_categories                                          │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  company_id          INT           FOREIGN KEY -> companies.id│
│  name                VARCHAR(100)  NOT NULL                   │
│  parent_category_id  INT           FOREIGN KEY -> product_categories.id (NULL for root)│
│  hsn_code            VARCHAR(10)                              │
│  gst_rate            DECIMAL(5,2)  DEFAULT 18.00              │
│  is_active           BOOLEAN       DEFAULT TRUE               │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: products
```
┌──────────────────────────────────────────────────────────────┐
│  products (Master Product Catalog)                           │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  company_id          INT           FOREIGN KEY -> companies.id│
│  sku                 VARCHAR(50)   UNIQUE, NOT NULL           │
│  name                VARCHAR(200)  NOT NULL                   │
│  description_short   VARCHAR(500)                             │
│  description_long    TEXT                                     │
│  category_id         INT           FOREIGN KEY -> product_categories.id│
│  brand               VARCHAR(100)                             │
│  mrp                 DECIMAL(10,2) NOT NULL                   │
│  distributor_price   DECIMAL(10,2) NOT NULL                   │
│  cost_price          DECIMAL(10,2)                            │
│  weight_grams        INT                                      │
│  length_cm           DECIMAL(7,2)                             │
│  width_cm            DECIMAL(7,2)                             │
│  height_cm           DECIMAL(7,2)                             │
│  hsn_code            VARCHAR(10)                              │
│  gst_rate            DECIMAL(5,2)  DEFAULT 18.00              │
│  status              ENUM('draft','active','discontinued')    │
│  images              JSON          (array of image URLs)      │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: product_variants
```
┌──────────────────────────────────────────────────────────────┐
│  product_variants (Size, Color, etc.)                        │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  product_id          INT           FOREIGN KEY -> products.id │
│  variant_sku         VARCHAR(50)   UNIQUE, NOT NULL           │
│  variant_name        VARCHAR(100)  NOT NULL                   │
│  size                VARCHAR(20)                              │
│  color               VARCHAR(50)                              │
│  mrp                 DECIMAL(10,2)                            │
│  distributor_price   DECIMAL(10,2)                            │
│  weight_grams        INT                                      │
│  barcode             VARCHAR(50)                              │
│  is_active           BOOLEAN       DEFAULT TRUE               │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

### 22.2 Distributor Tables

#### Table: distributors
```
┌──────────────────────────────────────────────────────────────┐
│  distributors                                                │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  company_id          INT           FOREIGN KEY -> companies.id│
│  name                VARCHAR(200)  NOT NULL                   │
│  legal_name          VARCHAR(200)  NOT NULL                   │
│  gstin               VARCHAR(15)   UNIQUE, NOT NULL           │
│  pan                 VARCHAR(10)   NOT NULL                   │
│  region              VARCHAR(200)  NOT NULL                   │
│  address             TEXT          NOT NULL                   │
│  city                VARCHAR(100)                             │
│  state               VARCHAR(100)                             │
│  pincode             VARCHAR(6)                               │
│  contact_person      VARCHAR(100)  NOT NULL                   │
│  contact_email       VARCHAR(100)  NOT NULL                   │
│  contact_phone       VARCHAR(15)   NOT NULL                   │
│  bank_account_name   VARCHAR(200)                             │
│  bank_account_number VARCHAR(20)                              │
│  bank_ifsc           VARCHAR(11)                              │
│  bank_name           VARCHAR(100)                             │
│  credit_limit        DECIMAL(12,2) DEFAULT 0                  │
│  payment_terms_days  INT           DEFAULT 30                 │
│  status              ENUM('active','paused','terminated')     │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: distributor_warehouses
```
┌──────────────────────────────────────────────────────────────┐
│  distributor_warehouses                                      │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  distributor_id      INT           FOREIGN KEY -> distributors.id│
│  name                VARCHAR(100)  NOT NULL                   │
│  address             TEXT          NOT NULL                   │
│  city                VARCHAR(100)                             │
│  state               VARCHAR(100)                             │
│  pincode             VARCHAR(6)    NOT NULL                   │
│  contact_person      VARCHAR(100)                             │
│  contact_phone       VARCHAR(15)                              │
│  is_default          BOOLEAN       DEFAULT FALSE              │
│  is_active           BOOLEAN       DEFAULT TRUE               │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

### 22.3 Platform Tables

#### Table: platforms
```
┌──────────────────────────────────────────────────────────────┐
│  platforms (Master list of supported platforms)               │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  code                VARCHAR(20)   UNIQUE, NOT NULL           │
│                      (e.g., 'amazon','flipkart','meesho')    │
│  name                VARCHAR(100)  NOT NULL                   │
│  logo_url            VARCHAR(500)                             │
│  api_base_url        VARCHAR(500)                             │
│  commission_default  DECIMAL(5,2)  DEFAULT 0                  │
│  return_window_days  INT           DEFAULT 7                  │
│  settlement_cycle_days INT         DEFAULT 7                  │
│  is_active           BOOLEAN       DEFAULT TRUE               │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: platform_connections
```
┌──────────────────────────────────────────────────────────────┐
│  platform_connections (Distributor's account on a platform)  │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  distributor_id      INT           FOREIGN KEY -> distributors.id│
│  platform_id         INT           FOREIGN KEY -> platforms.id│
│  seller_id           VARCHAR(100)  NOT NULL                   │
│  account_name        VARCHAR(200)                             │
│  credentials         TEXT          (encrypted JSON: API keys, tokens, secrets)│
│  sync_frequency_min  INT           DEFAULT 5                  │
│  auto_accept_orders  BOOLEAN       DEFAULT FALSE              │
│  inventory_buffer    INT           DEFAULT 0                  │
│  default_warehouse_id INT          FOREIGN KEY -> distributor_warehouses.id│
│  status              ENUM('connected','disconnected','error') │
│  last_sync_at        DATETIME      NULL                       │
│  last_sync_status    VARCHAR(200)                             │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
│                                                              │
│  UNIQUE(distributor_id, platform_id)                         │
└──────────────────────────────────────────────────────────────┘
```

#### Table: platform_listings
```
┌──────────────────────────────────────────────────────────────┐
│  platform_listings (Product listed on a platform)            │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  platform_connection_id INT        FOREIGN KEY -> platform_connections.id│
│  product_id          INT           FOREIGN KEY -> products.id │
│  variant_id          INT           FOREIGN KEY -> product_variants.id (NULL if no variant)│
│  platform_product_id VARCHAR(100)  (Amazon ASIN, Flipkart FSN, etc.)│
│  platform_sku        VARCHAR(100)                             │
│  listing_url         VARCHAR(500)                             │
│  selling_price       DECIMAL(10,2)                            │
│  platform_commission DECIMAL(5,2)                             │
│  listed_stock        INT           DEFAULT 0                  │
│  status              ENUM('active','inactive','suppressed','blocked')│
│  last_synced_at      DATETIME                                 │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
│                                                              │
│  UNIQUE(platform_connection_id, product_id, variant_id)      │
└──────────────────────────────────────────────────────────────┘
```

### 22.4 Primary Sales Tables

#### Table: stock_transfers
```
┌──────────────────────────────────────────────────────────────┐
│  stock_transfers (Company -> Distributor stock movement)      │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  sto_number          VARCHAR(20)   UNIQUE, NOT NULL           │
│  company_id          INT           FOREIGN KEY -> companies.id│
│  distributor_id      INT           FOREIGN KEY -> distributors.id│
│  status              ENUM('created','approved','packed',      │
│                       'shipped','in_transit','received',      │
│                       'completed','cancelled')                │
│  subtotal            DECIMAL(12,2) NOT NULL                   │
│  gst_amount          DECIMAL(12,2) NOT NULL                   │
│  total_amount        DECIMAL(12,2) NOT NULL                   │
│  payment_terms_days  INT           DEFAULT 30                 │
│  payment_due_date    DATE                                     │
│  invoice_number      VARCHAR(50)                              │
│  invoice_url         VARCHAR(500)                             │
│  tracking_number     VARCHAR(100)                             │
│  logistics_provider  VARCHAR(100)                             │
│  shipped_at          DATETIME                                 │
│  received_at         DATETIME                                 │
│  completed_at        DATETIME                                 │
│  notes               TEXT                                     │
│  created_by          INT           FOREIGN KEY -> app_users.id│
│  approved_by         INT           FOREIGN KEY -> app_users.id│
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: stock_transfer_items
```
┌──────────────────────────────────────────────────────────────┐
│  stock_transfer_items                                        │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  stock_transfer_id   INT           FOREIGN KEY -> stock_transfers.id│
│  product_id          INT           FOREIGN KEY -> products.id │
│  variant_id          INT           FOREIGN KEY -> product_variants.id│
│  quantity_sent       INT           NOT NULL                   │
│  quantity_received   INT           DEFAULT 0                  │
│  quantity_damaged    INT           DEFAULT 0                  │
│  unit_price          DECIMAL(10,2) NOT NULL                   │
│  gst_rate            DECIMAL(5,2)  NOT NULL                   │
│  line_total          DECIMAL(12,2) NOT NULL                   │
│  discrepancy_notes   TEXT                                     │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

### 22.5 Secondary Sales / Order Tables

#### Table: orders
```
┌──────────────────────────────────────────────────────────────┐
│  orders (Unified order from all platforms)                    │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  order_number        VARCHAR(30)   UNIQUE, NOT NULL           │
│  platform_connection_id INT        FOREIGN KEY -> platform_connections.id│
│  platform_order_id   VARCHAR(100)  NOT NULL                   │
│  distributor_id      INT           FOREIGN KEY -> distributors.id│
│  warehouse_id        INT           FOREIGN KEY -> distributor_warehouses.id│
│  customer_name       VARCHAR(200)                             │
│  customer_address    TEXT                                     │
│  customer_city       VARCHAR(100)                             │
│  customer_state      VARCHAR(100)                             │
│  customer_pincode    VARCHAR(6)                               │
│  customer_phone      VARCHAR(15)                              │
│  order_date          DATETIME      NOT NULL                   │
│  ship_by_date        DATETIME                                 │
│  status              ENUM('pending','confirmed','processing', │
│                       'shipped','in_transit','delivered',     │
│                       'completed','cancelled','rto','failed') │
│  subtotal            DECIMAL(10,2)                            │
│  shipping_charge     DECIMAL(10,2) DEFAULT 0                  │
│  discount            DECIMAL(10,2) DEFAULT 0                  │
│  total_amount        DECIMAL(10,2) NOT NULL                   │
│  platform_fees_total DECIMAL(10,2) DEFAULT 0                  │
│  net_receivable      DECIMAL(10,2) DEFAULT 0                  │
│  tracking_number     VARCHAR(100)                             │
│  courier_name        VARCHAR(100)                             │
│  shipped_at          DATETIME                                 │
│  delivered_at        DATETIME                                 │
│  fulfilled_by        INT           FOREIGN KEY -> app_users.id│
│  cancellation_reason TEXT                                     │
│  platform_raw_data   JSON          (original order JSON from platform)│
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
│                                                              │
│  UNIQUE(platform_connection_id, platform_order_id)           │
└──────────────────────────────────────────────────────────────┘
```

#### Table: order_items
```
┌──────────────────────────────────────────────────────────────┐
│  order_items                                                 │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  order_id            INT           FOREIGN KEY -> orders.id   │
│  product_id          INT           FOREIGN KEY -> products.id │
│  variant_id          INT           FOREIGN KEY -> product_variants.id│
│  platform_item_id    VARCHAR(100)                             │
│  quantity            INT           NOT NULL                   │
│  selling_price       DECIMAL(10,2) NOT NULL                   │
│  mrp                 DECIMAL(10,2)                            │
│  discount            DECIMAL(10,2) DEFAULT 0                  │
│  tax_amount          DECIMAL(10,2) DEFAULT 0                  │
│  line_total          DECIMAL(10,2) NOT NULL                   │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: platform_fees
```
┌──────────────────────────────────────────────────────────────┐
│  platform_fees (Detailed fee breakdown per order)            │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  order_id            INT           FOREIGN KEY -> orders.id   │
│  fee_type            ENUM('commission','closing_fee',         │
│                       'shipping_fee','weight_handling',       │
│                       'fixed_fee','collection_fee',          │
│                       'gst_on_fees','tcs','tds',             │
│                       'penalty','promotion_cost','other')    │
│  amount              DECIMAL(10,2) NOT NULL                   │
│  description         VARCHAR(200)                             │
│  created_at          DATETIME      DEFAULT NOW()              │
└──────────────────────────────────────────────────────────────┘
```

### 22.6 Inventory Tables

#### Table: inventory (Company warehouse)
```
┌──────────────────────────────────────────────────────────────┐
│  inventory (Company central warehouse stock)                 │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  company_id          INT           FOREIGN KEY -> companies.id│
│  product_id          INT           FOREIGN KEY -> products.id │
│  variant_id          INT           FOREIGN KEY -> product_variants.id│
│  quantity            INT           NOT NULL, DEFAULT 0        │
│  reserved_quantity   INT           DEFAULT 0                  │
│                      (reserved for approved but not shipped STOs)│
│  min_threshold       INT           DEFAULT 0                  │
│  location            VARCHAR(50)   (rack/bin location)        │
│  last_counted_at     DATETIME                                 │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
│                                                              │
│  UNIQUE(company_id, product_id, variant_id)                  │
└──────────────────────────────────────────────────────────────┘
```

#### Table: distributor_inventory
```
┌──────────────────────────────────────────────────────────────┐
│  distributor_inventory (Distributor warehouse stock)          │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  distributor_id      INT           FOREIGN KEY -> distributors.id│
│  warehouse_id        INT           FOREIGN KEY -> distributor_warehouses.id│
│  product_id          INT           FOREIGN KEY -> products.id │
│  variant_id          INT           FOREIGN KEY -> product_variants.id│
│  quantity            INT           NOT NULL, DEFAULT 0        │
│  reserved_quantity   INT           DEFAULT 0                  │
│                      (reserved for confirmed but not shipped orders)│
│  min_threshold       INT           DEFAULT 0                  │
│  location            VARCHAR(50)   (rack/bin location)        │
│  last_counted_at     DATETIME                                 │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
│                                                              │
│  UNIQUE(warehouse_id, product_id, variant_id)                │
└──────────────────────────────────────────────────────────────┘
```

#### Table: inventory_log
```
┌──────────────────────────────────────────────────────────────┐
│  inventory_log (Audit trail for every stock change)          │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  inventory_level     ENUM('company','distributor')            │
│  distributor_id      INT           (NULL for company level)   │
│  warehouse_id        INT                                      │
│  product_id          INT           NOT NULL                   │
│  variant_id          INT                                      │
│  action              ENUM('stock_transfer_out','stock_transfer_in',│
│                       'order_fulfillment','return_restock',   │
│                       'adjustment_add','adjustment_deduct',   │
│                       'damage','initial_stock')               │
│  old_quantity        INT           NOT NULL                   │
│  new_quantity        INT           NOT NULL                   │
│  change_quantity     INT           NOT NULL                   │
│                      (positive = added, negative = deducted)  │
│  reason              VARCHAR(500)                             │
│  reference_type      VARCHAR(50)   (STO/ORDER/RETURN/MANUAL) │
│  reference_id        VARCHAR(50)                              │
│  performed_by        INT           FOREIGN KEY -> app_users.id│
│  ip_address          VARCHAR(45)                              │
│  created_at          DATETIME      DEFAULT NOW()              │
│                                                              │
│  NOTE: This table is APPEND-ONLY. No updates or deletes.    │
└──────────────────────────────────────────────────────────────┘
```

### 22.7 Returns & Payments Tables

#### Table: returns
```
┌──────────────────────────────────────────────────────────────┐
│  returns                                                     │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  order_id            INT           FOREIGN KEY -> orders.id   │
│  platform_connection_id INT        FOREIGN KEY -> platform_connections.id│
│  distributor_id      INT           FOREIGN KEY -> distributors.id│
│  platform_return_id  VARCHAR(100)                             │
│  return_type         ENUM('customer_return','rto',            │
│                       'seller_initiated','replacement')       │
│  reason              VARCHAR(500)                             │
│  status              ENUM('initiated','in_transit','received',│
│                       'inspected','restocked','rejected',     │
│                       'disputed','closed')                    │
│  refund_amount       DECIMAL(10,2)                            │
│  refund_status       ENUM('pending','processed','deducted')   │
│  condition           ENUM('good','minor_damage','major_damage',│
│                       'wrong_item','missing')                 │
│  condition_notes     TEXT                                     │
│  condition_images    JSON          (array of image URLs)      │
│  received_at         DATETIME                                 │
│  inspected_at        DATETIME                                 │
│  inspected_by        INT           FOREIGN KEY -> app_users.id│
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: return_items
```
┌──────────────────────────────────────────────────────────────┐
│  return_items                                                │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  return_id           INT           FOREIGN KEY -> returns.id  │
│  order_item_id       INT           FOREIGN KEY -> order_items.id│
│  product_id          INT           FOREIGN KEY -> products.id │
│  variant_id          INT           FOREIGN KEY -> product_variants.id│
│  quantity_returned   INT           NOT NULL                   │
│  quantity_restocked  INT           DEFAULT 0                  │
│  condition           ENUM('good','damaged','missing')         │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: settlement_transactions
```
┌──────────────────────────────────────────────────────────────┐
│  settlement_transactions (Platform payments to Distributor)  │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  platform_connection_id INT        FOREIGN KEY -> platform_connections.id│
│  distributor_id      INT           FOREIGN KEY -> distributors.id│
│  settlement_id       VARCHAR(100)  (Platform's settlement reference)│
│  settlement_date     DATE          NOT NULL                   │
│  period_from         DATE                                     │
│  period_to           DATE                                     │
│  gross_amount        DECIMAL(12,2)                            │
│  total_fees          DECIMAL(12,2)                            │
│  total_returns       DECIMAL(12,2)                            │
│  net_amount          DECIMAL(12,2) NOT NULL                   │
│  expected_amount     DECIMAL(12,2)                            │
│  discrepancy         DECIMAL(12,2) DEFAULT 0                  │
│  status              ENUM('expected','received','reconciled', │
│                       'disputed')                             │
│  bank_reference      VARCHAR(100)                             │
│  notes               TEXT                                     │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: distributor_payments
```
┌──────────────────────────────────────────────────────────────┐
│  distributor_payments (Distributor paying Company for stock)  │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  distributor_id      INT           FOREIGN KEY -> distributors.id│
│  stock_transfer_id   INT           FOREIGN KEY -> stock_transfers.id (NULL for general payment)│
│  amount              DECIMAL(12,2) NOT NULL                   │
│  payment_method      ENUM('neft','rtgs','upi','cheque','cash')│
│  payment_reference   VARCHAR(100)                             │
│  payment_date        DATE          NOT NULL                   │
│  status              ENUM('pending','confirmed','rejected')   │
│  confirmed_by        INT           FOREIGN KEY -> app_users.id│
│  confirmed_at        DATETIME                                 │
│  notes               TEXT                                     │
│  created_at          DATETIME      DEFAULT NOW()              │
│  updated_at          DATETIME      DEFAULT NOW() ON UPDATE    │
└──────────────────────────────────────────────────────────────┘
```

### 22.8 Support Tables

#### Table: notifications
```
┌──────────────────────────────────────────────────────────────┐
│  notifications                                               │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  user_id             INT           FOREIGN KEY -> app_users.id│
│  type                VARCHAR(50)   NOT NULL                   │
│  title               VARCHAR(200)  NOT NULL                   │
│  message             TEXT                                     │
│  severity            ENUM('info','warning','critical')        │
│  reference_type      VARCHAR(50)   (ORDER/RETURN/STO/INVENTORY/PLATFORM)│
│  reference_id        VARCHAR(50)                              │
│  platform_id         INT                                      │
│  distributor_id      INT                                      │
│  is_read             BOOLEAN       DEFAULT FALSE              │
│  created_at          DATETIME      DEFAULT NOW()              │
└──────────────────────────────────────────────────────────────┘
```

#### Table: email_queue
```
┌──────────────────────────────────────────────────────────────┐
│  email_queue                                                 │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  to_email            VARCHAR(100)  NOT NULL                   │
│  subject             VARCHAR(200)  NOT NULL                   │
│  body                TEXT          NOT NULL                   │
│  status              ENUM('pending','sent','failed',          │
│                       'abandoned')  DEFAULT 'pending'         │
│  retry_count         INT           DEFAULT 0                  │
│  sent_at             DATETIME      NULL                       │
│  error_message       TEXT                                     │
│  created_at          DATETIME      DEFAULT NOW()              │
└──────────────────────────────────────────────────────────────┘
```

#### Table: audit_log
```
┌──────────────────────────────────────────────────────────────┐
│  audit_log (Master audit trail)                              │
├──────────────────────────────────────────────────────────────┤
│  id                  BIGINT        PRIMARY KEY, AUTO_INCREMENT│
│  user_id             INT           FOREIGN KEY -> app_users.id│
│  distributor_id      INT                                      │
│  platform_id         INT                                      │
│  action              VARCHAR(100)  NOT NULL                   │
│  entity_type         VARCHAR(50)   NOT NULL                   │
│                      (product/order/return/inventory/sto/user/platform)│
│  entity_id           VARCHAR(50)                              │
│  old_value           JSON                                     │
│  new_value           JSON                                     │
│  ip_address          VARCHAR(45)                              │
│  user_agent          VARCHAR(500)                             │
│  created_at          DATETIME      DEFAULT NOW()              │
│                                                              │
│  NOTE: This table is APPEND-ONLY. No updates or deletes.    │
│  Indexed on: user_id, entity_type, entity_id, created_at    │
└──────────────────────────────────────────────────────────────┘
```

#### Table: sync_log
```
┌──────────────────────────────────────────────────────────────┐
│  sync_log (Platform API sync tracking)                       │
├──────────────────────────────────────────────────────────────┤
│  id                  INT           PRIMARY KEY, AUTO_INCREMENT│
│  platform_connection_id INT        FOREIGN KEY -> platform_connections.id│
│  sync_type           ENUM('orders','inventory','returns',     │
│                       'settlements','listings')               │
│  direction           ENUM('pull','push')                      │
│  status              ENUM('success','partial','failed')       │
│  records_processed   INT           DEFAULT 0                  │
│  records_failed      INT           DEFAULT 0                  │
│  error_message       TEXT                                     │
│  started_at          DATETIME      NOT NULL                   │
│  completed_at        DATETIME                                 │
│  created_at          DATETIME      DEFAULT NOW()              │
└──────────────────────────────────────────────────────────────┘
```

---

## 23. ER Model (Entity Relationship Diagram)

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║                          ENTITY RELATIONSHIP DIAGRAM                           ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  ┌────────────┐                                                                ║
║  │ companies  │                                                                ║
║  └──────┬─────┘                                                                ║
║         │                                                                      ║
║         │ 1:N                                                                  ║
║         ├──────────────────────────────────────────────┐                        ║
║         │                    │                         │                        ║
║         ▼                    ▼                         ▼                        ║
║  ┌──────────────┐    ┌──────────────┐         ┌────────────┐                   ║
║  │  app_users   │    │ distributors │         │  products  │                   ║
║  └──────────────┘    └──────┬───────┘         └──────┬─────┘                   ║
║                             │                        │                         ║
║                     ┌───────┼──────────┐             │ 1:N                     ║
║                     │       │          │             │                         ║
║                     ▼       ▼          ▼             ▼                         ║
║              ┌──────────┐ ┌────────┐ ┌──────┐ ┌───────────────┐               ║
║              │dist_     │ │platform│ │stock_│ │product_       │               ║
║              │warehouses│ │_conn.  │ │trans.│ │variants       │               ║
║              └────┬─────┘ └───┬────┘ └──┬───┘ └───────────────┘               ║
║                   │           │         │                                      ║
║                   │     ┌─────┤         │                                      ║
║                   │     │     │         ▼                                      ║
║                   │     │     │    ┌──────────────┐                             ║
║                   │     │     │    │stock_transfer│                             ║
║                   │     │     │    │_items        │                             ║
║                   │     │     │    └──────────────┘                             ║
║                   │     │     │                                                 ║
║                   │     ▼     ▼                                                ║
║                   │  ┌──────────────┐  ┌──────────────┐                       ║
║                   │  │platform_     │  │  orders      │                       ║
║                   │  │listings      │  └──────┬───────┘                       ║
║                   │  └──────────────┘         │                               ║
║                   │                    ┌──────┼──────────┐                     ║
║                   │                    │      │          │                     ║
║                   │                    ▼      ▼          ▼                     ║
║                   │             ┌──────────┐┌────────┐┌──────────┐            ║
║                   │             │order_    ││platform││ returns  │            ║
║                   │             │items     ││_fees   │└────┬─────┘            ║
║                   │             └──────────┘└────────┘     │                  ║
║                   │                                        │                  ║
║                   │                                        ▼                  ║
║                   │                                  ┌──────────┐            ║
║                   │                                  │return_   │            ║
║                   │                                  │items     │            ║
║                   │                                  └──────────┘            ║
║                   │                                                          ║
║                   ▼                                                          ║
║            ┌──────────────────┐     ┌─────────────────────┐                  ║
║            │distributor_      │     │settlement_          │                  ║
║            │inventory         │     │transactions         │                  ║
║            └──────────────────┘     └─────────────────────┘                  ║
║                                                                              ║
║  CROSS-CUTTING TABLES (linked to multiple entities):                         ║
║  ┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      ║
║  │inventory_log │ │audit_log │ │sync_log  │ │notific.  │ │email_    │      ║
║  └──────────────┘ └──────────┘ └──────────┘ └──────────┘ │queue     │      ║
║                                                           └──────────┘      ║
║                                                                              ║
║  KEY RELATIONSHIPS:                                                          ║
║  - companies 1:N distributors (Company has many distributors)                ║
║  - companies 1:N products (Company has product catalog)                      ║
║  - companies 1:N app_users (Company has users)                               ║
║  - distributors 1:N distributor_warehouses                                   ║
║  - distributors 1:N platform_connections (each platform account)            ║
║  - distributors 1:N stock_transfers (receives stock from company)           ║
║  - platform_connections 1:N orders (orders from that platform account)      ║
║  - platform_connections 1:N platform_listings (products listed)             ║
║  - orders 1:N order_items                                                   ║
║  - orders 1:N platform_fees                                                 ║
║  - orders 1:N returns                                                       ║
║  - returns 1:N return_items                                                 ║
║  - products 1:N product_variants                                            ║
║  - stock_transfers 1:N stock_transfer_items                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

---

## 24. Platform-Specific Integration Details

### 24.1 Amazon SP-API Integration

```
AMAZON SELLING PARTNER API (SP-API):

  Authentication:
  - LWA (Login with Amazon) OAuth 2.0
  - Requires: Client ID, Client Secret, Refresh Token
  - Access token refreshed automatically (1 hour expiry)

  Key API Endpoints Used:
  ┌────────────────────────────────────────────────────────────────┐
  │ Purpose          │ Endpoint                     │ Method     │
  ├────────────────────────────────────────────────────────────────┤
  │ Get Orders       │ /orders/v0/orders            │ GET        │
  │ Get Order Items  │ /orders/v0/orders/{id}/items │ GET        │
  │ Update Inventory │ /feeds/2021-06-30/feeds      │ POST (feed)│
  │ Create Shipment  │ /shipping/v2/shipments       │ POST       │
  │ Get Reports      │ /reports/2021-06-30/reports   │ GET/POST   │
  │ Get Settlements  │ /finances/v0/financialEvents  │ GET        │
  │ Get Returns      │ /fba/returns/v0/returns       │ GET        │
  └────────────────────────────────────────────────────────────────┘

  Rate Limits:
  - Orders API: 1 request/second burst, 1/second sustained
  - Feeds API: 30 requests/minute
  - Must handle 429 (Too Many Requests) with exponential backoff

  Order Status Mapping:
  Amazon Status     -> Our Unified Status
  ────────────       ───────────────────
  Pending           -> PENDING
  Unshipped         -> CONFIRMED
  Shipped           -> SHIPPED
  Canceled          -> CANCELLED
  Unfulfillable     -> FAILED

  Inventory Sync:
  - Use POST_INVENTORY_AVAILABILITY_DATA feed
  - Submit XML/JSON with SKU + quantity
  - Feed processing takes 5-15 minutes
```

### 24.2 Flipkart Seller API Integration

```
FLIPKART SELLER API:

  Authentication:
  - OAuth 2.0 (Client Credentials)
  - Application ID + Secret -> Access Token
  - Token validity: varies

  Key API Endpoints Used:
  ┌────────────────────────────────────────────────────────────────┐
  │ Purpose          │ Endpoint                     │ Method     │
  ├────────────────────────────────────────────────────────────────┤
  │ Search Orders    │ /orders/search               │ POST       │
  │ Get Order Detail │ /orders/{order_id}           │ GET        │
  │ Update Inventory │ /listings/update              │ POST       │
  │ Create Shipment  │ /shipments/create            │ POST       │
  │ Get Labels       │ /shipments/{id}/labels       │ GET        │
  │ Dispatch         │ /shipments/dispatch          │ POST       │
  │ Get Returns      │ /returns                     │ GET        │
  │ Get Settlements  │ /payments/settlements        │ GET        │
  └────────────────────────────────────────────────────────────────┘

  Order Status Mapping:
  Flipkart Status    -> Our Unified Status
  ────────────────    ───────────────────
  APPROVED           -> CONFIRMED
  PACKED             -> PROCESSING
  READY_TO_DISPATCH  -> PROCESSING
  SHIPPED            -> SHIPPED
  DELIVERED          -> DELIVERED
  CANCELLED          -> CANCELLED
  RETURN_REQUESTED   -> (triggers return flow)
```

### 24.3 Meesho Supplier API Integration

```
MEESHO SUPPLIER API:

  Authentication:
  - API Token (Bearer token)
  - Supplier ID

  Key API Endpoints Used:
  ┌────────────────────────────────────────────────────────────────┐
  │ Purpose          │ Endpoint                     │ Method     │
  ├────────────────────────────────────────────────────────────────┤
  │ Get Orders       │ /api/v1/orders               │ GET        │
  │ Accept Order     │ /api/v1/orders/{id}/accept   │ POST       │
  │ Generate Label   │ /api/v1/shipments/label      │ POST       │
  │ Dispatch         │ /api/v1/shipments/dispatch   │ POST       │
  │ Get Returns      │ /api/v1/returns              │ GET        │
  │ Update Inventory │ /api/v1/inventory/update     │ POST       │
  └────────────────────────────────────────────────────────────────┘

  Special Notes:
  - Meesho uses 0% commission model (margin-based)
  - Supplier sets a supply price; Meesho sets selling price
  - Shipping is handled by Meesho logistics (mandatory)
  - Returns are deducted from next payout
```

### 24.4 Myntra Partner Portal Integration

```
MYNTRA PARTNER API:

  Authentication:
  - Partner credentials (Partner ID + Secret)
  - OAuth 2.0 token exchange

  Key Endpoints:
  - Order fetch, shipment creation, label generation
  - Inventory update
  - Return processing

  Special Notes:
  - Myntra is fashion-focused — strict quality guidelines
  - Mandatory Myntra logistics (no self-ship option for most)
  - Higher commission rates (10-25%) but higher ASP (Average Selling Price)
  - Seasonal sale events require inventory lock-in
```

### 24.5 JioMart & Snapdeal Integration

```
JIOMART SELLER API:
  - REST API with API key authentication
  - Standard order/inventory/shipment endpoints
  - Growing platform with increasing order volume
  - Self-ship option available

SNAPDEAL SELLER API:
  - REST API with seller credentials
  - Standard order/inventory/shipment endpoints
  - Lower average order value
  - Self-ship and Snapdeal logistics options
```

### 24.6 Adding a New Platform (Plugin Architecture)

```
TO ADD SUPPORT FOR A NEW PLATFORM:

  Step 1: Create Platform Adapter
  ────────────────────────────────
  Implement the PlatformAdapter interface:

  Interface PlatformAdapter:
    - connect(credentials)      -> validate and store
    - pullOrders(since_date)    -> return unified order format
    - pushInventory(sku, qty)   -> update stock on platform
    - createShipment(order)     -> return tracking info
    - generateLabel(shipment)   -> return label PDF
    - pullReturns(since_date)   -> return unified return format
    - pullSettlements(period)   -> return settlement data

  Step 2: Add platform to 'platforms' table
  Step 3: Add status mapping configuration
  Step 4: Add fee structure configuration
  Step 5: Test with sandbox/staging API
  Step 6: Deploy

  TIME TO ADD NEW PLATFORM: ~1-2 weeks (if platform has API)
```

---

## 25. Complete Flow Diagrams

### 25.1 End-to-End System Flow

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                        COMPLETE SYSTEM FLOW                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  PHASE 1: PRODUCT SETUP                                                    ║
║  ──────────────────────                                                    ║
║  Company Admin adds products to catalog                                    ║
║  -> SKU, name, images, pricing (MRP + distributor price)                   ║
║  -> Products available for distribution and platform listing               ║
║                                                                            ║
║  PHASE 2: PRIMARY SALES (Company -> Distributor)                           ║
║  ───────────────────────────────────────────────                           ║
║  Company creates Stock Transfer Order (STO)                                ║
║  -> Select distributor + products + quantities                             ║
║  -> Generate invoice                                                       ║
║  -> Ship from Company warehouse                                            ║
║  -> Distributor receives and acknowledges                                  ║
║  -> Company inventory decreases, Distributor inventory increases           ║
║                                                                            ║
║  PHASE 3: PLATFORM LISTING                                                 ║
║  ────────────────────────                                                  ║
║  Distributor connects platform accounts (Amazon, Flipkart, etc.)          ║
║  -> Configure pricing per platform (MRP + margin)                          ║
║  -> Allocate inventory per platform                                        ║
║  -> Push listings and stock to each platform API                           ║
║  -> Products now live and purchasable on platforms                         ║
║                                                                            ║
║  PHASE 4: SECONDARY SALES (Platform -> End Customer)                       ║
║  ───────────────────────────────────────────────────                       ║
║  Customer places order on Amazon/Flipkart/Meesho/etc.                      ║
║  -> MPEMS syncs order via platform API (every 5 min)                       ║
║  -> Order appears in Unified Order View                                    ║
║  -> Warehouse staff picks, packs, ships                                    ║
║  -> Shipping label generated via platform API                              ║
║  -> Tracking updated on platform                                           ║
║  -> Inventory auto-deducted and synced to all platforms                    ║
║                                                                            ║
║  PHASE 5: DELIVERY & RETURNS                                               ║
║  ───────────────────────────                                               ║
║  Order delivered to customer                                               ║
║  -> Platform confirms delivery                                             ║
║  -> If customer returns:                                                   ║
║     -> Return synced to MPEMS                                              ║
║     -> Item received at warehouse                                          ║
║     -> Inspected -> Restocked or rejected                                  ║
║     -> Refund handled by platform (deducted from settlement)               ║
║                                                                            ║
║  PHASE 6: PAYMENTS & RECONCILIATION                                        ║
║  ─────────────────────────────────                                         ║
║  Platform settles payments to Distributor (weekly/biweekly)               ║
║  -> MPEMS tracks each settlement                                           ║
║  -> Compares expected vs actual (flags discrepancies)                      ║
║  -> Distributor pays Company for stock received                            ║
║  -> MPEMS tracks outstanding balances                                      ║
║                                                                            ║
║  PHASE 7: MONITORING & ANALYTICS                                           ║
║  ───────────────────────────────                                           ║
║  Dashboard -> Real-time view of all platforms                              ║
║  Reports -> Cross-platform comparison, distributor performance             ║
║  Alerts -> Low stock, SLA breach, payment overdue                          ║
║  Audit -> Complete trail of every action                                   ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### 25.2 Order Lifecycle Flow (Across Platforms)

```
    CUSTOMER                  PLATFORM                  MPEMS (OUR APP)
    ────────                  ────────                  ──────────────
       │                         │                           │
       │  Places Order           │                           │
       ├────────────────────────>│                           │
       │                         │                           │
       │                         │  API Sync (every 5 min)   │
       │                         │<──────────────────────────┤
       │                         │                           │
       │                         │  Returns new orders       │
       │                         ├──────────────────────────>│
       │                         │                           │
       │                         │                   ┌───────▼──────┐
       │                         │                   │ NORMALIZE    │
       │                         │                   │ STORE        │
       │                         │                   │ NOTIFY STAFF │
       │                         │                   └───────┬──────┘
       │                         │                           │
       │                         │                   Staff picks & packs
       │                         │                           │
       │                         │  Generate label API       │
       │                         │<──────────────────────────┤
       │                         │                           │
       │                         │  Returns label PDF        │
       │                         ├──────────────────────────>│
       │                         │                           │
       │                         │                   Print label, pack
       │                         │                           │
       │                         │  Confirm shipment API     │
       │                         │<──────────────────────────┤
       │                         │                           │
       │  Tracking notification  │                   Update inventory
       │<────────────────────────┤                   Sync to platforms
       │                         │                           │
       │  Delivery               │                           │
       │<────────────────────────┤  Delivery confirmation    │
       │                         ├──────────────────────────>│
       │                         │                           │
       │                         │                   Status = DELIVERED
       │                         │                   Settlement expected
       │                         │                           │
```

---

## 26. Error Handling

### 26.1 Platform API Errors

| Scenario                          | Error                                     | Action                              |
|-----------------------------------|-------------------------------------------|-------------------------------------|
| Platform API unreachable          | Connection timeout                        | Retry 3x, then alert admin          |
| Invalid credentials               | 401 Unauthorized                          | Mark platform as ERROR, notify user |
| Rate limit exceeded               | 429 Too Many Requests                     | Exponential backoff (1s, 2s, 4s...) |
| Order sync failure                | Partial data or parsing error             | Log error, skip order, retry next sync |
| Inventory push failure            | Platform rejected update                  | Log, retry, alert if repeated       |
| Label generation failure          | Platform API error                        | Show error, allow manual label      |

### 26.2 Business Logic Errors

| Scenario                          | Error Message                                      | Action                     |
|-----------------------------------|----------------------------------------------------|----------------------------|
| Insufficient stock for order       | "Not enough stock for [item]. Available: X"        | Cannot fulfill, suggest STO|
| Stock changed during fulfillment   | "Stock has changed! Please review again."          | Reload and retry           |
| Distributor credit limit exceeded  | "Credit limit exceeded. Outstanding: Rs. X"        | Block STO, notify admin    |
| Platform listing suppressed        | "Listing suppressed on [Platform]. Reason: X"      | Alert, show fix steps      |
| Settlement discrepancy detected    | "Expected Rs. X, received Rs. Y. Difference: Rs. Z"| Flag for review            |
| STO quantity exceeds stock         | "Company warehouse has only X units of [SKU]"      | Adjust quantity            |

### 26.3 System Error Handling

```
- All database operations use TRANSACTIONS
- If any step fails -> ROLLBACK entire transaction
- No partial database updates (atomic operations)
- All errors logged with: timestamp, user, action, error details, stack trace
- Critical errors -> Alert admin immediately (email + in-app)
- Platform sync errors -> Logged in sync_log table with full details
- API response codes:
    200 = Success
    201 = Created
    400 = Bad request (validation error)
    401 = Unauthorized (not logged in)
    403 = Forbidden (no permission / wrong scope)
    404 = Not found
    409 = Conflict (race condition / duplicate)
    429 = Rate limited
    500 = Server error
    502 = Platform API unavailable
    503 = Service temporarily unavailable
```

---

## 27. Security Considerations

### 27.1 Authentication Security
```
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with short expiry (8 hours access, 7 days refresh)
- Account lockout after 5 failed attempts (30 minutes)
- HTTPS only (SSL/TLS encryption) -- all traffic
- Session invalidation on logout
- Multi-device session support with individual revocation
```

### 27.2 Authorization Security
```
- Role-based access control (RBAC) with scope filtering
- Every API endpoint checks: role + distributor scope + platform scope
- Users ONLY see data within their authorized scope
- Admin actions logged with IP address
- Sensitive operations require re-authentication (e.g., changing credentials)
```

### 27.3 Data Security
```
- Platform API credentials encrypted at rest (AES-256)
- Database credentials in environment variables (not in code)
- Customer PII (phone, address) masked in UI based on role
- Customer data not stored beyond what platforms provide
- XSS prevention (input sanitization, output encoding)
- CSRF tokens on all forms
- SQL injection prevention (parameterized queries / ORM)
- Rate limiting on all API endpoints
- No sensitive data in URLs or client-side logs
```

### 27.4 Platform Security
```
- Each platform connection uses encrypted credential storage
- API tokens refreshed automatically before expiry
- Webhook signatures verified (where platforms support)
- Platform API calls logged for audit
- Credentials never exposed to frontend
- Connection test before storing credentials
```

### 27.5 Infrastructure Security
```
- Database access restricted to application servers only
- Regular automated backups (daily full, hourly incremental)
- Audit logs are append-only (no edit/delete even by admin)
- Environment separation: Development / Staging / Production
- Dependency vulnerability scanning (npm audit / pip audit)
- Regular security patches and updates
```

---

## 28. Tech Stack Recommendation

| Layer              | Technology                              | Why                                          |
|--------------------|-----------------------------------------|----------------------------------------------|
| Frontend           | React.js / Next.js                      | Modern, fast, large ecosystem, SSR support   |
| UI Library         | Ant Design or Shadcn UI                 | Pre-built business components, tables, charts|
| State Management   | Redux Toolkit / Zustand                 | Manage complex multi-platform state          |
| Backend            | Node.js + Express / NestJS              | JavaScript full stack, async I/O for APIs    |
| Database           | PostgreSQL                              | Robust, JSON support, good for complex queries|
| ORM                | Prisma                                  | Type-safe queries, easy migrations           |
| Cache              | Redis                                   | API rate limit tracking, session store, queue |
| Job Queue          | BullMQ (Redis-backed)                   | Platform sync jobs, email queue, retries     |
| Auth               | JWT + bcrypt + Refresh Tokens           | Stateless, secure, multi-device              |
| API Documentation  | Swagger / OpenAPI 3.0                   | Auto-generated API docs                      |
| Email              | Nodemailer + SendGrid                   | Reliable email delivery                      |
| File Storage       | AWS S3 / Cloudflare R2                  | Product images, invoices, labels             |
| Real-time          | Socket.io                               | Live notifications, order updates            |
| Charts             | Recharts / Apache ECharts               | Cross-platform analytics dashboards          |
| Testing            | Jest + React Testing Library            | Unit and integration tests                   |
| CI/CD              | GitHub Actions                          | Automated testing and deployment             |
| Monitoring         | Sentry (errors) + Prometheus (metrics)  | Production monitoring and alerting           |

---

## 29. Build Priority Order

### Phase 1: Foundation (Week 1-3)
```
- Database setup (all tables)
- User authentication (login/logout/roles/JWT)
- Company profile setup
- Product catalog CRUD (add/edit/view products)
- Basic UI framework (layout, navigation, routing)
```

### Phase 2: Distributor & Primary Sales (Week 4-6)
```
- Distributor management (CRUD)
- Distributor warehouse management
- Stock Transfer Order (STO) creation and lifecycle
- Company inventory management
- Distributor inventory management
- Invoice generation for STOs
- Distributor receipt and acknowledgment flow
```

### Phase 3: Platform Integration - Core (Week 7-10)
```
- Platform connection framework (adapter pattern)
- Amazon SP-API integration (orders + inventory)
- Flipkart API integration (orders + inventory)
- Unified order view (2 platforms)
- Order sync service (polling)
- Inventory sync to platforms (push)
- Basic fulfillment flow (pick/pack/ship)
```

### Phase 4: Full Multi-Platform (Week 11-14)
```
- Meesho API integration
- Myntra API integration
- JioMart API integration
- Snapdeal API integration
- Batch fulfillment
- Shipping label generation per platform
- Platform-specific status mapping
```

### Phase 5: Returns & Payments (Week 15-17)
```
- Return sync from all platforms
- Return processing workflow (receive/inspect/restock)
- Settlement tracking per platform
- Platform fee tracking
- Reconciliation dashboard
- Distributor payment tracking (to Company)
```

### Phase 6: Dashboard & Reports (Week 18-20)
```
- Company Admin dashboard (all distributors, all platforms)
- Distributor dashboard (own data)
- Cross-platform sales comparison report
- Distributor performance report
- Product performance report
- Platform fee analysis report
- Inventory aging report
- Settlement reconciliation report
```

### Phase 7: Notifications & Audit (Week 21-22)
```
- In-app notification system (WebSocket)
- Email notification system (queue-based)
- SLA breach alerts
- Low stock alerts
- Complete audit trail
- Activity log UI
```

### Phase 8: Polish & Scale (Week 23-26)
```
- Performance optimization (caching, query optimization)
- Bulk operations (batch order processing)
- Export functionality (CSV, PDF reports)
- Mobile-responsive UI refinement
- Security hardening
- Load testing
- Documentation
- UAT and bug fixes
```

---

## Summary: What This System Manages

### The System DOES:
```
- Manage a master product catalog (Company level)
- Track stock transfers from Company to Distributors (Primary Sales)
- Connect to 6+ e-commerce platforms via APIs
- Unify orders from all platforms into one view
- Manage multi-level inventory (Company / Distributor / Platform)
- Handle platform-specific fulfillment rules
- Process returns per platform's return policy
- Track payments, fees, and settlements per platform
- Provide cross-platform analytics and comparison
- Support multiple distributors with scoped access
- Maintain complete audit trail of every action
- Alert on SLA breaches, low stock, payment issues
```

### The System does NOT:
```
- Sell directly to end customers (that happens on platforms)
- Replace platform seller dashboards (supplements them)
- Handle manufacturing or production planning
- Manage customer support / tickets (handled by platforms)
- Process payments from end customers (handled by platforms)
- Manage platform advertising / marketing campaigns
```

---

## Glossary

| Term               | Definition                                                           |
|--------------------|----------------------------------------------------------------------|
| Primary Sales      | Company selling stock to Distributors (B2B)                          |
| Secondary Sales    | Distributors selling on platforms to end customers (B2C)             |
| STO                | Stock Transfer Order (Company to Distributor shipment)               |
| PO                 | Purchase Order (Order from platform to fulfill)                      |
| SKU                | Stock Keeping Unit (unique product identifier)                       |
| ASIN               | Amazon Standard Identification Number                                |
| FSN                | Flipkart Serial Number                                               |
| MRP                | Maximum Retail Price                                                 |
| ASP                | Average Selling Price                                                |
| SLA                | Service Level Agreement (ship-by deadline)                           |
| RTO                | Return to Origin (failed delivery)                                   |
| TCS                | Tax Collected at Source (by platform)                                |
| TDS                | Tax Deducted at Source                                               |
| HSN                | Harmonized System Nomenclature (GST product classification)         |
| GSTIN              | GST Identification Number                                            |
| Settlement         | Platform paying Distributor for fulfilled orders (after fee deduction)|
| Reconciliation     | Matching expected payments with actual payments received             |
| Platform Adapter   | Code module that handles API communication with a specific platform  |

---

## Document Info

- **Created:** 2026-03-31
- **Updated:** 2026-04-01
- **Version:** 3.0 (Complete rewrite — Multi-Platform E-Commerce Management System)
- **Status:** Planning Phase
- **Scope:** Multi-platform, multi-distributor, unified management system
- **Previous Version:** v2.0 was a single-platform PO fulfillment system
