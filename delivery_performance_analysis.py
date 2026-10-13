
from pathlib import Path
import pandas as pd

# Dataset folder
DATA_DIR = Path(__file__).parent / "datasets"

# Load the required datasets
orders = pd.read_csv(
    DATA_DIR / "olist_orders_dataset.csv",
    parse_dates=[
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
)

customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")

print("Orders loaded:", len(orders))
print("Customers loaded:", len(customers))

# Keep orders with actual delivery dates and estimated dates
delivered = orders.dropna(
    subset=[
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
).copy()

# Calculate actual delivery time and delivery delay
delivered["actual_delivery_days"] = (
    delivered["order_delivered_customer_date"]
    - delivered["order_purchase_timestamp"]
).dt.total_seconds() / 86400

delivered["delivery_delay_days"] = (
    delivered["order_delivered_customer_date"]
    - delivered["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

delivered["delivery_status"] = delivered["delivery_delay_days"].apply(
    lambda days: "Late" if days > 0 else "On time or early"
)

# 1. Overall delivery performance
total_delivered = len(delivered)
late_orders = (delivered["delivery_delay_days"] > 0).sum()
late_percentage = (
    late_orders / total_delivered * 100 if total_delivered else 0
)

print("\n--- Overall Delivery Performance ---")
print("Orders with delivery dates:", total_delivered)
print("Late orders:", late_orders)
print(f"Late delivery percentage: {late_percentage:.2f}%")
print(
    "Average actual delivery time:",
    f"{delivered['actual_delivery_days'].mean():.2f} days",
)
print(
    "Average days early/late:",
    f"{delivered['delivery_delay_days'].mean():.2f} days",
)

# 2. Delivery performance by customer state
delivery_by_state = delivered.merge(
    customers[["customer_id", "customer_state"]],
    on="customer_id",
    how="left",
)

state_summary = (
    delivery_by_state.groupby("customer_state")
    .agg(
        total_orders=("order_id", "count"),
        average_delivery_days=("actual_delivery_days", "mean"),
        average_delay_days=("delivery_delay_days", "mean"),
        late_orders=("delivery_delay_days", lambda x: (x > 0).sum()),
    )
    .reset_index()
)

state_summary["late_percentage"] = (
    state_summary["late_orders"] / state_summary["total_orders"] * 100
)

state_summary = state_summary.sort_values(
    "average_delivery_days", ascending=False
)

print("\n--- States with Longest Average Delivery Time ---")
print(state_summary.head(10).round(2).to_string(index=False))

# 3. Save results
output_dir = Path(__file__).parent / "analysis_outputs"
output_dir.mkdir(exist_ok=True)

delivered.to_csv(
    output_dir / "delivery_performance_by_order.csv", index=False
)
state_summary.to_csv(
    output_dir / "delivery_performance_by_state.csv", index=False
)

print(f"\nAnalysis complete. Results saved to: {output_dir}")
