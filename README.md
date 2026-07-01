# Refinery Supply Chain & Maritime Logistics Dashboard

An economic decision-support dashboard designed to track downstream refinery logistics and market economics. This project automates the extraction of market spot prices and logistics data via Python, models refinery gross margins using DAX, and visualizes dynamic route-profitability metrics across global destination markets.

## 📊 Dashboard Architecture
![Refinery Supply Chain Dashboard](assets/dashboard_preview.jpg)

The dashboard provides real-time visibility into netback margins and supply chain economics:
* **Dynamic Cost Allocation:** Recalculates optimized fuel recipe costs dynamically when filtering by global destination.
* **Risk vs. Return Evaluation:** Utilizes statistical DAX evaluation contexts to heatmap historical margin volatility against raw profitability, identifying highly unstable shipping routes.

## Technical Scope

### 1. Data Engineering & Extraction
* Built an automated data pipeline using **Python (Pandas)** to extract and clean shifting market spot prices, freight costs, and maritime timelines.

### 2. Financial Modeling & Business Intelligence
* **Data Modeling:** Designed a robust star-schema relational model in **Power BI** to handle multi-component chemical blending data across geographic dimensions.
* **Advanced DAX:** Authored complex measures utilizing time-intelligence and statistical iterators (`STDEVX.S`) to model localized refinery margins, crack spreads, and directional risk.
* **Logistics Integration:** Paired Free-on-Board (FOB) refinery costs with variable freight burdens to output Cost, Insurance, and Freight (CIF) metrics.
