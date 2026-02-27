# Flipshop Ops Automation Scripts

This repository contains a growing collection of internal automation scripts built to eliminate manual, repetitive operational work for the Flipshop Ops team.

These scripts were designed to replace error-prone, time-consuming manual processes with safe, repeatable, auditable automations, allowing the Ops team to focus on higher-value work while improving speed and consistency across day-to-day operations.

---

## Purpose

As Flipshop scaled, many operational tasks were being handled manually across dashboards, spreadsheets, and admin tools. These scripts were created to:

- Reduce manual labor and operational overhead
- Minimize human error in high-volume workflows
- Standardize how common operational actions are performed
- Enable faster response to edge cases and compliance needs
- Provide reusable tooling for future operational automation

Each script targets a specific operational task and can be run independently.

---

## Scripts Overview

### Order Management
- **`approve_fcc_orders.py`**  
  Automates approval of orders requiring FCC-related checks.

- **`cancel_banned_device_orders.py`**  
  Identifies and cancels orders containing banned or restricted devices.

- **`cancel_nyc_orders.py`**  
  Cancels orders that violate NYC-specific regulations or constraints.

---

### Catalog & Inventory
- **`disable_skus.py`**  
  Disables SKUs programmatically and in bulk to prevent further sales of restricted or problematic items.

---

### Brand & Account Operations
- **`create_brands.py`**  
  Automates brand creation to reduce manual onboarding effort and ensure consistency.

- **`update_return_addr.py`**  
  Updates return address information across systems to maintain compliance and accuracy.

---

### Shared Infrastructure
- **`main.py`**  
  Entry point for running scripts and shared execution logic.

- **`auth_api.py`**  
  Handles authentication and access token management.

- **`orders_api.py`**, **`items_api.py`**, **`brands_api.py`**  
  API clients used by scripts to interact with Flipshop backend services.

- **`gsheet_utils.py`**  
  Utilities for reading from and writing to Google Sheets when Ops workflows require spreadsheet input or output.