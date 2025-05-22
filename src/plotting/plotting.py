import base64
import io
from matplotlib import pyplot as plt
from pypfopt import EfficientFrontier
from pypfopt.objective_functions import L2_reg
from pypfopt.plotting import plot_efficient_frontier
import pandas as pd
import numpy as np


def generate_charts(portfolio_data):
    """Generate portfolio visualization charts"""
    charts = {}

    # 1. Portfolio allocation pie chart
    if portfolio_data["allocation"]:
        plt.figure(figsize=(10, 8))
        labels = list(portfolio_data["allocation"].keys())
        sizes = list(portfolio_data["allocation"].values())

        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        plt.axis("equal")

        # Save to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png", bbox_inches="tight", dpi=300)
        img_buffer.seek(0)
        charts["allocation"] = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        plt.close()

    # 2. Performance metrics bar chart
    performance = portfolio_data["performance"]
    metrics = ["Expected Annual Return", "Annual Volatility"]
    values = [
        performance["expected_annual_return"] * 100,
        performance["annual_volatility"] * 100,
    ]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(metrics, values, color=["#2E86AB", "#A23B72"])
    plt.ylabel("Value")

    # Add value labels on bars
    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.1,
            f"{value:.2f}%" if bar.get_x() < 2 else f"{value:.2f}",
            ha="center",
            va="bottom",
        )

    plt.xticks(rotation=45)
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", bbox_inches="tight", dpi=300)
    img_buffer.seek(0)
    charts["performance"] = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
    plt.close()

    return charts


def generate_ef_plot(ef, performance):
    """Generate Efficient Frontier plot from stored session data with optional portfolio highlight"""

    # Generate plot
    fig, ax = plt.subplots(figsize=(10, 8))
    plot_efficient_frontier(ef, ax=ax, show_assets=True)

    ret_tangent = performance[0]
    std_tangent = performance[1]

    # Update legend
    ax.legend()

    plt.title("Efficient Frontier")
    plt.xlabel("Annual Volatility")
    plt.ylabel("Expected Annual Return")

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", bbox_inches="tight", dpi=300)
    img_buffer.seek(0)
    filename = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
    plt.close()

    return filename