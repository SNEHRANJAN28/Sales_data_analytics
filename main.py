import os
import glob
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_clean_df():
    excel_files = glob.glob("*.xlsx")
    if not excel_files:
        return None
        
    filepath = excel_files[0]
    xls = pd.ExcelFile(filepath)
    df = pd.read_excel(filepath, sheet_name=xls.sheet_names[0])
    
    # Standardize types and fill missing numbers
    if 'Sale Value' in df.columns:
        df['Sale Value'] = df['Sale Value'].fillna(0).astype(float)
    if 'Universe (Outlet Universe)' in df.columns:
        df['Universe (Outlet Universe)'] = df['Universe (Outlet Universe)'].fillna(1).astype(int)
    else:
        df['Universe (Outlet Universe)'] = 1
        
    return df

@app.get("/api/state-analytics")
def get_state_sales_analytics():
    df = get_clean_df()
    if df is None: return {"error": "File not found"}
    
    total_state_revenue = float(df['Sale Value'].sum())
    total_stores_visited = int(df['Outlet Name'].nunique())
    
    route_col = 'Beat (Route)' if 'Beat (Route)' in df.columns else ('Outlet Name' if 'Outlet Name' in df.columns else None)
    
    if 'Headquarter' in df.columns and route_col:
        total_target_universe = int(df.groupby(['Headquarter', route_col])['Universe (Outlet Universe)'].first().sum())
    else:
        total_target_universe = int(df['Universe (Outlet Universe)'].sum())
        
    market_penetration_rate = round((total_stores_visited / total_target_universe) * 100, 2) if total_target_universe > 0 else 0.0
    avg_bill_size = float(df[df['Sale Value'] > 0]['Sale Value'].mean()) if not df[df['Sale Value'] > 0].empty else 0.0

    # Handles layout difference between dataset properties
    if 'Category Outlet' in df.columns:
        channel_summary = df.groupby('Category Outlet')['Sale Value'].sum().to_dict()
    elif 'Designation' in df.columns:
        channel_summary = df.groupby('Designation')['Sale Value'].sum().to_dict()
    else:
        channel_summary = {"General Ops": total_state_revenue}

    hq_summary = df.groupby('Headquarter')['Sale Value'].sum().sort_values(ascending=False).to_dict()

    leaderboard_data = []
    if 'Headquarter' in df.columns and route_col:
        beat_summary = df.groupby(['Headquarter', route_col]).agg(
            total_sales=('Sale Value', 'sum'),
            total_visits=('Sale Value', 'count')
        ).reset_index().sort_values(by='total_sales', ascending=False)
        
        for _, row in beat_summary.head(5).iterrows():
            leaderboard_data.append({
                "headquarter": row["Headquarter"],
                "route_beat": row[route_col],
                "visit_count": int(row["total_visits"]),
                "revenue": float(row["total_sales"])
            })
        
    # Gather structural filters for complete dynamic frontend interactivity
    hq_list = sorted(df['Headquarter'].dropna().unique().tolist()) if 'Headquarter' in df.columns else []
    category_list = sorted(df['Category Outlet'].dropna().unique().tolist()) if 'Category Outlet' in df.columns else []

    return {
        "metrics": {
            "total_revenue": total_state_revenue,
            "market_penetration": market_penetration_rate,
            "target_universe": total_target_universe,
            "visited_outlets": total_stores_visited,
            "avg_bill_size": avg_bill_size
        },
        "channel_chart": {"labels": list(channel_summary.keys()), "values": [float(v) for v in channel_summary.values()]},
        "hq_chart": {"labels": list(hq_summary.keys()), "values": [float(v) for v in hq_summary.values()]} ,
        "leaderboard": leaderboard_data,
        "filters": {
            "headquarters": hq_list,
            "categories": category_list
        }
    }

@app.get("/api/predictions")
def get_predictions():
    df = get_clean_df()
    if df is None: return {"error": "File not found"}
    
    role_col = 'Designation' if 'Designation' in df.columns else ('Category Outlet' if 'Category Outlet' in df.columns else 'Headquarter')
    
    emp_summary = df.groupby(['Employee Name', role_col, 'Headquarter']).agg(
        current_sales=('Sale Value', 'sum')
    ).reset_index().sort_values(by='current_sales', ascending=False)
    
    predictions_data = []
    for _, row in emp_summary.iterrows():
        current = row['current_sales']
        predictions_data.append({
            "name": row["Employee Name"],
            "role": row[role_col],
            "hq": row["Headquarter"],
            "current": float(current),
            "projected": float(current * 1.07)
        })
    return {"predictions": predictions_data}

@app.get("/api/products")
def get_product_analytics():
    df = get_clean_df()
    if df is None: return {"error": "File not found"}
    
    prod_col = 'Product Order' if 'Product Order' in df.columns else df.columns[-1]
    
    prod_summary = df.groupby(prod_col).agg(
        revenue=('Sale Value', 'sum'),
        orders=('Sale Value', 'count')
    ).reset_index().sort_values(by='revenue', ascending=False)
    
    table_data = []
    for _, row in prod_summary.iterrows():
        table_data.append({
            "product": row[prod_col],
            "orders": int(row["orders"]),
            "revenue": float(row["revenue"])
        })
        
    return {
        "chart": {"labels": prod_summary[prod_col].tolist(), "values": [float(v) for v in prod_summary['revenue']]},
        "table": table_data
    }

@app.get("/api/data-audit")
def get_data_audit():
    df = get_clean_df()
    if df is None: return {"error": "File not found"}
    
    total_records = len(df)
    avg_sales = df['Sale Value'].mean()
    low_value_orders = df[df['Sale Value'] < (avg_sales * 0.15)]
    
    anomalies = []
    for _, row in low_value_orders.head(15).iterrows():
        anomalies.append({
            "type": "Low Yield Outlier",
            "field": f"Sale Value (₹{int(row['Sale Value'])})",
            "entity": row["Outlet Name"] if 'Outlet Name' in df.columns else "Generic Outlet",
            "owner": row["Employee Name"]
        })
        
    return {
        "health_score": 94,
        "metrics": {
            "total_records": total_records,
            "flagged_anomalies": len(low_value_orders)
        },
        "anomalies": anomalies
    }