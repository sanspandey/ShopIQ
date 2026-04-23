import pandas as pd
import numpy as np
import re
from datetime import datetime


class DataProcessor:
    """
    Loads any Excel/CSV, auto-detects column roles,
    cleans the data, and computes KPIs.
    """

    # ── Keyword lists for auto-detection ──────────────────────────────────────
    DATE_KEYWORDS     = ["date","time","day","month","year","period","when","dt","created","ordered","sold","invoice"]
    REVENUE_KEYWORDS  = ["revenue","sales","sale","amount","total","income","turnover",
                         "price","value","gmv","net","gross","payment","receipt","earning","profit","cost"]
    QTY_KEYWORDS      = ["qty","quantity","units","count","sold","items","pieces","volume","no","number"]
    PRODUCT_KEYWORDS  = ["product","item","name","sku","description","goods","article","model","title"]
    CATEGORY_KEYWORDS = ["category","cat","type","segment","group","department","section","class","genre"]
    REGION_KEYWORDS   = ["region","city","state","location","area","zone","store","branch","market","territory"]

    # ── Load ──────────────────────────────────────────────────────────────────
    def load_file(self, uploaded_file):
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            # Try UTF-8 first then latin-1
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8")
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="latin-1")
        else:
            df = pd.read_excel(uploaded_file)
        return df

    # ── Auto-detect + clean ───────────────────────────────────────────────────
    def auto_detect_and_clean(self, df: pd.DataFrame):
        df = df.copy()

        # 1. Strip whitespace from column names
        df.columns = [str(c).strip() for c in df.columns]

        # 2. Drop fully empty rows/columns
        df.dropna(how="all", inplace=True)
        df.dropna(axis=1, how="all", inplace=True)
        df.reset_index(drop=True, inplace=True)

        # 3. Detect column roles
        detected = self._detect_columns(df)

        # 4. Parse date column
        if detected.get("date_col"):
            df[detected["date_col"]] = pd.to_datetime(
                df[detected["date_col"]], errors="coerce"
            )
            df.dropna(subset=[detected["date_col"]], inplace=True)
            df.sort_values(detected["date_col"], inplace=True)
            df.reset_index(drop=True, inplace=True)

        # 5. Clean revenue column
        if detected.get("revenue_col"):
            df[detected["revenue_col"]] = (
                df[detected["revenue_col"]]
                .astype(str)
                .str.replace(r"[₹$£€,\s]", "", regex=True)
                .str.replace(r"[^\d.\-]", "", regex=True)
            )
            df[detected["revenue_col"]] = pd.to_numeric(df[detected["revenue_col"]], errors="coerce")
            df[detected["revenue_col"]] = df[detected["revenue_col"]].fillna(df[detected["revenue_col"]].median())
            # Remove clear outliers (>5×IQR above Q3)
            q3  = df[detected["revenue_col"]].quantile(0.75)
            iqr = df[detected["revenue_col"]].quantile(0.75) - df[detected["revenue_col"]].quantile(0.25)
            df = df[df[detected["revenue_col"]] <= q3 + 5 * iqr]

        # 6. Clean quantity column
        if detected.get("qty_col"):
            df[detected["qty_col"]] = pd.to_numeric(df[detected["qty_col"]], errors="coerce").fillna(0)

        # 7. Drop duplicates
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)

        # 8. Add helper columns
        if detected.get("date_col"):
            dc = detected["date_col"]
            df["_month"]   = df[dc].dt.to_period("M").astype(str)
            df["_week"]    = df[dc].dt.isocalendar().week.astype(int)
            df["_dow"]     = df[dc].dt.day_name()
            df["_year"]    = df[dc].dt.year
            df["_monthno"] = df[dc].dt.month

        # 9. Build meta
        meta = self._build_meta(df, detected)

        return df, meta

    # ── Column detection ──────────────────────────────────────────────────────
    def _score(self, col_name, keywords):
        col_lower = col_name.lower()
        return sum(k in col_lower for k in keywords)

    def _detect_columns(self, df):
        detected = {}
        candidates = {
            "date_col":     (self.DATE_KEYWORDS,     ["datetime64", "object"]),
            "revenue_col":  (self.REVENUE_KEYWORDS,  ["float64", "int64", "object"]),
            "qty_col":      (self.QTY_KEYWORDS,      ["float64", "int64"]),
            "product_col":  (self.PRODUCT_KEYWORDS,  ["object"]),
            "category_col": (self.CATEGORY_KEYWORDS, ["object"]),
            "region_col":   (self.REGION_KEYWORDS,   ["object"]),
        }

        for role, (keywords, _) in candidates.items():
            best_col, best_score = None, 0
            for col in df.columns:
                if col.startswith("_"):
                    continue
                s = self._score(col, keywords)
                if s > best_score:
                    best_score, best_col = s, col
            if best_col and best_score > 0:
                # Avoid assigning the same column to two roles
                if best_col not in detected.values():
                    detected[role] = best_col

        # Fallback: try to find a datetime column by dtype
        if "date_col" not in detected:
            for col in df.columns:
                if "datetime" in str(df[col].dtype):
                    detected["date_col"] = col
                    break

        # Fallback: try to find a numeric column for revenue
        if "revenue_col" not in detected:
            for col in df.columns:
                if df[col].dtype in [np.float64, np.int64] and col not in detected.values():
                    detected["revenue_col"] = col
                    break

        return detected

    # ── Meta builder ──────────────────────────────────────────────────────────
    def _build_meta(self, df, detected):
        meta = {**detected}

        # Human-readable detected col names
        meta["detected_cols"] = {k: v for k, v in detected.items() if v}

        # Date range
        if detected.get("date_col"):
            mn = df[detected["date_col"]].min()
            mx = df[detected["date_col"]].max()
            meta["date_range"] = f"{mn.strftime('%b %Y')} – {mx.strftime('%b %Y')}"
            meta["n_months"] = max(1, (mx.year - mn.year) * 12 + mx.month - mn.month + 1)
        else:
            meta["date_range"] = "Unknown period"
            meta["n_months"] = 1

        return meta

    # ── KPIs ─────────────────────────────────────────────────────────────────
    def compute_kpis(self, df, meta):
        stats = {}
        rc = meta.get("revenue_col")
        pc = meta.get("product_col")

        # Total revenue
        if rc:
            total = df[rc].sum()
            stats["total_revenue"] = self._fmt_currency(total)
            stats["total_revenue_raw"] = total

            # Month-over-month delta (last two full months)
            if "_month" in df.columns:
                monthly = df.groupby("_month")[rc].sum().sort_index()
                if len(monthly) >= 2:
                    prev, curr = monthly.iloc[-2], monthly.iloc[-1]
                    pct = ((curr - prev) / prev * 100) if prev else 0
                    stats["revenue_delta"] = f"{'▲' if pct >= 0 else '▼'} {abs(pct):.1f}% vs prev month"
                    stats["revenue_dir"]   = "up" if pct >= 0 else "down"
        else:
            stats["total_revenue"] = "—"

        # Total orders
        stats["total_orders"] = f"{len(df):,}"

        # Avg order value
        if rc:
            avg = df[rc].mean()
            stats["avg_order"]     = self._fmt_currency(avg)
            stats["avg_order_raw"] = avg

            # Delta
            if "_month" in df.columns:
                monthly_avg = df.groupby("_month")[rc].mean().sort_index()
                if len(monthly_avg) >= 2:
                    prev, curr = monthly_avg.iloc[-2], monthly_avg.iloc[-1]
                    pct = ((curr - prev) / prev * 100) if prev else 0
                    stats["avg_delta"] = f"{'▲' if pct >= 0 else '▼'} {abs(pct):.1f}% vs prev month"
                    stats["avg_dir"]   = "up" if pct >= 0 else "down"
        else:
            stats["avg_order"] = "—"

        # Best product
        if pc and rc:
            top = df.groupby(pc)[rc].sum().idxmax()
            stats["top_product"] = str(top)[:22] + ("…" if len(str(top)) > 22 else "")
        elif pc:
            top = df[pc].value_counts().idxmax()
            stats["top_product"] = str(top)[:22]
        else:
            stats["top_product"] = "—"

        return stats

    def _fmt_currency(self, val):
        if val >= 1_00_00_000:
            return f"₹{val/1_00_00_000:.1f}Cr"
        elif val >= 1_00_000:
            return f"₹{val/1_00_000:.1f}L"
        elif val >= 1_000:
            return f"₹{val/1_000:.1f}K"
        else:
            return f"₹{val:,.0f}"
