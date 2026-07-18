# End-to-End Refinery Optimization & Digital Twin Engine

This repository contains a production-grade refinery digital twin and quantitative trading engine that bridges deep chemical process engineering with commercial downstream analytics. 

By interfacing a headless DWSIM chemical process simulation with a SciPy Linear Programming (LP) engine and an automated Power BI analytics pipeline, this project models the end-to-end workflow of an Economic Planning & Optimization desk at a downstream energy supermajor.

---

## 📊 Live Dashboard Demonstration
*(Watch the dynamic cost allocation and risk heatmapping in action below)*

![Dashboard Demonstration](assets/dashboard_gif.gif)

📄 **[Click here to view or download the high-resolution PDF export](assets/dashboard_Export.pdf)**

---

## System Architecture & Workflow

The engine executes an automated, four-stage data architecture to convert raw thermodynamic properties into real-world maritime arbitrage signals:

[1. Market Ingestion] ---> [2. DWSIM Digital Twin] ---> [3. SciPy LP Engine] ---> [4. Power BI Dashboard]\
  Live WTI/RBOB Data &nbsp; &nbsp; &nbsp; &nbsp; Thermodynamic States &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Non-Linear Blending &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;CIF Margin Heatmaps\
  via yfinance (Daily) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; (RVP / RON Extraction) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; & Cosine RVP Waves &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; DAX Volatility Models

1. Market Ingestion (price_fetcher.py): Programmatically extracts continuous daily historical commodity data for WTI Crude (CL=F) and RBOB Gasoline (RB=F) via the Yahoo Finance API, cleanly handling weekend exchange gaps using a forward-fill algorithm.
2. Headless Process Simulation: Automates a DWSIM refinery flowsheet in the background via a Python interface. The engine applies Peng-Robinson thermodynamics and Petroleum Assay Characterization to dynamically compute physical properties (RVP and RON) for intermediate streams.
3. Mathematical Blending Optimization: Evaluates feedstock component costs and solves a daily operational blending grid to minimize the manufacturing cost of USGC Regular 87 gasoline while satisfying non-linear physical constraints.
4. Commercial Visualization Layer: Feeds a robust multi-year daily dataset into Power BI, tracking localized global product netbacks, freight volatility, and structural arbitrage windows.

---

## Engineering & Mathematical Core

### 1. Non-Linear Property Linearization
Vapor pressure does not blend linearly by volume fraction. To solve this inside a deterministic Linear Program without stalling execution speeds, the engine converts raw Reid Vapor Pressure (RVP) into a linear blending index using an industry-standard power law:

$$
RVP_{index} = RVP^{1.25}
$$

### 2. Continuous Seasonal Regulatory Modeling
Instead of relying on rigid calendar-month step changes that cause numerical discontinuities at year-end boundaries, the optimization engine models the EPA's shifting environmental regulations using a continuous, periodic cosine wave driven by the calendar day of the year (t):

$$
RVP_{max}(t) = 10.8 + 3.0 * cos(\frac{2\pi t}{365})
$$

* Summer Mode (t ≈ 182): Tightens the cap to a strict 7.8 psi, forcing the optimizer to systematically dump high-vapor-pressure Butane and favor expensive Alkylate.
* Winter Mode (t ≈ 0): Relaxes the cap to 13.8 psi, allowing the refinery to aggressively blend cheap, highly profitable Butane.

---

## Repository Structure

├── Blending_Model.dwxmz        # DWSIM Core process flowsheet and assay model\
├── price_fetcher.py            # Standalone automation script for daily historical data ingestion\
├── power_bi_optimizer.py       # Core loop script embedded within Power BI (DWSIM + SciPy LP)\
├── live_prices.csv             # Continuous daily market cache bypassing BI sandboxing\
└── README.md                   # Project documentation

---

## Installation & Setup

### Prerequisites
* Python 3.10+
* DWSIM (installed locally with automation path exported)
* Power BI Desktop

### Dependencies
Install the required quantitative and interface packages:
```bash
pip install pandas numpy scipy yfinance pythonnet# Refinery Supply Chain & Maritime Logistics Dashboard
```
An economic decision-support dashboard designed to track downstream refinery logistics and market economics. This project automates the extraction of market spot prices and logistics data via Python, models refinery gross margins using DAX, and visualizes dynamic route-profitability metrics across global destination markets.

---

## Running the Engine
1. Execute the daily market data extraction script to build your local pricing cache:
```bash
python price_fetcher.py
```
2. Verify that live_prices.csv has successfully generated daily time-series rows.
3. Open Power BI and ensure the directory paths inside the Python Script data source point to your local .dwxmz` and .csv files.
4. Click Refresh to run the complete simulation, optimization, and financial model back-test.

---

## Commercail Insights Identified

* **The "Spring Squeeze" Phenomenon:** The model perfectly captures historical margin compressions in March/April. During these windows, macroeconomic crude spikes (such as the 2026 Strait of Hormuz crisis) frequently collide with the structural transition to low-RVP summer fuel, driving optimized blend costs vertically.
* **Structural Global Arbitrage Dynamics:** Back-testing reveals highly realistic geographical market realities. Santos, Brazil acts as a structural high-margin import sink due to local refining deficits and low freight layout from the USGC, while Singapore acts as a highly consolidated regional refining hub where the USGC export window opens only during severe localized supply shocks.
* **Advanced DAX:** Authored complex measures utilizing time-intelligence and statistical iterators (`STDEVX.S`) to model localized refinery margins, crack spreads, and directional risk.
* **Logistics Integration:** Paired Free-on-Board (FOB) refinery costs with variable freight burdens to output Cost, Insurance, and Freight (CIF) metrics.
