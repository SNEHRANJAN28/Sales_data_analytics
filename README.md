# Enterprise Sales Data Analytics & Revenue Intelligence System

An end-to-end data analytics and business intelligence project designed to transform raw transactional sales data into actionable strategic insights. This repository contains data pipelines, exploratory data analysis (EDA), machine learning models for customer segmentation and sales forecasting, and interactive dashboard designs.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Business Objectives](#business-objectives)
- [Repository Structure](#repository-structure)
- [Data Architecture & Schema](#data-architecture--schema)
- [Analytics & Machine Learning Workflow](#analytics--machine-learning-workflow)
- [Interactive BI Dashboard & KPIs](#interactive-bi-dashboard--kpis)
- [Key Insights & Strategic Recommendations](#key-insights--strategic-recommendations)
- [Tech Stack](#tech-stack)
- [Installation & Getting Started](#installation--getting-started)

---

## Project Overview

In multi-channel retail and e-commerce environments, unorganized transactional streams lead to revenue leakage, poor inventory allocation, and missed customer retention opportunities. 

This project establishes an automated analytics pipeline that integrates SQL data warehousing, Python-driven exploratory analysis, machine learning algorithms (RFM clustering and time-series forecasting), and dynamic Power BI reporting to optimize pricing strategies, track cohort retention, and predict demand trends.

---

## Business Objectives

1. **Build a Scalable Data Pipeline:** Construct a normalized relational Star Schema in SQL to query and aggregate millions of sales records efficiently.
2. **Execute Diagnostic Analysis:** Perform exploratory data analysis using Python (`Pandas`, `Seaborn`) to identify high-margin product lines, sales bottlenecks, and discount erosion.
3. **Implement Customer Segmentation:** Apply unsupervised K-Means clustering on Recency, Frequency, and Monetary (RFM) metrics to group customers by value.
4. **Deploy Predictive Revenue Forecasting:** Train time-series machine learning models (`Prophet`, `ARIMA`) to project quarterly sales and streamline inventory planning.
5. **Develop Executive Dashboards:** Build an interactive Power BI dashboard powered by DAX metrics for real-time performance tracking.

---

## Repository Structure

```text
├── data/
│   ├── raw/                 # Original transactional CSVs
│   └── processed/           # Cleaned datasets ready for analysis
├── sql/
│   ├── schema_design.sql    # DDL scripts for Star Schema tables
│   └── analytical_queries.sql # Window functions, aggregates, and CTEs
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_exploratory_data_analysis.ipynb
│   ├── 03_rfm_customer_segmentation.ipynb
│   └── 04_sales_forecasting.ipynb
├── dashboards/
│   └── sales_intelligence.pbix # Power BI dashboard file
├── assets/                  # Dashboard screenshots and diagrams
├── requirements.txt         # Required Python packages
└── README.md                # Project documentation

Data Architecture & Schema
Raw transactional data is processed through an ETL pipeline and structured into a Star Schema within a relational database (PostgreSQL / MS SQL Server):
+------------------+
       |   Dim_Customer   |
       +------------------+
                |
                |
+---------------+---------------+
|           Fact_Sales          | <--- +------------------+
+---------------+---------------+      |   Dim_Product    |
                |                      +------------------+
                |
       +------------------+
       |     Dim_Date     |
       +------------------+

Tables Overview:
Fact_Sales: Central table containing transaction metrics (Order_ID, Sales_Amount, Quantity, Discount, Profit_Margin, Shipping_Cost).
Dim_Customer: Demographic features, geographical locations, and acquisition details.
Dim_Product: Product hierarchy, category details, unit cost, and MSRP.
Dim_Date: Standard calendar attributes, fiscal quarters, holidays, and business days.
Analytics & Machine Learning Workflow
1. Data Cleaning & Transformation (Python)
Applied Interquartile Range (IQR) filtering to remove price and quantity anomalies.
Standardized datetime structures and imputed missing values using domain logic.
Conducted Pareto Analysis (80/20 rule) to isolate top-performing SKUs.
2. RFM Customer Segmentation (K-Means Clustering)
Customers are evaluated based on:
Recency (R): Days since last purchase.
Frequency (F): Total number of transactions.
Monetary (M): Total monetary spent.
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Preprocessing & Scaling
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_df[['Recency', 'Frequency', 'Monetary']])

# Clustering into 4 distinct groups
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
rfm_df['Cluster_ID'] = kmeans.fit_predict(rfm_scaled)
Identified Segments:
VIP / Champions: High frequency, high spend, recent activity.
Loyal Customers: Consistent purchase history and steady spending.
At-Risk: High historical spend, but inactive for over 180 days.
Low-Value / Churned: Low order frequency and low spend.

3. Revenue Forecasting (Prophet & ARIMA)
Predictive time-series modeling was implemented to forecast monthly revenue for upcoming quarters using trend decomposition and lag features:
from prophet import Prophet

# Fit Prophet Model
prophet_df = monthly_sales.rename(columns={'order_date': 'ds', 'total_revenue': 'y'})
model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
model.fit(prophet_df)

# Forecast Next 12 Months
future = model.make_future_dataframe(periods=12, freq='M')
forecast = model.predict(future)

Interactive BI Dashboard & KPIs
The executive dashboard tracks core metrics built with dynamic DAX Expressions:
Total Revenue & Gross Profit Margin ($)
Average Order Value (AOV)
Year-over-Year (YoY) Sales Growth (%)
Customer Lifetime Value (LTV)
Sample DAX Code:
YoY_Revenue_Growth = 
VAR CurrentYearSales = SUM(Fact_Sales[Sales_Amount])
VAR PriorYearSales = CALCULATE(
    SUM(Fact_Sales[Sales_Amount]), 
    SAMEPERIODLASTYEAR(Dim_Date[Date])
)
RETURN
DIVIDE(CurrentYearSales - PriorYearSales, PriorYearSales, 0)

Key Insights & Strategic Recommendations
Optimize Discounting: Discounts exceeding 25% eroded gross profit margins by 14% without producing proportional gains in volume.
Re-engage At-Risk Customers: Automated retention workflows aimed at high-value "At-Risk" segments prevent revenue churn.
Inventory Alignment: Time-series demand predictions enable proactive supply chain scheduling ahead of peak seasonal periods.
Tech Stack
Database & Querying: SQL, PostgreSQL, MS SQL Server
Languages & Libraries: Python (Pandas, NumPy, Scikit-learn, Prophet, Matplotlib, Seaborn)
Business Intelligence: Power BI, DAX, Power Query
Tools: Jupyter Notebook, Git, GitHub, VS Code
Installation & Getting Started
Clone the repository:
git clone [https://github.com/SNEHRANJAN28/Sales_data_analytics.git](https://github.com/SNEHRANJAN28/Sales_data_analytics.git)
cd Sales_data_analytics

Set up a virtual environment and install dependencies:
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt

Database Setup:
Execute scripts in sql/schema_design.sql within PostgreSQL/MS SQL Server.
Load clean CSV files into staging tables.
Run Notebooks:
Launch Jupyter Notebook to review the EDA, clustering, and forecasting workflows:
jupyter notebook
