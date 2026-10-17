#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

//+------------------------------------------------------------------+
//| XPredictor Institutional Reality Cone for NinjaTrader 8 (Futures) |
//| Designed for Topstep, Apex Trader Funding, and CME/CBOT Traders  |
//+------------------------------------------------------------------+
namespace NinjaTrader.NinjaScript.Indicators
{
    public class XPredictorRealityCone : Indicator
    {
        private double sigmaClamped = 0.0035;
        private double macroDrift = 0.0;
        private string tagPrefix = "XP_Cone_";

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description                                 = @"XPredictor Institutional Bayesian Reality Cone for Futures Desks.";
                Name                                        = "XPredictorRealityCone";
                Calculate                                   = Calculate.OnBarClose;
                IsOverlay                                   = true;
                DisplayInDataBox                            = true;
                DrawOnPricePanel                            = true;
                PaintPriceMarkers                           = true;
                ScaleJustification                          = NinjaTrader.Gui.Chart.ScaleJustification.Right;
                IsSuspendedWhileInactive                    = true;

                PartnerKey                                  = "TOPSTEP_COMBINE_EDITION";
                ReferenceBars                               = 60;
                ForecastHorizon                             = 22;
                SigmaMultiplier                             = 2.10;

                UpperBandColor                              = Brushes.MediumSeaGreen;
                MeanVectorColor                             = Brushes.DarkGoldenrod;
                LowerBandColor                              = Brushes.Crimson;

                AddPlot(new Stroke(Brushes.MediumSeaGreen, 2), PlotStyle.Line, "P90Upper");
                AddPlot(new Stroke(Brushes.DarkGoldenrod, 2),  PlotStyle.Line, "MeanEP");
                AddPlot(new Stroke(Brushes.Crimson, 2),        PlotStyle.Line, "P10Lower");
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < ReferenceBars + 10)
                return;

            // 1. Calculate empirical log-returns volatility across reference window
            double sumR = 0;
            double[] rets = new double[ReferenceBars];
            for (int i = 0; i < ReferenceBars - 1; i++)
            {
                double p1 = Close[i];
                double p2 = Close[i + 1] > 0 ? Close[i + 1] : p1;
                double r = Math.Log(p1 / p2);
                rets[i] = r;
                sumR += r;
            }
            double meanR = sumR / (ReferenceBars - 1);
            double sumSq = 0;
            for (int i = 0; i < ReferenceBars - 1; i++)
            {
                sumSq += Math.Pow(rets[i] - meanR, 2);
            }
            double variance = sumSq / (ReferenceBars - 2);
            double sigmaLive = Math.Sqrt(variance) * Math.Sqrt(ForecastHorizon);
            sigmaClamped = Math.Max(0.0018, Math.Min(0.015, sigmaLive));

            // 2. Momentum drift
            double pStart = Open[ReferenceBars - 1] > 0 ? Open[ReferenceBars - 1] : Close[0];
            double brushedSlope = (Close[0] - pStart) / pStart;
            double trendSign = brushedSlope < -0.002 ? -1.0 : 1.0;
            macroDrift = trendSign * Math.Min(0.018, Math.Max(0.003, Math.Abs(brushedSlope) * 0.50));

            // 3. Assign terminal values
            double c0 = Close[0];
            double pUpper = c0 * (1.0 + macroDrift + SigmaMultiplier * sigmaClamped);
            double pMean  = c0 * (1.0 + macroDrift);
            double pLower = c0 * (1.0 + macroDrift - SigmaMultiplier * sigmaClamped);

            Values[0][0] = pUpper;
            Values[1][0] = pMean;
            Values[2][0] = pLower;

            // Draw forward visual rays on the most recent bar
            if (IsFirstTickOfBar)
            {
                Draw.Line(this, tagPrefix + "Upper", false, 0, c0, -ForecastHorizon, pUpper, UpperBandColor, DashStyleHelper.Dash, 1);
                Draw.Line(this, tagPrefix + "Mean",  false, 0, c0, -ForecastHorizon, pMean,  MeanVectorColor, DashStyleHelper.Solid, 2);
                Draw.Line(this, tagPrefix + "Lower", false, 0, c0, -ForecastHorizon, pLower, LowerBandColor, DashStyleHelper.Dash, 1);

                Draw.Text(this, tagPrefix + "LblP90", $"P90 (+2.1σ): {pUpper:F2}", -ForecastHorizon - 2, pUpper, UpperBandColor);
                Draw.Text(this, tagPrefix + "LblP50", $"MEAN E[P]: {pMean:F2}",  -ForecastHorizon - 2, pMean,  MeanVectorColor);
                Draw.Text(this, tagPrefix + "LblP10", $"P10 (-2.1σ): {pLower:F2}", -ForecastHorizon - 2, pLower, LowerBandColor);
            }
        }

        #region Properties
        [NinjaScriptProperty]
        [Display(Name="Partner Key", Order=1, GroupName="Partner Authentication")]
        public string PartnerKey { get; set; }

        [NinjaScriptProperty]
        [Range(20, 120)]
        [Display(Name="Reference Bars", Order=2, GroupName="Reality Cone Parameters")]
        public int ReferenceBars { get; set; }

        [NinjaScriptProperty]
        [Range(5, 50)]
        [Display(Name="Forecast Horizon (Bars)", Order=3, GroupName="Reality Cone Parameters")]
        public int ForecastHorizon { get; set; }

        [NinjaScriptProperty]
        [Range(1.0, 3.5)]
        [Display(Name="Sigma Multiplier (2.1 = 95%)", Order=4, GroupName="Reality Cone Parameters")]
        public double SigmaMultiplier { get; set; }

        [XmlIgnore]
        [Display(Name="Upper Band Color (+2.1σ)", Order=5, GroupName="Visuals")]
        public Brush UpperBandColor { get; set; }

        [XmlIgnore]
        [Display(Name="Mean Vector Color E[P]", Order=6, GroupName="Visuals")]
        public Brush MeanVectorColor { get; set; }

        [XmlIgnore]
        [Display(Name="Lower Band Color (-2.1σ)", Order=7, GroupName="Visuals")]
        public Brush LowerBandColor { get; set; }
        #endregion
    }
}
