# Modern Web Prop Stack Partner Integration Guide
### TradeLocker, DXtrade, Match-Trader & Custom Prop CRM Portals

This turnkey package is designed for modern web-first prop trading firms (e.g. **FundedNext, Funding Pips, Blue Guardian, MyFundedFX, Goat Funded Trader**) seeking 3-minute deployment into client evaluation dashboards.

---

## 1. Package Files
- `xpredictor_embed_widget.html` — Interactive preview & turnkey HTML embed snippet
- `webhook_payload_spec.json` — JSON Schema for real-time risk & volatility alerts
- `webhook_risk_listener.py` — Python HTTP receiver for CRM integration

---

## 2. Fast 3-Minute Iframe Integration
Paste this single snippet into your React, Vue, or Web dashboard:

```html
<iframe 
  src="https://aravinthragav.github.io/xpredictor/?partner=YOUR_FIRM_NAME&asset=XAUUSD&tf=1h" 
  width="100%" 
  height="640" 
  frameborder="0" 
  style="border-radius: 16px; border: 1px solid rgba(120, 112, 106, 0.25);"
  allow="clipboard-write">
</iframe>
```

### URL Configuration Parameters:
- `partner`: Your firm identifier (e.g. `fundednext`, `fundingpips`, `blueguardian`). Dynamically co-brands the terminal and pre-fills partner metadata.
- `asset`: Default loaded asset (`XAUUSD`, `SPX`, `NDX`, `DAX`, `OIL`, `BTCUSDT`, `ETHUSDT`).
- `tf`: Default timeframe (`15m`, `1h`, `4h`).

---

## 3. Real-Time Risk Webhooks for CRM & TradeLocker Alerts
When market conditions breach $+2.1\sigma$ or $-2.1\sigma$ boundaries, our engine dispatches a POST webhook to your server endpoint:

```bash
# Run the local listener demo:
python webhook_risk_listener.py 8080
```

---

## 4. Technical Support
- Developer Support: `arkankl07@gmail.com`
- Live Partner Sandbox: [https://aravinthragav.github.io/xpredictor/](https://aravinthragav.github.io/xpredictor/)
