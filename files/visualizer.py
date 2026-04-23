import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ─── Shared theme ─────────────────────────────────────────────────────────────
DARK_BG   = "#0a0d14"
CARD_BG   = "#141927"
GRID_CLR  = "#1e2535"
TEXT_CLR  = "#e8e8f0"
MUTED_CLR = "#6b7494"
COLORS    = ["#60a5fa", "#a78bfa", "#34d399", "#f59e0b", "#f87171",
             "#38bdf8", "#818cf8", "#4ade80", "#fbbf24", "#fb7185"]

LAYOUT_BASE = dict(
    paper_bgcolor=CARD_BG,
    plot_bgcolor=CARD_BG,
    font=dict(family="DM Sans", color=TEXT_CLR),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR, tickfont=dict(color=MUTED_CLR)),
    yaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR, tickfont=dict(color=MUTED_CLR)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED_CLR)),
)


class Visualizer:

    # ── Revenue trend line ──────────────────────────────────────────────────
    def revenue_trend(self, df, meta):
        rc = meta.get("revenue_col")
        if not rc or "_month" not in df.columns:
            return self._empty_fig("No date or revenue column detected")

        monthly = df.groupby("_month")[rc].sum().reset_index()
        monthly.columns = ["Month", "Revenue"]
        monthly["MA3"] = monthly["Revenue"].rolling(3, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Revenue"],
            mode="lines+markers",
            name="Revenue",
            line=dict(color="#60a5fa", width=2.5),
            marker=dict(size=6, color="#60a5fa"),
            fill="tozeroy",
            fillcolor="rgba(96,165,250,0.08)",
        ))
        fig.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["MA3"],
            mode="lines", name="3-Month Avg",
            line=dict(color="#a78bfa", width=1.5, dash="dot"),
        ))
        fig.update_layout(**LAYOUT_BASE, title=dict(text="", font=dict(size=14)))
        return fig

    # ── Monthly bar ─────────────────────────────────────────────────────────
    def monthly_bar(self, df, meta):
        rc = meta.get("revenue_col")
        if not rc or "_month" not in df.columns:
            return self._empty_fig("No date/revenue data")

        monthly = df.groupby("_month")[rc].sum().reset_index()
        monthly.columns = ["Month", "Revenue"]
        max_rev = monthly["Revenue"].max()
        monthly["color"] = monthly["Revenue"].apply(
            lambda v: "#34d399" if v == max_rev else "#60a5fa"
        )

        fig = go.Figure(go.Bar(
            x=monthly["Month"], y=monthly["Revenue"],
            marker_color=monthly["color"],
            marker_line_width=0,
        ))
        fig.update_layout(**LAYOUT_BASE, bargap=0.3)
        return fig

    # ── Day of week ─────────────────────────────────────────────────────────
    def day_of_week(self, df, meta):
        rc = meta.get("revenue_col")
        if not rc or "_dow" not in df.columns:
            return self._empty_fig("No date data")

        order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = df.groupby("_dow")[rc].sum().reindex(order).fillna(0).reset_index()
        dow.columns = ["Day", "Revenue"]

        fig = go.Figure(go.Bar(
            x=dow["Day"], y=dow["Revenue"],
            marker=dict(
                color=dow["Revenue"],
                colorscale=[[0,"#1e2535"],[0.5,"#3b82f6"],[1,"#60a5fa"]],
                showscale=False,
            ),
            marker_line_width=0,
        ))
        fig.update_layout(**LAYOUT_BASE, bargap=0.25)
        return fig

    # ── Top products bar ─────────────────────────────────────────────────────
    def top_products(self, df, meta, top_n=10):
        rc = meta.get("revenue_col")
        pc = meta.get("product_col")
        if not rc or not pc:
            return None

        prod = df.groupby(pc)[rc].sum().nlargest(top_n).reset_index()
        prod.columns = ["Product", "Revenue"]
        prod = prod.sort_values("Revenue")

        fig = go.Figure(go.Bar(
            x=prod["Revenue"], y=prod["Product"],
            orientation="h",
            marker=dict(
                color=prod["Revenue"],
                colorscale=[[0,"#1e2535"],[0.5,"#6366f1"],[1,"#a78bfa"]],
                showscale=False,
            ),
            marker_line_width=0,
        ))
        fig.update_layout(**LAYOUT_BASE, bargap=0.25,
                          xaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=MUTED_CLR)),
                          yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=TEXT_CLR, size=11)))
        return fig

    # ── Product pie ──────────────────────────────────────────────────────────
    def product_pie(self, df, meta, top_n=7):
        rc = meta.get("revenue_col")
        pc = meta.get("product_col")
        if not rc or not pc:
            return None

        prod = df.groupby(pc)[rc].sum().nlargest(top_n).reset_index()
        prod.columns = ["Product", "Revenue"]

        fig = go.Figure(go.Pie(
            labels=prod["Product"],
            values=prod["Revenue"],
            hole=0.55,
            marker=dict(colors=COLORS[:len(prod)], line=dict(color=DARK_BG, width=2)),
            textfont=dict(color=TEXT_CLR),
        ))
        fig.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            font=dict(family="DM Sans", color=TEXT_CLR),
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED_CLR)),
        )
        return fig

    # ── Category heatmap ─────────────────────────────────────────────────────
    def category_heatmap(self, df, meta):
        rc  = meta.get("revenue_col")
        cat = meta.get("category_col")
        if not rc or not cat or "_month" not in df.columns:
            return None

        pivot = df.pivot_table(values=rc, index=cat, columns="_month", aggfunc="sum").fillna(0)
        if pivot.empty:
            return None

        fig = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0,"#0f1320"],[0.5,"#3b82f6"],[1,"#34d399"]],
            showscale=True,
            hovertemplate="Month: %{x}<br>Category: %{y}<br>Revenue: ₹%{z:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            font=dict(family="DM Sans", color=TEXT_CLR),
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(tickfont=dict(color=MUTED_CLR)),
            yaxis=dict(tickfont=dict(color=TEXT_CLR)),
        )
        return fig

    # ── Revenue forecast ─────────────────────────────────────────────────────
    def revenue_forecast(self, df, meta, periods=3):
        rc = meta.get("revenue_col")
        if not rc or "_month" not in df.columns:
            return self._empty_fig("No date/revenue data for forecast"), None

        monthly = df.groupby("_month")[rc].sum().reset_index()
        monthly.columns = ["Month", "Revenue"]

        if len(monthly) < 3:
            return self._empty_fig("Need at least 3 months of data to forecast"), None

        # Simple linear trend + seasonal adjustment
        y = monthly["Revenue"].values.astype(float)
        x = np.arange(len(y))
        coeffs = np.polyfit(x, y, 1)  # linear fit
        trend  = np.poly1d(coeffs)

        # Residuals → season pattern (cycle over available months)
        residuals = y - trend(x)

        # Forecast
        future_x   = np.arange(len(y), len(y) + periods)
        fc_trend   = trend(future_x)

        # Season indices (cycle)
        season = residuals[-min(12, len(residuals)):]
        fc_season = np.array([season[i % len(season)] for i in range(periods)])
        fc_vals   = fc_trend + fc_season

        # Confidence interval (std of residuals)
        std = residuals.std()
        fc_upper = fc_vals + 1.5 * std
        fc_lower = fc_vals - 1.5 * std

        # Generate future month labels
        last_period = pd.Period(monthly["Month"].iloc[-1], freq="M")
        future_months = [(last_period + i + 1).strftime("%Y-%m") for i in range(periods)]

        fig = go.Figure()

        # Historical
        fig.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Revenue"],
            mode="lines+markers", name="Historical",
            line=dict(color="#60a5fa", width=2.5),
            marker=dict(size=5, color="#60a5fa"),
        ))

        # Confidence band
        fig.add_trace(go.Scatter(
            x=future_months + future_months[::-1],
            y=list(fc_upper) + list(fc_lower[::-1]),
            fill="toself",
            fillcolor="rgba(167,139,250,0.12)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Confidence range",
            showlegend=True,
        ))

        # Forecast line
        # Connect historical last point to first forecast
        bridge_x = [monthly["Month"].iloc[-1]] + future_months
        bridge_y = [monthly["Revenue"].iloc[-1]] + list(fc_vals)
        fig.add_trace(go.Scatter(
            x=bridge_x, y=bridge_y,
            mode="lines+markers", name="Forecast",
            line=dict(color="#a78bfa", width=2.5, dash="dot"),
            marker=dict(size=7, color="#a78bfa", symbol="diamond"),
        ))

        # Vertical divider
        fig.add_vline(x=monthly["Month"].iloc[-1], line_dash="dash",
                      line_color=MUTED_CLR, line_width=1, opacity=0.5)

        fig.update_layout(**LAYOUT_BASE)

        # Forecast dataframe
        fc_df = pd.DataFrame({
            "month":     future_months,
            "forecast":  fc_vals.round(2),
            "lower":     fc_lower.round(2),
            "upper":     fc_upper.round(2),
        })

        return fig, fc_df

    # ── Utility ──────────────────────────────────────────────────────────────
    def _empty_fig(self, msg="No data"):
        fig = go.Figure()
        fig.add_annotation(text=msg, x=0.5, y=0.5, showarrow=False,
                           font=dict(color=MUTED_CLR, size=14))
        fig.update_layout(**LAYOUT_BASE)
        return fig
