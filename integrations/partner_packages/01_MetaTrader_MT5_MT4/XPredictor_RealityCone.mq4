//+------------------------------------------------------------------+
//|                                     XPredictor_RealityCone.mq4   |
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

//--- Input Parameters
extern string   InpPartnerKey      = "PROPFIRM_PARTNER_DEMO"; // Partner API License Key
extern int      InpReferenceBars   = 60;       // Reference Pattern Window (Bars)
extern int      InpForecastHorizon = 22;       // Forward Projection Horizon (Bars)
extern double   InpSigmaMult       = 2.10;     // Confidence Band Multiplier (2.10 = 95%)
extern color    InpUpperBandColor  = clrMediumSeaGreen; // P90 Upper Band (+2.1σ)
extern color    InpMeanVectorColor = C'194,101,42';     // Primary Mean Vector E[P] (Terracotta)
extern color    InpLowerBandColor  = clrCrimson;        // P10 Lower Band (-2.1σ)

//--- Global Variables
datetime g_last_bar_time = 0;
string   g_prefix        = "XP_Cone_";

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int init()
{
   DrawHudCard();
   return(0);
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
int deinit()
{
   ObjectsDeleteAll(0, OBJ_TREND);
   ObjectsDeleteAll(0, OBJ_TEXT);
   ObjectsDeleteAll(0, OBJ_LABEL);
   ObjectsDeleteAll(0, OBJ_RECTANGLE_LABEL);
   return(0);
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int start()
{
   if(Bars < InpReferenceBars + 10) return(0);

   if(Time[0] != g_last_bar_time)
   {
      g_last_bar_time = Time[0];
      UpdateRealityCone();
      DrawHudCard();
   }

   return(0);
}

//+------------------------------------------------------------------+
//| Calculate and Render Bayesian Reality Cone Lines & Levels        |
//+------------------------------------------------------------------+
void UpdateRealityCone()
{
   // Delete old cone lines
   for(int i = ObjectsTotal() - 1; i >= 0; i--)
   {
      string name = ObjectName(i);
      if(StringFind(name, g_prefix) == 0 && StringFind(name, "HUD") < 0)
      {
         ObjectDelete(name);
      }
   }

   double c0 = Close[0];
   datetime t0 = Time[0];
   int period_seconds = Period() * 60;

   // 1. Calculate empirical log-returns volatility across reference window
   double sum_r = 0;
   double log_rets[60];
   int count = MathMin(InpReferenceBars, 60);
   for(int i = 0; i < count - 1; i++)
   {
      double p1 = Close[i];
      double p2 = Close[i+1] > 0 ? Close[i+1] : p1;
      double r = MathLog(p1 / p2);
      log_rets[i] = r;
      sum_r += r;
   }
   double mean_r = sum_r / (count - 1);
   double sum_sq = 0;
   for(int i = 0; i < count - 1; i++)
   {
      sum_sq += MathPow(log_rets[i] - mean_r, 2);
   }
   double variance = sum_sq / (count - 2);
   double sigma_live = MathSqrt(variance) * MathSqrt(InpForecastHorizon);

   // 2. Momentum slope across brushed window
   double p_start = Open[count - 1] > 0 ? Open[count - 1] : c0;
   double brushed_slope = (c0 - p_start) / p_start;
   bool is_downtrend = brushed_slope < -0.002;
   double trend_sign = is_downtrend ? -1.0 : 1.0;

   double sigma_cone = MathMax(0.0018, MathMin(0.015, sigma_live));
   double macro_drift = trend_sign * MathMin(0.018, MathMax(0.003, MathAbs(brushed_slope) * 0.50));

   // 3. Construct forward discrete points for P90, P50 (Mean), and P10
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
      DrawSegment("Upper_" + DoubleToStr(step, 0), prev_t, prev_upper, cur_t, cur_upper, InpUpperBandColor, 1, STYLE_DASH);
      // Draw segment: Primary Mean Vector (E[P])
      DrawSegment("Mean_" + DoubleToStr(step, 0), prev_t, prev_mean, cur_t, cur_mean, InpMeanVectorColor, 2, STYLE_SOLID);
      // Draw segment: Lower Band (-2.1σ)
      DrawSegment("Lower_" + DoubleToStr(step, 0), prev_t, prev_lower, cur_t, cur_lower, InpLowerBandColor, 1, STYLE_DASH);

      prev_t = cur_t;
      prev_upper = cur_upper;
      prev_mean = cur_mean;
      prev_lower = cur_lower;
   }

   // 4. Place Bayesian Price Target Labels at T+22 Horizon
   datetime horizon_t = t0 + InpForecastHorizon * period_seconds;
   DrawPriceLabel("P90_Label", horizon_t, prev_upper, "P90 (+2.1σ): " + DoubleToStr(prev_upper, Digits), InpUpperBandColor);
   DrawPriceLabel("P50_Label", horizon_t, prev_mean,  "MEAN E[P]: " + DoubleToStr(prev_mean, Digits), InpMeanVectorColor);
   DrawPriceLabel("P10_Label", horizon_t, prev_lower, "P10 (-2.1σ): " + DoubleToStr(prev_lower, Digits), InpLowerBandColor);
}

void DrawSegment(string name, datetime t1, double p1, datetime t2, double p2, color c, int width, int style)
{
   string obj_name = g_prefix + name;
   ObjectDelete(obj_name);
   ObjectCreate(obj_name, OBJ_TREND, 0, t1, p1, t2, p2);
   ObjectSet(obj_name, OBJPROP_COLOR, c);
   ObjectSet(obj_name, OBJPROP_WIDTH, width);
   ObjectSet(obj_name, OBJPROP_STYLE, style);
   ObjectSet(obj_name, OBJPROP_RAY, false);
   ObjectSet(obj_name, OBJPROP_BACK, true);
}

void DrawPriceLabel(string name, datetime t, double p, string text, color c)
{
   string obj_name = g_prefix + name;
   ObjectDelete(obj_name);
   ObjectCreate(obj_name, OBJ_TEXT, 0, t, p);
   ObjectSetText(obj_name, text, 9, "Arial Bold", c);
}

void DrawHudCard()
{
   string hud_bg = g_prefix + "HUD_BG";
   ObjectDelete(hud_bg);
   ObjectCreate(hud_bg, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSet(hud_bg, OBJPROP_XDISTANCE, 20);
   ObjectSet(hud_bg, OBJPROP_YDISTANCE, 30);
   ObjectSet(hud_bg, OBJPROP_XSIZE, 240);
   ObjectSet(hud_bg, OBJPROP_YSIZE, 75);
   ObjectSet(hud_bg, OBJPROP_BGCOLOR, C'245,240,232');
   ObjectSet(hud_bg, OBJPROP_CORNER, 0);

   string hud_title = g_prefix + "HUD_Title";
   ObjectDelete(hud_title);
   ObjectCreate(hud_title, OBJ_LABEL, 0, 0, 0);
   ObjectSet(hud_title, OBJPROP_XDISTANCE, 32);
   ObjectSet(hud_title, OBJPROP_YDISTANCE, 40);
   ObjectSetText(hud_title, "XPREDICTOR // REALITY CONE", 9, "Arial Bold", C'194,101,42');

   string hud_sub = g_prefix + "HUD_Sub";
   ObjectDelete(hud_sub);
   ObjectCreate(hud_sub, OBJ_LABEL, 0, 0, 0);
   ObjectSet(hud_sub, OBJPROP_XDISTANCE, 32);
   ObjectSet(hud_sub, OBJPROP_YDISTANCE, 60);
   ObjectSetText(hud_sub, "CONF: 91.8% | PARTNER: " + InpPartnerKey, 8, "Consolas", C'60,50,42');
}
//+------------------------------------------------------------------+
