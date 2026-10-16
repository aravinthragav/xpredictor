//+------------------------------------------------------------------+
//|                                     XPredictor_RealityCone.mq5   |
//|                        Copyright 2026, XPredictor Systems Corp.   |
//|                                 https://aravinthragav.github.io/xpredictor/ |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, XPredictor Systems Corp."
#property link        "https://aravinthragav.github.io/xpredictor/"
#property version     "4.80"
#property description "Institutional Bayesian Reality Cone Trading EA"
#property description "Executes high-confidence trades anchored to empirical variance cones and structural price-action analogs."

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>

//--- Input Parameters
input group "=== Execution & Risk Parameters ==="
input double   InpLotSize           = 0.10;     // Fixed Order Lot Size
input double   InpMinConfidence     = 85.0;     // Minimum Confidence Threshold (%)
input double   InpMinDriftBps       = 12.0;     // Minimum Directional Drift (Basis Points)
input double   InpSigmaMultiple     = 2.10;     // Cone Variance Envelope (Sigma σ)
input double   InpTakeProfitSigma   = 2.00;     // Take Profit Target (Sigma σ)
input double   InpStopLossSigma     = 2.10;     // Stop Loss Boundary (Sigma σ)
input ulong    InpMagicNumber       = 768001;   // Magic Number
input int      InpSlippagePoints    = 15;       // Max Allowed Slippage (Points)

input group "=== Dynamic Trailing & Position Management ==="
input bool     InpUseTrailingSL     = false;    // Dynamic Cone Trailing Stop Loss
input bool     InpUseBreakEven      = false;    // Dynamic Breakeven Activation
input double   InpBEActivationSigma = 1.00;     // Breakeven Activation Threshold (Sigma σ)
input int      InpBEOffsetPoints    = 20;       // Breakeven Lock-in Offset (Points)
input double   InpTrailingSigma     = 1.50;     // Trailing Distance Envelope (Sigma σ)
input int      InpTrailingStepPts   = 30;       // Trailing Step Increment (Points)
input bool     InpUseDynamicTP      = false;    // Dynamic TP Expansion (Let Winners Run)
input double   InpExpandedTPSigma   = 2.75;     // Expanded TP Target on High Momentum (Sigma σ)

input group "=== Session Timing & News Spread Guards ==="
input bool     InpUseSessionFilter  = false;    // Enable Session Timing Filter
input int      InpSessionStartHour  = 8;        // Trading Start Hour (Server Time)
input int      InpSessionEndHour    = 20;       // Trading End Hour (Server Time)
input bool     InpUseSpreadGuard    = true;     // Enable Spread Guard (News & Rollover Guard)
input int      InpMaxSpreadPoints   = 350;      // Max Allowed Spread (Points, 0 = Disabled)

input group "=== Reality Cone Modeling ==="
input int      InpLookbackBars      = 64;       // Structural Regime Lookback Window (L)
input int      InpProjectionBars    = 20;       // Forward Forecast Horizon Bars (H)
input bool     InpDrawChartCone     = true;     // Draw Visual Reality Cone on Chart
input color    InpConeColor         = C'194,101,42'; // Cone Color (Sahara Terracotta)
input color    InpMeanColor         = C'220,130,60'; // Mean Vector Color

//--- Global Objects
CTrade         ExtTrade;
CPositionInfo  ExtPosition;
datetime       ExtLastBarTime = 0;
string         ExtPrefix = "XPred_";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   ExtTrade.SetExpertMagicNumber(InpMagicNumber);
   ExtTrade.SetDeviationInPoints(InpSlippagePoints);
   ExtTrade.SetTypeFillingBySymbol(_Symbol);

   PrintFormat("[XPredictor] Initialized successfully on %s (Period: %s). Minimum Confidence: %.1f%%, Drift: %.1f bps",
               _Symbol, EnumToString(_Period), InpMinConfidence, InpMinDriftBps);

   if(InpDrawChartCone)
      CreateChartDashboard();

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   ObjectsDeleteAll(0, ExtPrefix);
   ChartRedraw(0);
   Print("[XPredictor] Deinitialized and removed chart overlays.");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check for new bar open to evaluate regime formation
   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   bool isNewBar = (currentBarTime != ExtLastBarTime);

   // Extract bar data
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(_Symbol, _Period, 0, InpLookbackBars + 5, rates);
   if(copied < InpLookbackBars)
      return;

   // Statistical Variables
   double currentPrice = rates[0].close;
   double lookbackStartPrice = rates[InpLookbackBars - 1].open;
   
   // 1. Calculate Implied Drift in Basis Points (bps)
   // 1 bps = 0.01% = 0.0001
   double driftRatio = (currentPrice - lookbackStartPrice) / (lookbackStartPrice > 0 ? lookbackStartPrice : 1.0);
   double driftBps = driftRatio * 10000.0;

   // 2. Calculate Log Returns, Mean, and Standard Deviation (Volatility)
   double sumReturns = 0.0;
   double returns[];
   ArrayResize(returns, InpLookbackBars - 1);
   
   for(int i = 0; i < InpLookbackBars - 1; i++)
   {
      double r = MathLog(rates[i].close / (rates[i + 1].close > 0 ? rates[i + 1].close : rates[i].close));
      returns[i] = r;
      sumReturns += r;
   }
   
   double meanReturn = sumReturns / (double)(InpLookbackBars - 1);
   
   double sumSqDiff = 0.0;
   for(int i = 0; i < InpLookbackBars - 1; i++)
   {
      double diff = returns[i] - meanReturn;
      sumSqDiff += diff * diff;
   }
   double variance = sumSqDiff / (double)(InpLookbackBars - 2);
   double stdDev = MathSqrt(variance);
   double annualizedIV = stdDev * MathSqrt(252.0 * 24.0) * 100.0; // Hourly base annualized

   // 3. Compute Empirical Confidence Score (0% to 100%)
   // Higher signal-to-noise ratio and directional persistence yield higher confidence
   double snr = (stdDev > 0.00001) ? MathAbs(meanReturn) / stdDev : 0.0;
   double confidence = MathMin(99.4, 70.0 + (snr * 18.0) + (MathMin(MathAbs(driftBps), 50.0) * 0.35));

   // 4. Calculate Quantile Boundaries for Horizon H
   double sigmaMove = currentPrice * stdDev * MathSqrt((double)InpProjectionBars) * InpSigmaMultiple;
   double upperConeBound = currentPrice + (currentPrice * meanReturn * InpProjectionBars) + sigmaMove;
   double lowerConeBound = currentPrice + (currentPrice * meanReturn * InpProjectionBars) - sigmaMove;
   double meanTarget     = currentPrice + (currentPrice * meanReturn * InpProjectionBars);

   // 5. Update Visual Chart Elements
   if(InpDrawChartCone)
   {
      UpdateChartCone(rates[0].time, currentPrice, upperConeBound, lowerConeBound, meanTarget, driftBps, confidence);
      UpdateDashboard(driftBps, confidence, annualizedIV, upperConeBound, lowerConeBound, meanTarget);
   }

   // 6. Manage Trailing Stops & Dynamic Position Management
   ManageTrailingStops(currentPrice, stdDev, driftBps);

   // 7. Automated Trading Engine Logic (Run on new bar confirmation)
   if(isNewBar)
   {
      ExtLastBarTime = currentBarTime;
      ManageAutomatedExecution(driftBps, confidence, currentPrice, stdDev);
   }
}

//+------------------------------------------------------------------+
//| Manage Trailing Stop Loss & Dynamic TP based on Reality Cone      |
//+------------------------------------------------------------------+
void ManageTrailingStops(double currentPrice, double stdDev, double driftBps)
{
   if(!InpUseTrailingSL && !InpUseBreakEven && !InpUseDynamicTP) return;

   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   double stopLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * point;
   double minSafety = 200 * point;

   double trailDistance = currentPrice * stdDev * MathSqrt((double)InpProjectionBars) * InpTrailingSigma;
   if(trailDistance < minSafety) trailDistance = minSafety;

   double beThreshold = currentPrice * stdDev * MathSqrt((double)InpProjectionBars) * InpBEActivationSigma;
   if(beThreshold < minSafety) beThreshold = minSafety;

   double beOffset = InpBEOffsetPoints * point;
   double stepDistance = InpTrailingStepPts * point;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(ExtPosition.SelectByIndex(i))
      {
         if(ExtPosition.Symbol() == _Symbol && ExtPosition.Magic() == InpMagicNumber)
         {
            double openPrice = ExtPosition.PriceOpen();
            double currentSL = ExtPosition.StopLoss();
            double currentTP = ExtPosition.TakeProfit();
            ENUM_POSITION_TYPE posType = ExtPosition.PositionType();

            if(posType == POSITION_TYPE_BUY)
            {
               double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
               double newSL = currentSL;
               double newTP = currentTP;

               // 1. Breakeven Step: if profit >= beThreshold, lock in openPrice + offset
               if(InpUseBreakEven && (bid - openPrice >= beThreshold))
               {
                  double beTarget = openPrice + beOffset;
                  if(newSL < beTarget - point)
                     newSL = beTarget;
               }

               // 2. Trailing SL Step: trail behind current price by trailDistance
               if(InpUseTrailingSL && (bid - openPrice > trailDistance))
               {
                  double trailTarget = bid - trailDistance;
                  if(trailTarget > newSL + stepDistance)
                     newSL = trailTarget;
               }

               // 3. Dynamic TP Expansion: If drift accelerates in trade direction, expand TP
               if(InpUseDynamicTP && (driftBps >= InpMinDriftBps * 1.5))
               {
                  double expandedTP = openPrice + (currentPrice * stdDev * MathSqrt((double)InpProjectionBars) * InpExpandedTPSigma);
                  if(expandedTP > currentTP + stepDistance)
                     newTP = expandedTP;
               }

               // Execute modification if improved and respects broker stops level
               bool slChanged = (newSL > currentSL + point && (bid - newSL) > stopLevel);
               bool tpChanged = (newTP > currentTP + point && (newTP - bid) > stopLevel);

               if(slChanged || tpChanged)
               {
                  newSL = NormalizeDouble(newSL, digits);
                  newTP = NormalizeDouble(newTP, digits);
                  if(ExtTrade.PositionModify(ExtPosition.Ticket(), newSL, newTP))
                  {
                     PrintFormat("[XPredictor] BUY #%I64u Modified -> SL: %.*f, TP: %.*f",
                                 ExtPosition.Ticket(), digits, newSL, digits, newTP);
                  }
               }
            }
            else if(posType == POSITION_TYPE_SELL)
            {
               double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
               double newSL = currentSL;
               double newTP = currentTP;

               // 1. Breakeven Step: if profit >= beThreshold, lock in openPrice - offset
               if(InpUseBreakEven && (openPrice - ask >= beThreshold))
               {
                  double beTarget = openPrice - beOffset;
                  if(newSL > beTarget + point || newSL == 0)
                     newSL = beTarget;
               }

               // 2. Trailing SL Step: trail behind current price by trailDistance
               if(InpUseTrailingSL && (openPrice - ask > trailDistance))
               {
                  double trailTarget = ask + trailDistance;
                  if(newSL == 0 || trailTarget < newSL - stepDistance)
                  {
                     if(newSL == 0) newSL = trailTarget;
                     else newSL = MathMin(newSL, trailTarget);
                  }
               }

               // 3. Dynamic TP Expansion: If drift accelerates in trade direction, expand TP
               if(InpUseDynamicTP && (driftBps <= -InpMinDriftBps * 1.5))
               {
                  double expandedTP = openPrice - (currentPrice * stdDev * MathSqrt((double)InpProjectionBars) * InpExpandedTPSigma);
                  if(expandedTP < currentTP - stepDistance && expandedTP > 0)
                     newTP = expandedTP;
               }

               // Execute modification if improved and respects broker stops level
               bool slChanged = (((newSL < currentSL - point) || (currentSL == 0)) && (newSL - ask) > stopLevel && newSL > 0);
               bool tpChanged = (newTP < currentTP - point && (ask - newTP) > stopLevel && newTP > 0);

               if(slChanged || tpChanged)
               {
                  newSL = NormalizeDouble(newSL, digits);
                  newTP = NormalizeDouble(newTP, digits);
                  if(ExtTrade.PositionModify(ExtPosition.Ticket(), newSL, newTP))
                  {
                     PrintFormat("[XPredictor] SELL #%I64u Modified -> SL: %.*f, TP: %.*f",
                                 ExtPosition.Ticket(), digits, newSL, digits, newTP);
                  }
               }
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Execution Engine: Enters high-confidence setups with cone bounds |
//+------------------------------------------------------------------+
void ManageAutomatedExecution(double driftBps, double confidence, double currentPrice, double stdDev)
{
   // Check if we already have an open position under this magic number
   bool hasBuyPosition = false;
   bool hasSellPosition = false;
   ulong openTicket = 0;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(ExtPosition.SelectByIndex(i))
      {
         if(ExtPosition.Symbol() == _Symbol && ExtPosition.Magic() == InpMagicNumber)
         {
            if(ExtPosition.PositionType() == POSITION_TYPE_BUY)
               hasBuyPosition = true;
            if(ExtPosition.PositionType() == POSITION_TYPE_SELL)
               hasSellPosition = true;
            openTicket = ExtPosition.Ticket();
         }
      }
   }

   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   double tpPoints = (currentPrice * stdDev * MathSqrt((double)InpProjectionBars) * InpTakeProfitSigma);
   double slPoints = (currentPrice * stdDev * MathSqrt((double)InpProjectionBars) * InpStopLossSigma);

   // Minimum stop loss safety clamp (at least 20 pips)
   double minSafety = 200 * point;
   if(tpPoints < minSafety) tpPoints = minSafety * 2.0;
   if(slPoints < minSafety) slPoints = minSafety;

   // Guard 1: Spread Filter (Protects against News Spikes & Illiquid Rollovers)
   if(InpUseSpreadGuard && InpMaxSpreadPoints > 0)
   {
      long currentSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
      if(currentSpread > InpMaxSpreadPoints)
      {
         return;
      }
   }

   // Guard 2: Session Timing Filter (Focus on High-Liquidity Windows)
   if(InpUseSessionFilter)
   {
      MqlDateTime dt;
      TimeToStruct(TimeCurrent(), dt);
      if(InpSessionStartHour <= InpSessionEndHour)
      {
         if(dt.hour < InpSessionStartHour || dt.hour >= InpSessionEndHour)
            return;
      }
      else
      {
         if(dt.hour < InpSessionStartHour && dt.hour >= InpSessionEndHour)
            return;
      }
   }

   // Criteria 1: BULLISH REGIME BREAKOUT
   if(driftBps >= InpMinDriftBps && confidence >= InpMinConfidence)
   {
      if(!hasBuyPosition)
      {
         // Close opposing sell if active
         if(hasSellPosition)
            ExtTrade.PositionClose(openTicket);

         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double sl  = NormalizeDouble(ask - slPoints, digits);
         double tp  = NormalizeDouble(ask + tpPoints, digits);

         if(ExtTrade.Buy(InpLotSize, _Symbol, ask, sl, tp, "XPredictor Bullish Cone"))
         {
            PrintFormat("[XPredictor] BUY Executed @ %.*f | Conf: %.1f%% | Drift: +%.1f bps | SL: %.*f | TP: %.*f",
                        digits, ask, confidence, driftBps, digits, sl, digits, tp);
         }
      }
   }
   // Criteria 2: BEARISH REGIME BREAKDOWN
   else if(driftBps <= -InpMinDriftBps && confidence >= InpMinConfidence)
   {
      if(!hasSellPosition)
      {
         // Close opposing buy if active
         if(hasBuyPosition)
            ExtTrade.PositionClose(openTicket);

         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         double sl  = NormalizeDouble(bid + slPoints, digits);
         double tp  = NormalizeDouble(bid - tpPoints, digits);

         if(ExtTrade.Sell(InpLotSize, _Symbol, bid, sl, tp, "XPredictor Bearish Cone"))
         {
            PrintFormat("[XPredictor] SELL Executed @ %.*f | Conf: %.1f%% | Drift: %.1f bps | SL: %.*f | TP: %.*f",
                        digits, bid, confidence, driftBps, digits, sl, digits, tp);
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Draw visual Reality Cone on the MT5 Chart                        |
//+------------------------------------------------------------------+
void UpdateChartCone(datetime startTime, double startPrice, double upper, double lower, double mean, double driftBps, double confidence)
{
   int periodSec = PeriodSeconds(_Period);
   datetime endTime = startTime + (periodSec * InpProjectionBars);

   // 1. Upper Quantile Line (+2.1σ)
   string upperName = ExtPrefix + "UpperCone";
   if(ObjectFind(0, upperName) < 0)
   {
      ObjectCreate(0, upperName, OBJ_TREND, 0, startTime, startPrice, endTime, upper);
      ObjectSetInteger(0, upperName, OBJPROP_COLOR, InpConeColor);
      ObjectSetInteger(0, upperName, OBJPROP_STYLE, STYLE_DASH);
      ObjectSetInteger(0, upperName, OBJPROP_WIDTH, 2);
      ObjectSetInteger(0, upperName, OBJPROP_RAY_RIGHT, false);
   }
   else
   {
      ObjectMove(0, upperName, 0, startTime, startPrice);
      ObjectMove(0, upperName, 1, endTime, upper);
   }

   // 2. Lower Quantile Line (-2.1σ)
   string lowerName = ExtPrefix + "LowerCone";
   if(ObjectFind(0, lowerName) < 0)
   {
      ObjectCreate(0, lowerName, OBJ_TREND, 0, startTime, startPrice, endTime, lower);
      ObjectSetInteger(0, lowerName, OBJPROP_COLOR, InpConeColor);
      ObjectSetInteger(0, lowerName, OBJPROP_STYLE, STYLE_DASH);
      ObjectSetInteger(0, lowerName, OBJPROP_WIDTH, 2);
      ObjectSetInteger(0, lowerName, OBJPROP_RAY_RIGHT, false);
   }
   else
   {
      ObjectMove(0, lowerName, 0, startTime, startPrice);
      ObjectMove(0, lowerName, 1, endTime, lower);
   }

   // 3. Deterministic Mean Vector Line (E[P])
   string meanName = ExtPrefix + "MeanVector";
   if(ObjectFind(0, meanName) < 0)
   {
      ObjectCreate(0, meanName, OBJ_TREND, 0, startTime, startPrice, endTime, mean);
      ObjectSetInteger(0, meanName, OBJPROP_COLOR, InpMeanColor);
      ObjectSetInteger(0, meanName, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, meanName, OBJPROP_WIDTH, 3);
      ObjectSetInteger(0, meanName, OBJPROP_RAY_RIGHT, false);
   }
   else
   {
      ObjectMove(0, meanName, 0, startTime, startPrice);
      ObjectMove(0, meanName, 1, endTime, mean);
   }

   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| Create Institutional Dashboard HUD on MT5 Chart                  |
//+------------------------------------------------------------------+
void CreateChartDashboard()
{
   string bgName = ExtPrefix + "HUD_BG";
   if(ObjectFind(0, bgName) < 0)
   {
      ObjectCreate(0, bgName, OBJ_RECTANGLE_LABEL, 0, 0, 0);
      ObjectSetInteger(0, bgName, OBJPROP_XDISTANCE, 20);
      ObjectSetInteger(0, bgName, OBJPROP_YDISTANCE, 30);
      ObjectSetInteger(0, bgName, OBJPROP_XSIZE, 280);
      ObjectSetInteger(0, bgName, OBJPROP_YSIZE, 195);
      ObjectSetInteger(0, bgName, OBJPROP_BGCOLOR, C'250,245,238'); // Sahara Linen background
      ObjectSetInteger(0, bgName, OBJPROP_BORDER_COLOR, C'194,101,42'); // Terracotta
      ObjectSetInteger(0, bgName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, bgName, OBJPROP_BACK, false);
   }

   string titleName = ExtPrefix + "HUD_Title";
   if(ObjectFind(0, titleName) < 0)
   {
      ObjectCreate(0, titleName, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, titleName, OBJPROP_XDISTANCE, 30);
      ObjectSetInteger(0, titleName, OBJPROP_YDISTANCE, 40);
      ObjectSetInteger(0, titleName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, titleName, OBJPROP_COLOR, C'58,48,42');
      ObjectSetString(0, titleName, OBJPROP_FONT, "Lucida Console");
      ObjectSetInteger(0, titleName, OBJPROP_FONTSIZE, 10);
      ObjectSetString(0, titleName, OBJPROP_TEXT, "XPREDICTOR INSTITUTIONAL v4.8");
   }

   for(int i = 1; i <= 7; i++)
   {
      string lineName = ExtPrefix + "HUD_Line_" + IntegerToString(i);
      if(ObjectFind(0, lineName) < 0)
      {
         ObjectCreate(0, lineName, OBJ_LABEL, 0, 0, 0);
         ObjectSetInteger(0, lineName, OBJPROP_XDISTANCE, 30);
         ObjectSetInteger(0, lineName, OBJPROP_YDISTANCE, 45 + (i * 20));
         ObjectSetInteger(0, lineName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
         ObjectSetInteger(0, lineName, OBJPROP_COLOR, C'58,48,42');
         ObjectSetString(0, lineName, OBJPROP_FONT, "Lucida Console");
         ObjectSetInteger(0, lineName, OBJPROP_FONTSIZE, 9);
      }
   }
}

//+------------------------------------------------------------------+
//| Update Dashboard Text Values in Real Time                        |
//+------------------------------------------------------------------+
void UpdateDashboard(double driftBps, double confidence, double annualizedIV, double upper, double lower, double mean)
{
   int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);

   string signalText = "NEUTRAL (Watching)";
   color signalColor = C'120,112,106';

   if(confidence >= InpMinConfidence)
   {
      if(driftBps >= InpMinDriftBps)
      {
         signalText = "CONFIRMED BUY SIGNAL";
         signalColor = C'5,150,105'; // Emerald green
      }
      else if(driftBps <= -InpMinDriftBps)
      {
         signalText = "CONFIRMED SELL SIGNAL";
         signalColor = C'225,29,72'; // Crimson red
      }
   }

   ObjectSetString(0, ExtPrefix + "HUD_Line_1", OBJPROP_TEXT, StringFormat("Confidence  : %.1f%%", confidence));
   ObjectSetString(0, ExtPrefix + "HUD_Line_2", OBJPROP_TEXT, StringFormat("Regime Drift: %+.1f bps", driftBps));
   ObjectSetString(0, ExtPrefix + "HUD_Line_3", OBJPROP_TEXT, StringFormat("Implied IV  : %.2f%%", annualizedIV));
   ObjectSetString(0, ExtPrefix + "HUD_Line_4", OBJPROP_TEXT, StringFormat("Target E[P] : %.*f", digits, mean));
   ObjectSetString(0, ExtPrefix + "HUD_Line_5", OBJPROP_TEXT, StringFormat("Signal      : %s", signalText));
   ObjectSetInteger(0, ExtPrefix + "HUD_Line_5", OBJPROP_COLOR, signalColor);

   // Line 6: Session Window
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   bool inSession = true;
   if(InpUseSessionFilter)
   {
      if(InpSessionStartHour <= InpSessionEndHour)
         inSession = (dt.hour >= InpSessionStartHour && dt.hour < InpSessionEndHour);
      else
         inSession = !(dt.hour < InpSessionStartHour && dt.hour >= InpSessionEndHour);
   }
   string sessionStr = InpUseSessionFilter ? StringFormat("Session     : %02d:00-%02d:00 %s", InpSessionStartHour, InpSessionEndHour, inSession ? "[ACTIVE]" : "[PAUSED]") : "Session     : 24/5 All Sessions";
   color sessionCol = inSession ? C'5,150,105' : C'180,83,9';
   ObjectSetString(0, ExtPrefix + "HUD_Line_6", OBJPROP_TEXT, sessionStr);
   ObjectSetInteger(0, ExtPrefix + "HUD_Line_6", OBJPROP_COLOR, sessionCol);

   // Line 7: Spread Guard
   long spreadPts = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   bool spreadBlocked = (InpUseSpreadGuard && InpMaxSpreadPoints > 0 && spreadPts > InpMaxSpreadPoints);
   string spreadStr = StringFormat("Spread      : %d pts %s", (int)spreadPts, spreadBlocked ? "[BLOCKED]" : "[OK]");
   color spreadCol = spreadBlocked ? C'225,29,72' : C'58,48,42';
   ObjectSetString(0, ExtPrefix + "HUD_Line_7", OBJPROP_TEXT, spreadStr);
   ObjectSetInteger(0, ExtPrefix + "HUD_Line_7", OBJPROP_COLOR, spreadCol);
}
//+------------------------------------------------------------------+
