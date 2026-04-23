import json
import re
import numpy as np
import pandas as pd
import requests


class AIAnalyzer:
    """
    Sends a rich business data snapshot to Groq (llama-3.3-70b-versatile)
    and gets back structured plain-English insights + supports multi-turn chat.
    """

    API_URL  = "https://api.groq.com/openai/v1/chat/completions"
    MODEL    = "llama-3.3-70b-versatile"
    API_KEY  = GROQ_API_KEY

    SYSTEM_PROMPT = (
        "You are ShopIQ, an expert AI business analyst for small shop owners in India. "
        "You have deep knowledge of Indian retail, seasonal trends, and regional markets. "
        "You speak plainly and practically — like a trusted advisor, not a consultant. "
        "Always use ₹ for currency. Be specific with numbers from the data provided."
    )

    # ── Public API ────────────────────────────────────────────────────────────
    def generate_insights(self, df, meta, stats, forecast_df=None):
        """
        Build a data snapshot and ask Groq to return structured JSON with:
          summary, alerts, positives, recommendations, forecast_note
        """
        snapshot = self._build_snapshot(df, meta, stats, forecast_df)
        prompt   = self._build_analysis_prompt(snapshot)

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ]

        try:
            raw = self._call_api(messages)
            return self._parse_response(raw)
        except Exception as e:
            return {
                "summary": f"AI analysis could not be completed: {e}. "
                           f"Please check your Groq API key.",
                "alerts": [],
                "positives": [],
                "recommendations": ["Ensure your Groq API key is valid to enable AI insights."],
                "forecast_note": None,
            }

    def chat(self, user_message: str, df, meta, stats, history: list = None):
        """
        Multi-turn chat — answer a follow-up question about the sales data.
        history: list of {"role": "user"/"assistant", "content": "..."} dicts
        Returns: (reply_text, updated_history)
        """
        snapshot = self._build_snapshot(df, meta, stats)
        system   = (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"SALES DATA CONTEXT:\n{json.dumps(snapshot, indent=2, default=str)}"
        )

        messages = [{"role": "system", "content": system}]
        if history:
            messages.extend(history[-10:])  # keep last 10 turns
        messages.append({"role": "user", "content": user_message})

        try:
            reply = self._call_api(messages, max_tokens=512)
            updated_history = (history or []) + [
                {"role": "user",      "content": user_message},
                {"role": "assistant", "content": reply},
            ]
            return reply, updated_history
        except Exception as e:
            err = f"Sorry, I could not process that: {e}"
            return err, history or []

    # ── Snapshot Builder ──────────────────────────────────────────────────────
    def _build_snapshot(self, df, meta, stats, forecast_df=None):
        snap = {}
        rc = meta.get("revenue_col")
        pc = meta.get("product_col")
        cc = meta.get("category_col")

        snap["date_range"]    = meta.get("date_range", "Unknown")
        snap["total_records"] = len(df)
        snap["total_revenue"] = round(stats.get("total_revenue_raw", 0), 2)
        snap["avg_order"]     = round(stats.get("avg_order_raw", 0), 2)
        snap["total_orders"]  = len(df)

        # Monthly trend + growth
        if rc and "_month" in df.columns:
            monthly = df.groupby("_month")[rc].sum().sort_index()
            snap["monthly_revenue"] = {k: round(v, 2) for k, v in monthly.to_dict().items()}
            snap["best_month"]  = str(monthly.idxmax())
            snap["worst_month"] = str(monthly.idxmin())
            vals = monthly.values
            if len(vals) >= 2:
                growth = [(vals[i] - vals[i-1]) / vals[i-1] * 100
                          for i in range(1, len(vals)) if vals[i-1] != 0]
                if growth:
                    snap["mom_growth_pct"]  = [round(g, 1) for g in growth]
                    snap["avg_growth_pct"]  = round(float(np.mean(growth)), 1)
                    snap["last_mom_growth"] = round(growth[-1], 1)

        # Top & bottom products
        if rc and pc:
            by_prod = df.groupby(pc)[rc].sum()
            snap["top_5_products"]    = by_prod.nlargest(5).round(2).to_dict()
            snap["bottom_3_products"] = by_prod.nsmallest(3).round(2).to_dict()
            snap["total_products"]    = len(by_prod)

        # Category breakdown
        if rc and cc:
            by_cat = df.groupby(cc)[rc].sum().nlargest(6)
            snap["categories"] = by_cat.round(2).to_dict()

        # Day of week
        if rc and "_dow" in df.columns:
            dow = df.groupby("_dow")[rc].sum()
            snap["best_day_of_week"]  = str(dow.idxmax())
            snap["worst_day_of_week"] = str(dow.idxmin())
            snap["dow_revenue"]       = {k: round(v, 2) for k, v in dow.to_dict().items()}

        # Quarterly
        if rc and "_quarter" in df.columns:
            snap["quarterly_revenue"] = {
                k: round(v, 2)
                for k, v in df.groupby("_quarter")[rc].sum().to_dict().items()
            }

        # Forecast
        if forecast_df is not None and not forecast_df.empty:
            snap["forecast"] = forecast_df.to_dict(orient="records")

        return snap

    # ── Prompt Builder ────────────────────────────────────────────────────────
    def _build_analysis_prompt(self, snap):
        return f"""Analyse this sales data and respond ONLY with a valid JSON object (no markdown fences, no extra text):

DATA SNAPSHOT:
{json.dumps(snap, indent=2, default=str)}

Return ONLY this JSON structure:
{{
  "summary": "3-4 sentences covering overall performance with specific numbers. Written for a non-technical shop owner in plain English.",
  "alerts": ["Up to 3 specific warnings about declining trends, weak months, or risks — each under 80 words"],
  "positives": ["Up to 3 specific strengths with product names and numbers — each under 80 words"],
  "recommendations": ["3-4 very specific, actionable suggestions the owner can act on this week — reference actual product names and numbers from the data"],
  "forecast_note": "1-2 sentences interpreting the revenue forecast in plain language."
}}

Rules:
- Use ₹ for all currency amounts
- Reference actual product names, months, and numbers from the data
- alerts: highlight declining trends, weak months, risky patterns
- positives: highlight best products, peak days, growth streaks
- recommendations: must be practical (e.g. "Stock more of [Product X] before weekends")
- Keep each string under 120 words
"""

    # ── Groq API Call ─────────────────────────────────────────────────────────
    def _call_api(self, messages: list, max_tokens: int = 1024) -> str:
        response = requests.post(
            self.API_URL,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {self.API_KEY}",
            },
            json={
                "model":       self.MODEL,
                "messages":    messages,
                "max_tokens":  max_tokens,
                "temperature": 0.4,
                "stream":      False,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise ValueError(data["error"].get("message", str(data["error"])))

        return data["choices"][0]["message"]["content"]

    # ── Response Parser ───────────────────────────────────────────────────────
    def _parse_response(self, raw: str) -> dict:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()

        # Direct parse
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

        # Extract first {...} block
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Fallback
        return {
            "summary": clean[:500] if clean else "AI analysis unavailable.",
            "alerts": [],
            "positives": [],
            "recommendations": [],
            "forecast_note": None,
        }
