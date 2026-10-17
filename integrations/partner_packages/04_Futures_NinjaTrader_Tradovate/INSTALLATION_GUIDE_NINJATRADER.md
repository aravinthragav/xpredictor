# NinjaTrader 8 & Tradovate Partner Integration Guide
### Institutional Reality Cone Indicator for Futures Prop Desks

This package is designed for CME/CBOT futures prop evaluation firms (e.g. **Topstep, Apex Trader Funding, Fast Track Trading**).

---

## 1. Package Files
- `XPredictorRealityCone.cs` — Native NinjaScript C# Custom Indicator Source Code

---

## 2. Installation into NinjaTrader 8 (2 Minutes)
1. Open **NinjaTrader 8**.
2. Click **Tools** $\to$ **New NinjaScript Editor** (or press `F5`).
3. In the NinjaScript Explorer panel on the right, right-click on **Indicators** $\to$ **New Indicator**.
4. Name the indicator `XPredictorRealityCone`.
5. Replace the template code with the contents of `XPredictorRealityCone.cs`.
6. Press `F5` (or click **Compile** in the top ribbon). The compilation chime will sound.
7. Open any futures chart (e.g., `NQ`, `ES`, `GC`, `CL`), press `Ctrl+I` to open Indicators, select **XPredictorRealityCone**, and click **Add**.

---

## 3. Trailing Threshold Drawdown Defense
- **Why Futures Prop Desks Use This**: On evaluations (like Topstep Combine or Apex PA accounts), traders frequently fail when their open equity trails back into the high-water threshold.
- The $-2.1\sigma$ Reality Cone boundary visually establishes where trailing drawdown risks escalate, encouraging traders to take profits near the $+2.1\sigma$ expansion bounds rather than holding through pullbacks.

---

## 4. Technical Support
- Developer Support: `arkankl07@gmail.com`
- Live Partner Sandbox: [https://aravinthragav.github.io/xpredictor/](https://aravinthragav.github.io/xpredictor/)
