
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Project paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "analysis_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load results from the previous analysis
orders = pd.read_csv(
    OUTPUT_DIR / "delivery_performance_by_order.csv"
)
states = pd.read_csv(
    OUTPUT_DIR / "delivery_performance_by_state.csv"
)

# -------------------------------
# Chart 1: Overall delivery KPIs
# -------------------------------
total_orders = len(orders)
late_orders = (orders["delivery_delay_days"] > 0).sum()
late_rate = late_orders / total_orders * 100 if total_orders else 0
average_days = orders["actual_delivery_days"].mean()

fig, ax = plt.subplots(figsize=(8, 5))

labels = [
    "Orders analyzed",
    "Late orders",
    "Late delivery rate (%)",
    "Average delivery days",
]
values = [
    total_orders,
    late_orders,
    late_rate,
    average_days,
]

bars = ax.bar(labels, values)
ax.set_title("Olist Delivery Performance KPIs")
ax.set_ylabel("Value")
ax.tick_params(axis="x", labelrotation=15)

for bar, value in zip(bars, values):
    label = f"{value:,.2f}" if "%" in labels[bars.index(bar)] or "days" in labels[bars.index(bar)] else f"{value:,.0f}"
    ax.annotate(
        label,
        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
        ha="center",
        xytext=(0, 4),
        textcoords="offset points",
    )

fig.tight_layout()
fig.savefig(OUTPUT_DIR / "01_overall_delivery_kpis.png", dpi=200)
plt.close(fig)

# -----------------------------------
# Chart 2: Average delivery by state
# -----------------------------------
top_slow = states.nlargest(10, "average_delivery_days").sort_values(
    "average_delivery_days"
)

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(
    top_slow["customer_state"],
    top_slow["average_delivery_days"],
)
ax.set_title("10 States with Longest Average Delivery Time")
ax.set_xlabel("Average delivery time (days)")
ax.set_ylabel("Customer state")

for bar in bars:
    ax.annotate(
        f"{bar.get_width():.1f}",
        (bar.get_width(), bar.get_y() + bar.get_height() / 2),
        xytext=(4, 0),
        textcoords="offset points",
        va="center",
    )

fig.tight_layout()
fig.savefig(OUTPUT_DIR / "02_average_delivery_by_state.png", dpi=200)
plt.close(fig)

# -----------------------------------
# Chart 3: Late delivery percentage
# -----------------------------------
top_late = states.nlargest(10, "late_percentage").sort_values(
    "late_percentage"
)

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(
    top_late["customer_state"],
    top_late["late_percentage"],
)
ax.set_title("10 States with Highest Late-Delivery Percentage")
ax.set_xlabel("Late deliveries (%)")
ax.set_ylabel("Customer state")

for bar in bars:
    ax.annotate(
        f"{bar.get_width():.1f}%",
        (bar.get_width(), bar.get_y() + bar.get_height() / 2),
        xytext=(4, 0),
        textcoords="offset points",
        va="center",
    )

fig.tight_layout()
fig.savefig(OUTPUT_DIR / "03_late_delivery_by_state.png", dpi=200)
plt.close(fig)

print("Charts created successfully:")
for filename in [
    "01_overall_delivery_kpis.png",
    "02_average_delivery_by_state.png",
    "03_late_delivery_by_state.png",
]:
    print(OUTPUT_DIR / filename)
