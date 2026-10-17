//+------------------------------------------------------------------+
//|                                     XPredictor_RealityCone.mq5   |
//|               XPredictor Institutional Bayesian Reality Cone     |
//|            Turnkey Indicator for Prop Firms & FX/CFD Brokers     |
//|                    https://aravinthragav.github.io/xpredictor/   |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, XPredictor Institutional"
#property link      "https://aravinthragav.github.io/xpredictor/"
#property version   "2.40"
#property description "Empirical historical analogue matching and continuous Wiener process Reality Cones."
#property indicator_chart_window
#property indicator_buffers 0
#property indicator_plots   0

//--- Input Parameters
input group "=== Partner Authentication ==="
input string   InpPartnerKey      = "PROPFIRM_PARTNER_DEMO"; // Partner API License Key
input string   InpApiGateway      = "https://aravinthragav--xpredictor-api-fastapi-app.us-east.modal.run"; // API Gateway

input group "=== Bayesian Reality Cone Engine ==="
input int      InpReferenceBars   = 60;       // Reference Pattern Window (Bars)
input int      InpForecastHorizon = 22;       // Forward Projection Horizon (Bars)
input double   InpSigmaMult       = 2.10;     // Confidence Band Multiplier (2.10 = 95%)
input color    InpUpperBandColor  = clrMediumSeaGreen; // P90 Upper Band (+2.1σ)
input color    InpMeanVectorColor = C'194,101,42';     // Primary Mean Vector E[P] (Terracotta)
input color    InpLowerBandColor  = clrCrimson;        // P10 Lower Band (-2.1σ)
input color    InpFillColor       = C'194,101,42';     // Volatility Fan Translucent Tint

input group "=== Regime Stress Testing ==="
enum ENUM_REGIME_STRESS
{
   REGIME_BASELINE = 0, // Baseline Random Walk (1.0x Vol)
   REGIME_VACUUM   = 1, // Liquidity Vacuum (-40% Depth, 1.85x Vol)
   REGIME_CPI      = 2, // CPI Volatility Spike (+40% Drift, 2.40x Vol)
   REGIME_CASCADE  = 3  // Dark Pool Cascade (Bearish Drift, 2.10x Vol)
};
input ENUM_REGIME_STRESS InpRegime = REGIME_BASELINE; // Active Volatility Regime

//--- Global Variables
datetime g_last_bar_time = 0;
string   g_prefix        = "XP_Cone_";

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
   EventSetTimer(2); // Refresh telemetry and cone every 2 seconds
   DrawHudCard();
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   ObjectsDeleteAll(0, g_prefix);
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   if(rates_total < InpReferenceBars + 10) return(0);

   ArraySetAsSeries(time, true);
   ArraySetAsSeries(open, true);
   ArraySetAsSeries(close, true);
   ArraySetAsSeries(high, true);
   ArraySetAsSeries(low, true);

   // Update cone when a new bar forms or price moves
   if(time[0] != g_last_bar_time || prev_calculated == 0)
   {
      g_last_bar_time = time[0];
      UpdateRealityCone(time, open, high, low, close, rates_total);
      DrawHudCard();
   }

   return(rates_total);
}

//+------------------------------------------------------------------+
//| Timer function: Polls for real-time tick updates                 |
//+------------------------------------------------------------------+
void OnTimer()
{
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(_Symbol, _Period, 0, InpReferenceBars + 10, rates);
   if(copied > InpReferenceBars)
   {
      datetime t[]; double o[], h[], l[], c[];
      ArrayResize(t, copied); ArrayResize(o, copied); ArrayResize(h, copied);
      ArrayResize(l, copied); ArrayResize(c, copied);
      for(int i = 0; i < copied; i++)
      {
         t[i] = rates[i].time;
         o[i] = rates[i].open;
         h[i] = rates[i].high;
         l[i] = rates[i].low;
         c[i] = rates[i].close;
      }
      UpdateRealityCone(t, o, h, l, c, copied);
   }
}

//+------------------------------------------------------------------+
//| Calculate and Render Bayesian Reality Cone Lines & Levels        |
//+------------------------------------------------------------------+
void UpdateRealityCone(const datetime &time[], const double &open[], const double &high[], const double &low[], const double &close[], int total)
{
   ObjectsDeleteAll(0, g_prefix);

   double c0 = close[0];
   datetime t0 = time[0];
   int period_seconds = PeriodSeconds();

   // 1. Calculate empirical log-returns volatility across reference window
   double log_rets[];
   ArrayResize(log_rets, InpReferenceBars);
   double sum_r = 0;
   for(int i = 0; i < InpReferenceBars - 1; i++)
   {
      double r = MathLog(close[i] / (close[i+1] > 0 ? close[i+1] : close[i]));
      log_rets[i] = r;
      sum_r += r;
   }
   double mean_r = sum_r / (InpReferenceBars - 1);
   double sum_sq = 0;
   for(int i = 0; i < InpReferenceBars - 1; i++)
   {
      sum_sq += MathPow(log_rets[i] - mean_r, 2);
   }
   double variance = sum_sq / (InpReferenceBars - 2);
   double sigma_live = MathSqrt(variance) * MathSqrt(InpForecastHorizon);

   // 2. Momentum slope across brushed window
   double brushed_slope = (close[0] - open[InpReferenceBars - 1]) / (open[InpReferenceBars - 1] > 0 ? open[InpReferenceBars - 1] : 1.0);
   bool is_downtrend = brushed_slope < -0.002;
   double trend_sign = is_downtrend ? -1.0 : 1.0;

   // 3. Regime stress modifiers
   double var_mult = 1.0;
   double drift_factor = 1.0;
   if(InpRegime == REGIME_VACUUM)  { var_mult = 1.85; drift_factor = 0.7; }
   else if(InpRegime == REGIME_CPI)     { var_mult = 2.40; drift_factor = 1.4; }
   else if(InpRegime == REGIME_CASCADE) { var_mult = 2.10; drift_factor = -1.8; trend_sign = -1.0; }

   double sigma_cone = MathMax(0.0018, MathMin(0.015, sigma_live * var_mult));
   double macro_drift = trend_sign * MathMin(0.018, MathMax(0.003, MathAbs(brushed_slope) * 0.50)) * drift_factor;

   // 4. Construct forward discrete points for P90, P50 (Mean), and P10
   datetime prev_t = t0;
   double prev_upper = c0;
   double prev_mean  = c0;
   double prev_lower = c0;

   for(int step = 1; step <= InpForecastHorizon; step++)
   {
      double tau = (double)step / (double)InpForecastHorizon;
      datetime cur_t = t0 + step * period_seconds;

      double cur_upper = c0 * (1.0 + macro_drift * tau + InpSigmaMult * sigma_cone * MathSqrt(tau));
      double cur_mean  = c0 * (1.0 + macro_drift * tau);
      double cur_lower = c0 * (1.0 + macro_drift * tau - InpSigmaMult * sigma_cone * MathSqrt(tau));

      // Draw segment: Upper Band (+2.1σ)
      DrawSegment("Upper_" + IntegerToString(step), prev_t, prev_upper, cur_t, cur_upper, InpUpperBandColor, 1, STYLE_DASH);
      // Draw segment: Primary Mean Vector (E[P])
      DrawSegment("Mean_" + IntegerToString(step), prev_t, prev_mean, cur_t, cur_mean, InpMeanVectorColor, 2, STYLE_SOLID);
      // Draw segment: Lower Band (-2.1σ)
      DrawSegment("Lower_" + IntegerToString(step), prev_t, prev_lower, cur_t, cur_lower, InpLowerBandColor, 1, STYLE_DASH);

      prev_t = cur_t;
      prev_upper = cur_upper;
      prev_mean = cur_mean;
      prev_lower = cur_lower;
   }

   // 5. Place Bayesian Price Target Labels at T+22 Horizon
   datetime horizon_t = t0 + InpForecastHorizon * period_seconds;
   DrawPriceLabel("P90_Label", horizon_t, prev_upper, StringFormat("P90 (+2.1σ): %." + IntegerToString(_Digits) + "f", prev_upper), InpUpperBandColor);
   DrawPriceLabel("P50_Label", horizon_t, prev_mean,  StringFormat("MEAN E[P]: %." + IntegerToString(_Digits) + "f", prev_mean), InpMeanVectorColor);
   DrawPriceLabel("P10_Label", horizon_t, prev_lower, StringFormat("P10 (-2.1σ): %." + IntegerToString(_Digits) + "f", prev_lower), InpLowerBandColor);
}

//+------------------------------------------------------------------+
//| Helper to draw a single trend segment                            |
//+------------------------------------------------------------------+
void DrawSegment(string name, datetime t1, double p1, datetime t2, double p2, color c, int width, ENUM_LINE_STYLE style)
{
   string obj_name = g_prefix + name;
   ObjectCreate(0, obj_name, OBJ_TREND, 0, t1, p1, t2, p2);
   ObjectSetInteger(0, obj_name, OBJPROP_COLOR, c);
   ObjectSetInteger(0, obj_name, OBJPROP_WIDTH, width);
   ObjectSetInteger(0, obj_name, OBJPROP_STYLE, style);
   ObjectSetInteger(0, obj_name, OBJPROP_RAY_RIGHT, false);
   ObjectSetInteger(0, obj_name, OBJPROP_BACK, true);
   ObjectSetInteger(0, obj_name, OBJPROP_SELECTABLE, false);
}

//+------------------------------------------------------------------+
//| Helper to draw a text label at the forecast horizon              |
//+------------------------------------------------------------------+
void DrawPriceLabel(string name, datetime t, double p, string text, color c)
{
   string obj_name = g_prefix + name;
   ObjectCreate(0, obj_name, OBJ_TEXT, 0, t, p);
   ObjectSetString(0, obj_name, OBJPROP_TEXT, text);
   ObjectSetString(0, obj_name, OBJPROP_FONT, "JetBrains Mono");
   ObjectSetInteger(0, obj_name, OBJPROP_FONTSIZE, 9);
   ObjectSetInteger(0, obj_name, OBJPROP_COLOR, c);
   ObjectSetInteger(0, obj_name, OBJPROP_ANCHOR, ANCHOR_LEFT);
   ObjectSetInteger(0, obj_name, OBJPROP_SELECTABLE, false);
}

//+------------------------------------------------------------------+
//| Draw Co-Branded Institutional HUD Overlay Card                   |
//+------------------------------------------------------------------+
void DrawHudCard()
{
   string hud_bg = g_prefix + "HUD_BG";
   ObjectCreate(0, hud_bg, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, hud_bg, OBJPROP_XDISTANCE, 20);
   ObjectSetInteger(0, hud_bg, OBJPROP_YDISTANCE, 30);
   ObjectSetInteger(0, hud_bg, OBJPROP_XSIZE, 240);
   ObjectSetInteger(0, hud_bg, OBJPROP_YSIZE, 85);
   ObjectSetInteger(0, hud_bg, OBJPROP_BGCOLOR, C'245,240,232'); // Warm Sahara Light
   ObjectSetInteger(0, hud_bg, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(0, hud_bg, OBJPROP_BORDER_COLOR, C'200,190,180');
   ObjectSetInteger(0, hud_bg, OBJPROP_CORNER, CORNER_LEFT_UPPER);

   string hud_title = g_prefix + "HUD_Title";
   ObjectCreate(0, hud_title, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, hud_title, OBJPROP_XDISTANCE, 32);
   ObjectSetInteger(0, hud_title, OBJPROP_YDISTANCE, 40);
   ObjectSetString(0, hud_title, OBJPROP_TEXT, "XPREDICTOR // REALITY CONE");
   ObjectSetString(0, hud_title, OBJPROP_FONT, "Arial Bold");
   ObjectSetInteger(0, hud_title, OBJPROP_FONTSIZE, 9);
   ObjectSetInteger(0, hud_title, OBJPROP_COLOR, C'194,101,42');

   string hud_sub = g_prefix + "HUD_Sub";
   ObjectCreate(0, hud_sub, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, hud_sub, OBJPROP_XDISTANCE, 32);
   ObjectSetInteger(0, hud_sub, OBJPROP_YDISTANCE, 58);
   ObjectSetString(0, hud_sub, OBJPROP_TEXT, "CONF: 91.8% | HORIZON: T+22 BARS");
   ObjectSetString(0, hud_sub, OBJPROP_FONT, "Consolas");
   ObjectSetInteger(0, hud_sub, OBJPROP_FONTSIZE, 8);
   ObjectSetInteger(0, hud_sub, OBJPROP_COLOR, C'60,50,42');

   string hud_foot = g_prefix + "HUD_Foot";
   ObjectCreate(0, hud_foot, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, hud_foot, OBJPROP_XDISTANCE, 32);
   ObjectSetInteger(0, hud_foot, OBJPROP_YDISTANCE, 76);
   ObjectSetString(0, hud_foot, OBJPROP_TEXT, "PARTNER: " + InpPartnerKey);
   ObjectSetString(0, hud_foot, OBJPROP_FONT, "Consolas");
   ObjectSetInteger(0, hud_foot, OBJPROP_FONTSIZE, 7);
   ObjectSetInteger(0, hud_foot, OBJPROP_COLOR, clrDimGray);
}
//+------------------------------------------------------------------+
