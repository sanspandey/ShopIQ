# 📊 ShopIQ — AI Sales Analytics v2.0

> Upload any Excel/CSV sales file → get instant AI-powered dashboards, trend alerts, and revenue forecasts in plain English. Now with Groq AI chat assistant.

---

## 🚀 Two Ways to Use

### Option A — Web App (Recommended) ✅
Just open **`shopiq.html`** in any browser. No installation needed.
- Drag & drop your Excel or CSV file
- Everything runs locally in your browser
- AI insights powered by Groq (llama-3.3-70b)

### Option B — Python / Streamlit App
Run the original Streamlit version locally.

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
streamlit run app.py
```

---

## 📁 Files

| File | Description |
|---|---|
| **shopiq.html** | ✅ Complete web app — open in browser, no install needed |
| app.py | Original Streamlit UI |
| data_processor.py | Python data cleaning module |
| ai_analyzer.py | Python Claude API analyzer |
| visualizer.py | Python Plotly charts |
| generate_sample_data.py | Generate test Excel data |
| sample_sales_data.xlsx | Sample data to test with |
| requirements.txt | Python dependencies |

---

## ✨ Features (shopiq.html)

| Feature | Details |
|---|---|
| **Smart Data Cleaning** | 20+ date formats, currency symbols (₹$£€), duplicates, outliers, missing values |
| **Auto Column Detection** | Finds date, revenue, product, category columns by keyword matching |
| **Revenue Trend** | Line chart with 3-month moving average, scrollable |
| **Monthly Comparison** | Bar chart highlighting best month, scrollable |
| **Day-of-Week Analysis** | Which days drive most sales |
| **Quarterly Revenue** | Q1–Q4 breakdown bar chart |
| **Weekly Radar** | Revenue by day across last 6 months |
| **Top Products** | Horizontal bar + donut chart, click to drill down |
| **Product Explorer** | Select any product → see its monthly trend, DoW performance, vs all comparison |
| **Category Heatmap** | Month × category revenue grouped bars |
| **Revenue Forecast** | Linear trend + seasonal model, 1–6 months ahead with confidence bands |
| **Groq AI Analysis** | Auto-generated summary, alerts, positives, recommendations |
| **AI Chat Assistant** | Ask anything about your data in plain English (multi-turn) |
| **Download CSV** | Export full cleaned data as CSV with UTF-8 BOM |
| **Download Excel** | Export as .xlsx with summary sheet |
| **Dark / Light Mode** | Toggle in sidebar |
| **Fully Responsive** | Works on mobile, tablet, desktop |

---

## 🤖 AI Setup

The web app uses **Groq API** (already configured with API key).
- Model: `llama-3.3-70b-versatile`
- Ultra-fast inference (~1-2 seconds)
- Supports CORS from browser (no proxy needed)

For the Python app, set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

---

## 📋 Supported File Formats

ShopIQ auto-detects columns — your file can have **any column names**:

- **Date-like**: date, time, day, ordered, sold, invoice, timestamp…
- **Revenue-like**: sales, amount, total, price, revenue, income, mrp…
- **Quantity-like**: qty, quantity, units, count, pieces, nos…
- **Product-like**: product, item, name, sku, description…
- **Category-like**: category, type, segment, group, department…

---

## 💡 Tips

1. At least **one date column** and **one numeric sales column** required
2. More months = better forecasts (3+ months recommended)
3. Include a product/item column for product-level insights
4. Currency symbols (₹, $, £) are handled automatically
5. Click any bar or pie slice to drill into that product's trend

---

*Built with ❤️ for small shop owners across India 🇮🇳*
