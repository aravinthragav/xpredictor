"""
services/growth-bot/chart_renderer.py
Renders institutional 1200x675 PNG preview cards of the Hybrid AI Reality Cone,
historical candles, and Bayesian confidence levels using pure PIL.
"""

import math
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont


def render_reality_cone_card(
    symbol: str,
    timeframe: str,
    candles: List[Dict[str, float]],
    twin_info: Dict[str, Any],
    p90: float,
    p50: float,
    p10: float,
    confidence_pct: float,
    output_path: str = "reality_cone_alert.png"
) -> str:
    """
    Renders an institutional 1200x675 chart card with candles, reality cone fan,
    Bayesian price markers, and telemetry badges.
    """
    WIDTH = 1200
    HEIGHT = 675
    
    # Sahara clean theme colors
    BG_COLOR = (255, 255, 255)
    GRID_COLOR = (242, 236, 228)
    TEXT_MAIN = (45, 38, 33)
    TEXT_MUTED = (140, 130, 120)
    PRIMARY_ORANGE = (194, 101, 42)
    GREEN_CANDLE = (5, 150, 105)
    RED_CANDLE = (225, 29, 72)
    CONE_FILL = (194, 101, 42, 38)
    CONE_EDGE = (194, 101, 42, 140)
    
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Try loading clean font, fallback to default
    try:
        font_lg = ImageFont.truetype("arialbd.ttf", 24)
        font_md = ImageFont.truetype("arialbd.ttf", 16)
        font_sm = ImageFont.truetype("arial.ttf", 13)
        font_mono = ImageFont.truetype("consola.ttf", 13)
    except Exception:
        font_lg = ImageFont.load_default()
        font_md = ImageFont.load_default()
        font_sm = ImageFont.load_default()
        font_mono = ImageFont.load_default()

    # Layout dimensions
    TOP_BAR_H = 80
    BOTTOM_BAR_H = 60
    RIGHT_AXIS_W = 100
    LEFT_PAD = 40
    CHART_TOP = TOP_BAR_H + 20
    CHART_BOTTOM = HEIGHT - BOTTOM_BAR_H - 20
    CHART_RIGHT = WIDTH - RIGHT_AXIS_W
    CHART_W = CHART_RIGHT - LEFT_PAD
    CHART_H = CHART_BOTTOM - CHART_TOP
    
    # Top Header Banner
    draw.rectangle([(0, 0), (WIDTH, TOP_BAR_H)], fill=(250, 246, 240))
    draw.line([(0, TOP_BAR_H), (WIDTH, TOP_BAR_H)], fill=GRID_COLOR, width=1)
    
    # Header Title
    title_text = f"XPredictor  |  {symbol} ({timeframe.upper()}) HYBRID AI REALITY CONE"
    draw.text((LEFT_PAD, 26), title_text, fill=TEXT_MAIN, font=font_lg)
    
    # Confidence Badge
    conf_badge_text = f"CONFIDENCE: {confidence_pct:.1f}%"
    badge_x = WIDTH - 260
    badge_y = 22
    draw.rounded_rectangle([(badge_x, badge_y), (badge_x + 220, badge_y + 36)], radius=6, fill=(5, 150, 105))
    draw.text((badge_x + 18, badge_y + 8), conf_badge_text, fill=(255, 255, 255), font=font_md)

    if not candles:
        img.save(output_path, "PNG")
        return output_path

    # Price range calculation
    min_p = min(c["low"] for c in candles)
    max_p = max(c["high"] for c in candles)
    min_p = min(min_p, p10)
    max_p = max(max_p, p90)
    span = (max_p - min_p) or 1.0
    pad = span * 0.12
    min_p -= pad
    max_p += pad
    span = max_p - min_p

    def p_to_y(price: float) -> float:
        return CHART_BOTTOM - ((price - min_p) / span) * CHART_H

    # Horizontal Grid Lines & Price Labels
    for i in range(5):
        y_norm = i / 4.0
        gy = CHART_TOP + y_norm * CHART_H
        draw.line([(LEFT_PAD, gy), (CHART_RIGHT, gy)], fill=GRID_COLOR, width=1)
        grid_price = max_p - y_norm * span
        draw.text((CHART_RIGHT + 12, gy - 7), f"{grid_price:,.2f}", fill=TEXT_MUTED, font=font_mono)

    # Candlestick plotting
    n_candles = len(candles)
    horizon_bars = 22
    total_slots = n_candles + horizon_bars
    slot_w = CHART_W / total_slots
    candle_w = max(3.0, slot_w * 0.65)

    last_x = LEFT_PAD
    last_close_y = p_to_y(candles[-1]["close"])

    for i, c in enumerate(candles):
        cx = LEFT_PAD + i * slot_w + slot_w / 2.0
        last_x = cx
        cy_open = p_to_y(c["open"])
        cy_close = p_to_y(c["close"])
        cy_high = p_to_y(c["high"])
        cy_low = p_to_y(c["low"])

        is_bullish = c["close"] >= c["open"]
        color = GREEN_CANDLE if is_bullish else RED_CANDLE

        # Wick
        draw.line([(cx, cy_high), (cx, cy_low)], fill=color, width=1)
        # Body
        top_y = min(cy_open, cy_close)
        bot_y = max(cy_open, cy_close)
        if bot_y - top_y < 1:
            bot_y = top_y + 1
        draw.rectangle([(cx - candle_w / 2.0, top_y), (cx + candle_w / 2.0, bot_y)], fill=color)

    # Reality Cone Fan (+2.1σ, P50, -2.1σ)
    cone_layer = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))
    cone_draw = ImageDraw.Draw(cone_layer, "RGBA")

    cone_end_x = min(CHART_RIGHT - 20, last_x + horizon_bars * slot_w)
    p90_y = p_to_y(p90)
    p50_y = p_to_y(p50)
    p10_y = p_to_y(p10)

    # Fan polygon curve
    upper_poly = [(last_x, last_close_y)]
    lower_poly = [(last_x, last_close_y)]
    steps = 22
    for s in range(1, steps + 1):
        tau = s / float(steps)
        curr_x = last_x + s * ((cone_end_x - last_x) / float(steps))
        cur_p90 = candles[-1]["close"] + (p90 - candles[-1]["close"]) * math.sqrt(tau)
        cur_p10 = candles[-1]["close"] + (p10 - candles[-1]["close"]) * math.sqrt(tau)
        upper_poly.append((curr_x, p_to_y(cur_p90)))
        lower_poly.append((curr_x, p_to_y(cur_p10)))

    cone_polygon = upper_poly + list(reversed(lower_poly))
    cone_draw.polygon(cone_polygon, fill=(194, 101, 42, 45))

    # Cone outline & bounds
    for i in range(len(upper_poly) - 1):
        cone_draw.line([upper_poly[i], upper_poly[i + 1]], fill=(194, 101, 42, 160), width=2)
        cone_draw.line([lower_poly[i], lower_poly[i + 1]], fill=(194, 101, 42, 160), width=2)

    # P50 Center Drift
    cone_draw.line([(last_x, last_close_y), (cone_end_x, p50_y)], fill=(194, 101, 42, 220), width=2)

    # Composite cone onto main image
    img = Image.alpha_composite(img, cone_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Right-hand Bayesian Tag Pills
    bayes_tags = [
        ("P90: " + f"{p90:,.2f}", p90_y, (5, 150, 105)),
        ("P50: " + f"{p50:,.2f}", p50_y, PRIMARY_ORANGE),
        ("P10: " + f"{p10:,.2f}", p10_y, (225, 29, 72))
    ]
    for tag_txt, ty, tag_col in bayes_tags:
        pill_w = 100
        pill_h = 22
        draw.rounded_rectangle(
            [(cone_end_x + 6, ty - pill_h / 2), (cone_end_x + 6 + pill_w, ty + pill_h / 2)],
            radius=4,
            fill=tag_col
        )
        draw.text((cone_end_x + 12, ty - 7), tag_txt, fill=(255, 255, 255), font=font_mono)

    # Bottom Telemetry & Footnote
    draw.rectangle([(0, HEIGHT - BOTTOM_BAR_H), (WIDTH, HEIGHT)], fill=(250, 246, 240))
    draw.line([(0, HEIGHT - BOTTOM_BAR_H), (WIDTH, HEIGHT - BOTTOM_BAR_H)], fill=GRID_COLOR, width=1)
    
    twin_label = twin_info.get("date", "Historical Peak")
    twin_score = twin_info.get("match_score", 96.0)
    footer_left = f"Top Historical Twin: #{twin_info.get('rank', 1)} {symbol} ({twin_label})  •  {twin_score:.1f}% Match"
    draw.text((LEFT_PAD, HEIGHT - BOTTOM_BAR_H + 20), footer_left, fill=TEXT_MAIN, font=font_md)

    footer_right = "xpredictor.com  |  Institutional Bayesian AI"
    draw.text((WIDTH - 310, HEIGHT - BOTTOM_BAR_H + 22), footer_right, fill=TEXT_MUTED, font=font_sm)

    img = img.convert("RGB")
    img.save(output_path, "PNG", quality=95)
    return output_path


if __name__ == "__main__":
    # Test generation
    sample_candles = []
    p = 2650.0
    for i in range(40):
        delta = math.sin(i * 0.2) * 4.0 + 1.2
        c_open = p
        c_close = p + delta
        c_high = max(c_open, c_close) + 2.5
        c_low = min(c_open, c_close) - 2.0
        sample_candles.append({"open": c_open, "high": c_high, "low": c_low, "close": c_close})
        p = c_close

    out = render_reality_cone_card(
        symbol="XAUUSD",
        timeframe="1h",
        candles=sample_candles,
        twin_info={"rank": 1, "date": "Oct 18, 2024 Breakout", "match_score": 96.4},
        p90=p + 38.0,
        p50=p + 14.0,
        p10=p - 18.0,
        confidence_pct=91.8,
        output_path="test_social_card.png"
    )
    print(f"Rendered test card: {out}")
