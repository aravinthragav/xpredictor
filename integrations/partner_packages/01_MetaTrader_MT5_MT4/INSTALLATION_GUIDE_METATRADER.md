# MetaTrader 5 & MetaTrader 4 Partner Integration Guide
### Institutional Bayesian Reality Cone Indicator Package

This turnkey package enables prop firms and brokers to distribute the **XPredictor Reality Cone** indicator directly to client MetaTrader terminals.

---

## 1. Package Files
- `XPredictor_RealityCone.mq5` — Native MetaTrader 5 Source Code
- `XPredictor_RealityCone.mq4` — Native MetaTrader 4 Source Code

---

## 2. Installation for MetaTrader 5 (MT5)
1. Open **MetaTrader 5**.
2. Click **File** $\to$ **Open Data Folder**.
3. Navigate to `MQL5` $\to$ `Indicators`.
4. Copy `XPredictor_RealityCone.mq5` into this folder.
5. In MT5, press `Ctrl+N` to open the **Navigator** window, right-click **Indicators**, and select **Refresh**.
6. Drag `XPredictor_RealityCone` onto any **15M**, **1H**, or **4H** chart (e.g. `XAUUSD`, `EURUSD`, `US500`).

---

## 3. Installation for MetaTrader 4 (MT4)
1. Open **MetaTrader 4**.
2. Click **File** $\to$ **Open Data Folder**.
3. Navigate to `MQL4` $\to$ `Indicators`.
4. Copy `XPredictor_RealityCone.mq4` into this folder.
5. Right-click **Indicators** in Navigator and select **Refresh**.
6. Attach to your desired chart.

---

## 4. Key Configurable Parameters
| Parameter | Default Value | Description |
| :--- | :--- | :--- |
| `InpPartnerKey` | `PROPFIRM_PARTNER_DEMO` | Your custom co-branded partner token. |
| `InpReferenceBars` | `60` | Pattern window analyzed for empirical returns. |
| `InpForecastHorizon` | `22` | Forward projection bars ($T+22$). |
| `InpSigmaMult` | `2.10` | Confidence band width ($2.1\sigma \approx 95\%$ confidence). |
| `InpRegime` | `REGIME_BASELINE` | Stress test modes: Baseline, Liquidity Vacuum, CPI Spike, Cascade. |

---

## 5. Technical Support & Broker Licensing
- Technical Inquiries: `arkankl07@gmail.com`
- Live Partner Sandbox: [https://aravinthragav.github.io/xpredictor/](https://aravinthragav.github.io/xpredictor/)
