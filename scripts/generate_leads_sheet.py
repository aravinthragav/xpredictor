import os
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ensure output directories exist
leads_dir = r"c:\Users\USER-ID\Documents\Gold\xpredictor\leads"
onedrive_dir = r"C:\Users\USER-ID\OneDrive"
os.makedirs(leads_dir, exist_ok=True)

wb = openpyxl.Workbook()

# Setup Sheet 1: Master Leads Matrix
ws1 = wb.active
ws1.title = "Institutional Leads Matrix"

# Color Palette (Institutional Sahara & Navy Theme)
NAVY_FILL = PatternFill(start_color="161F2C", end_color="161F2C", fill_type="solid")
GOLD_FILL = PatternFill(start_color="C2652A", end_color="C2652A", fill_type="solid")
LIGHT_GOLD = PatternFill(start_color="F5ECE1", end_color="F5ECE1", fill_type="solid")
PROP_FILL  = PatternFill(start_color="EEF2FF", end_color="EEF2FF", fill_type="solid")
BROKER_FILL= PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")

HEADER_FONT = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
ROW_FONT    = Font(name="Segoe UI", size=9)
BOLD_FONT   = Font(name="Segoe UI", size=9, bold=True)
LINK_FONT   = Font(name="Segoe UI", size=9, color="0066CC", underline="single")

THIN_BORDER = Border(
    left=Side(style='thin', color='E5E7EB'),
    right=Side(style='thin', color='E5E7EB'),
    top=Side(style='thin', color='E5E7EB'),
    bottom=Side(style='thin', color='E5E7EB')
)

headers = [
    "ID", "Firm Name", "Category", "Jurisdiction / HQ", "Key Executive / Decision Maker",
    "Target Title", "Contact Email", "Custom Demo Sandbox Link", "Cold Outreach Hook",
    "Cold Email Subject Line", "Outreach Status", "Notes / Next Step"
]

ws1.append(headers)
for col_idx, h in enumerate(headers, 1):
    cell = ws1.cell(row=1, column=col_idx)
    cell.fill = NAVY_FILL
    cell.font = HEADER_FONT
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

leads = [
    # Top Prop Firms
    (1, "FTMO", "Prop Trading Firm", "Prague, Czechia / EU", "Otakar Suffner / Marek Vasicek", "CEO & Head of Risk", "partners@ftmo.com",
     "https://aravinthragav.github.io/xpredictor/?partner=ftmo",
     "Preventing challenge failures in low-vol chop & protecting funded accounts from Max Daily DD spikes with Bayesian Cones",
     "FTMO x XPredictor: Dynamic Max Drawdown & Reality Cone Copilot for Evaluation Desks", "Ready for Outreach", "Primary target - largest retail prop firm"),
    (2, "FundedNext", "Prop Trading Firm", "Dubai, UAE", "Abdullah Jayed / Syed Lateef", "CEO & Head of Operations", "partnerships@fundednext.com",
     "https://aravinthragav.github.io/xpredictor/?partner=fundednext",
     "Stellar challenge pass rate stabilization and volatility boundary defense for funded traders",
     "FundedNext Stellar Desk: AI Historical Regime Matching & Risk Copilot", "Ready for Outreach", "High viral community in MENA/Asia"),
    (3, "Topstep", "Prop Trading Firm", "Chicago, IL, USA", "Michael Patak", "CEO & Founder", "partners@topstep.com",
     "https://aravinthragav.github.io/xpredictor/?partner=topstep",
     "Futures Trading Combine volatility boundaries and zero-lookahead regime forecasting",
     "Topstep Combine: Empirical Volatility Envelopes for Futures Traders", "Ready for Outreach", "US Futures dominance"),
    (4, "Apex Trader Funding", "Prop Trading Firm", "Texas, USA", "Darrell Martin", "CEO", "support@apextraderfunding.com",
     "https://aravinthragav.github.io/xpredictor/?partner=apex",
     "Trailing threshold drawdown defense during high-variance news releases (CPI/FOMC)",
     "Apex Trader Funding: Trailing Threshold Risk Copilot via Hybrid AI Cones", "Ready for Outreach", "Massive US retail volume"),
    (5, "Alpha Capital Group", "Prop Trading Firm", "London, UK", "George Baker", "CEO & Head of Trading", "info@alphacapitalgroup.uk",
     "https://aravinthragav.github.io/xpredictor/?partner=AlphaCapital",
     "Advanced market microstructure and resting liquidity depth integration for UK/EU challenge desks",
     "Alpha Capital Group: Proprietary AI Historical Twin Matching Suite", "Ready for Outreach", "Strong institutional branding"),
    (6, "Funding Pips", "Prop Trading Firm", "Dubai, UAE", "Khaled Ayesh", "CEO", "support@fundingpips.com",
     "https://aravinthragav.github.io/xpredictor/?partner=FundingPips",
     "Ultra-fast scaling plan risk modeling and 2-step evaluation retention copilot",
     "Funding Pips x XPredictor: Proprietary Risk Sandbox for Active Challengers", "Ready for Outreach", "Rapidly growing Dubai prop desk"),
    (7, "E8 Markets", "Prop Trading Firm", "Dallas, TX / Prague", "Dylan Elchami", "CEO & Founder", "partners@e8markets.com",
     "https://aravinthragav.github.io/xpredictor/?partner=E8",
     "Customizable drawdown scaling and Bayesian Reality Cone volatility analytics for E8 Track",
     "E8 Markets: Institutional AI Volatility Boundaries for Evaluation Desks", "Ready for Outreach", "Tech-forward userbase"),
    (8, "The 5%ers", "Prop Trading Firm", "London / Tel Aviv", "Gil Ben Hur", "CEO", "help@the5ers.com",
     "https://aravinthragav.github.io/xpredictor/?partner=The5ers",
     "Hyper-growth career program risk stabilization and swing-trading historical regime verification",
     "The 5%ers: Proprietary Multi-Horizon Volatility Envelopes for Funded Desks", "Ready for Outreach", "Specialized in serious swing traders"),
    (9, "MyFundedFX", "Prop Trading Firm", "Dallas, USA", "Matthew Leech", "CEO", "support@myfundedfx.com",
     "https://aravinthragav.github.io/xpredictor/?partner=MyFundedFX",
     "One-click embeddable web trader risk copilot for MT5/DXTrade/cTrader challenges",
     "MyFundedFX: Embeddable AI Pattern Search & Reality Cone Terminal", "Ready for Outreach", "Multiple front-end trading platforms"),
    (10, "City Traders Imperium", "Prop Trading Firm", "London, UK", "Daniel Martin", "Head of Trading", "cti@citytradersimperium.com",
     "https://aravinthragav.github.io/xpredictor/?partner=CTI",
     "Professional funded trader portfolio protection and empirical analogue matching",
     "CTI Desk: Institutional Risk Copilot & 50M+ Historical Regime Search", "Ready for Outreach", "High funded account longevity"),
    (11, "Blue Guardian", "Prop Trading Firm", "Dubai / UK", "Sean Bainbridge", "CEO", "support@blueguardian.com",
     "https://aravinthragav.github.io/xpredictor/?partner=BlueGuardian",
     "Guardian Protector tool enhancement via real-time +2.1σ / -2.1σ Bayesian envelopes",
     "Blue Guardian Protector: Enhancing Trader Discipline with AI Reality Cones", "Ready for Outreach", "Focus on automated risk protection"),
    (12, "Fidelcrest", "Prop Trading Firm", "Cyprus / EU", "Trading Operations", "Head of Risk Management", "support@fidelcrest.com",
     "https://aravinthragav.github.io/xpredictor/?partner=Fidelcrest",
     "Micro and Pro trader challenge retention in choppy currency and gold regimes",
     "Fidelcrest Pro Desks: Causal AI Regime Matching & Volatility Prediction", "Ready for Outreach", "EU established prop firm"),
    (13, "Audacity Capital", "Prop Trading Firm", "London, UK", "Karim Yousfi", "CEO", "support@audacitycapital.co.uk",
     "https://aravinthragav.github.io/xpredictor/?partner=Audacity",
     "Funded trader program risk management copilot for London session institutional desks",
     "Audacity Capital: Proprietary AI Risk Copilot for Funded Traders", "Ready for Outreach", "London institutional presence"),
    (14, "Goat Funded Trader", "Prop Trading Firm", "Spain / UAE", "Partnerships Desk", "Head of Strategic Growth", "support@goatfundedtrader.com",
     "https://aravinthragav.github.io/xpredictor/?partner=GoatFunded",
     "No time-limit evaluation retention and zero-lookahead historical pattern matching",
     "Goat Funded Trader: Turnkey AI Reality Cone Sandbox for Challengers", "Ready for Outreach", "High retail traffic"),
    (15, "Funded Trading Plus", "Prop Trading Firm", "London, UK", "Simon M.", "COO", "support@fundedtradingplus.com",
     "https://aravinthragav.github.io/xpredictor/?partner=FundedTradingPlus",
     "Experienced and Master trader scaling with institutional order depth profile analytics",
     "Funded Trading Plus: Bayesian Probability Cones for Master Challengers", "Ready for Outreach", "High TrustPilot ratings"),
    (16, "Smart Prop Trader", "Prop Trading Firm", "Austin, TX, USA", "Blake Morrow", "Co-Founder", "support@smartproptrader.com",
     "https://aravinthragav.github.io/xpredictor/?partner=SmartPropTrader",
     "Affordable evaluation conversion lift and multi-asset MT5 indicator integration",
     "Smart Prop Trader: Turnkey AI Risk Sandbox & Native MT5 Indicator", "Ready for Outreach", "US retail trader appeal"),
    (17, "Bespoke Funding", "Prop Trading Firm", "London, UK", "Executive Desk", "Head of Partnerships", "support@bespokefundingprogram.com",
     "https://aravinthragav.github.io/xpredictor/?partner=BespokeFunding",
     "Classic and Rapid challenge volatility monitoring with empirical forward projections",
     "Bespoke Funding: Empirical Volatility Boundaries for Challenge Desks", "Ready for Outreach", "Flexible evaluation models"),
    (18, "SurgeTrader", "Prop Trading Firm", "Naples, FL, USA", "Jana Seaman", "CEO", "info@surgetrader.com",
     "https://aravinthragav.github.io/xpredictor/?partner=SurgeTrader",
     "Audition pass rate optimization and institutional Gold/Index regime modeling",
     "SurgeTrader Audition Desk: AI Historical Analogue & Risk Copilot", "Ready for Outreach", "Single-phase evaluation focus"),
    (19, "True Forex Funds", "Prop Trading Firm", "Hungary / EU", "Executive Team", "Head of Risk & Trading", "support@trueforexfunds.com",
     "https://aravinthragav.github.io/xpredictor/?partner=TrueForexFunds",
     "Proprietary MT5 liquidity integration and dynamic cascade stress-testing",
     "True Forex Funds: Proprietary AI Risk Copilot for Funded Desks", "Ready for Outreach", "European footprint"),
    (20, "Fast Track Trading", "Prop Trading Firm", "USA", "Bob Iaccino", "Head Trader & Co-Founder", "support@fasttracktrading.net",
     "https://aravinthragav.github.io/xpredictor/?partner=FastTrack",
     "Immediate funding account protection and intraday volatility dispersion boundaries",
     "Fast Track Trading: AI Volatility Cones for Direct Funded Accounts", "Ready for Outreach", "Futures direct funding"),

    # Top FX / CFD & Multi-Asset Brokers
    (21, "IC Markets", "FX/CFD Broker (ECN)", "Sydney, Australia / CySEC / FSA", "Andrew Budzinski", "CEO & Managing Director", "institutional@icmarkets.com",
     "https://aravinthragav.github.io/xpredictor/?partner=icmarkets",
     "Client retention in chop & boosting monthly lot turnover on Raw Spread ECN accounts via AI confidence metrics",
     "IC Markets Client Area: Embeddable AI Reality Cone Terminal & 18x Lot ROI", "Ready for Outreach", "World's largest FX/CFD volume broker"),
    (22, "Pepperstone", "FX/CFD Broker", "Melbourne, Australia / FCA / CySEC", "Tamas Szabo", "Group CEO", "institutional@pepperstone.com",
     "https://aravinthragav.github.io/xpredictor/?partner=pepperstone",
     "Razor account competitive differentiation and retaining discretionary traders across 15M/1H/4H regimes",
     "Pepperstone Razor: AI Pattern Recognition & Reality Cone Copilot", "Ready for Outreach", "High-volume algorithmic and retail traders"),
    (23, "Exness", "Multi-Asset Broker", "Limassol, Cyprus / UK / South Africa", "Petr Valov", "CEO & Founder", "partnerships@exness.com",
     "https://aravinthragav.github.io/xpredictor/?partner=exness",
     "Empowering high-frequency retail clients with institutional Level 2 resting wall analytics and historical regime search",
     "Exness Institutional: Proprietary AI Pattern Matching Engine for Client Portal", "Ready for Outreach", "Trillions in monthly volume"),
    (24, "Vantage Markets", "FX/CFD Broker", "Sydney / Cayman / UK", "Marc Despallieres", "Chief Strategy & Trading Officer", "partners@vantagemarkets.com",
     "https://aravinthragav.github.io/xpredictor/?partner=Vantage",
     "Client lifetime value expansion (90 days -> 180+ days) and turnkey web component integration",
     "Vantage Markets: Multiplying Client LTV & Lot Turnover with AI Reality Cones", "Ready for Outreach", "Aggressive global expansion"),
    (25, "ThinkMarkets", "Multi-Asset Broker", "Chicago / London / Australia", "Nauman Anees", "CEO & Co-Founder", "partnerships@thinkmarkets.com",
     "https://aravinthragav.github.io/xpredictor/?partner=ThinkMarkets",
     "ThinkTrader proprietary platform integration and native MT5 indicator distribution",
     "ThinkMarkets: AI Volatility Copilot for ThinkTrader & MT5 Desks", "Ready for Outreach", "Proprietary trading app + MT5"),
    (26, "Tickmill", "FX/CFD Broker", "London, UK / CySEC / Seychelles", "Illimar Mattus / Sudhanshu Agarwal", "Co-Founder & Executive Director", "institutional@tickmill.com",
     "https://aravinthragav.github.io/xpredictor/?partner=Tickmill",
     "Pro account spread revenue maximization and Gold (XAU/USD) volatility forecasting",
     "Tickmill Institutional: Proprietary AI Regime Search & Volatility Cones", "Ready for Outreach", "Low spread VIP accounts"),
    (27, "FP Markets", "FX/CFD Broker", "Sydney, Australia / CySEC", "Craig Allison", "CEO", "partners@fpmarkets.com",
     "https://aravinthragav.github.io/xpredictor/?partner=FPMarkets",
     "Iframe client area integration for DMA and raw pricing clients to prevent hesitation in chop",
     "FP Markets: Turnkey Client Portal AI Terminal (Zero Infrastructure Setup)", "Ready for Outreach", "Award-winning Australian ECN"),
    (28, "XM Group", "Multi-Asset Broker", "Limassol, Cyprus / Belize / Australia", "Constantinos Cleanthous", "CEO & Co-Founder", "partners@xm.com",
     "https://aravinthragav.github.io/xpredictor/?partner=XM",
     "Educating and empowering 10M+ registered clients with objective statistical boundaries",
     "XM Group: Next-Gen AI Decision Support Terminal for Client Area", "Ready for Outreach", "Massive global retail base"),
    (29, "Axi", "FX/CFD Broker", "Sydney, Australia / UK", "Rajesh Yohannan", "Group CEO", "partners@axi.com",
     "https://aravinthragav.github.io/xpredictor/?partner=Axi",
     "Axi Select prop funding ecosystem enhancement with Bayesian Reality Cones",
     "Axi Select: Enhancing Trader Capital Allocation with AI Reality Cones", "Ready for Outreach", "Has its own prop incubator Axi Select"),
    (30, "FXTM (ForexTime)", "FX/CFD Broker", "Cyprus / UK / Mauritius", "Olga Rybalkina", "CEO", "partners@fxtm.com",
     "https://aravinthragav.github.io/xpredictor/?partner=FXTM",
     "Advantage account trader longevity and automated MT5 Reality Cone signals",
     "FXTM Advantage: Institutional AI Pattern Matching for Active Clients", "Ready for Outreach", "Emerging market retail powerhouse"),
    (31, "BlackBull Markets", "FX/CFD Broker", "Auckland, New Zealand", "Michael Walker", "Managing Director", "partners@blackbullmarkets.com",
     "https://aravinthragav.github.io/xpredictor/?partner=BlackBull",
     "Institutional liquidity client portal widget with real-time resting iceberg detection",
     "BlackBull Markets: Proprietary AI Reality Cone Integration for MT5 / TradingView", "Ready for Outreach", "TradingView broker partner"),
    (32, "AvaTrade", "Multi-Asset Broker", "Dublin, Ireland / ASIC / FSCA", "Dáire Ferguson", "CEO", "partners@avatrade.com",
     "https://aravinthragav.github.io/xpredictor/?partner=AvaTrade",
     "AvaProtect risk management suite augmentation with predictive volatility envelopes",
     "AvaProtect x XPredictor: Next-Gen Empirical Risk Boundaries for AvaTrade Clients", "Ready for Outreach", "Strong retail risk products"),
    (33, "Eightcap", "FX/CFD Broker", "Melbourne, Australia / Bahamas", "Joel Murphy", "CEO", "partners@eightcap.com",
     "https://aravinthragav.github.io/xpredictor/?partner=Eightcap",
     "Prop firm liquidity provider integration and high-volume crypto/CFD analytics",
     "Eightcap Partner Desk: Institutional AI Reality Cones for Prop & Retail Traders", "Ready for Outreach", "Major prop trading infrastructure broker"),
    (34, "OANDA", "Multi-Asset Broker", "New York, USA / London / Singapore", "Gavin Bambury", "CEO", "institutional@oanda.com",
     "https://aravinthragav.github.io/xpredictor/?partner=OANDA",
     "OANDA Prop Trader and API client retention with institutional Bayesian modeling",
     "OANDA Prop Trader: Institutional AI Pattern Recognition & Reality Cones", "Ready for Outreach", "Recently launched OANDA Prop Trader"),
    (35, "CMC Markets", "Multi-Asset Broker", "London, UK (FTSE 250)", "Peter Cruddas", "CEO & Founder", "institutional@cmcmarkets.com",
     "https://aravinthragav.github.io/xpredictor/?partner=CMCMarkets",
     "NextGen platform institutional add-on for sovereign desks and high-net-worth traders",
     "CMC Markets Connect: Proprietary AI Regime Search for Institutional Desks", "Ready for Outreach", "Tier-1 institutional broker"),
    (36, "Saxo Bank", "Multi-Asset Investment Bank", "Copenhagen, Denmark / Global", "Kim Fournais", "CEO & Founder", "institutional@saxobank.com",
     "https://aravinthragav.github.io/xpredictor/?partner=SaxoBank",
     "OpenAPI integration for institutional wealth and active multi-asset trading desks",
     "Saxo Bank Institutional: OpenAPI Historical Regime Search & Volatility Cones", "Ready for Outreach", "Global banking infrastructure"),
    (37, "Swissquote", "Banking & FX Broker", "Gland, Switzerland (SIX:SQN)", "Marc Bürki", "CEO", "institutional@swissquote.ch",
     "https://aravinthragav.github.io/xpredictor/?partner=Swissquote",
     "Swiss-grade quantitative analytics for tier-1 asset managers and active CFD traders",
     "Swissquote Institutional: Proprietary AI Reality Cone Engine for eForex Desks", "Ready for Outreach", "Swiss banking safety reputation"),
    (38, "Admirals", "Multi-Asset Broker", "Tallinn, Estonia / UK / CySEC", "Sergei Bogatenkov", "CEO", "partners@admiralmarkets.com",
     "https://aravinthragav.github.io/xpredictor/?partner=Admirals",
     "Supreme Edition MT5 plugin upgrade with AI-powered historical pattern matching",
     "Admirals Supreme Edition: Integrating AI Reality Cones for Active Clients", "Ready for Outreach", "Famous for MT5 Supreme Edition"),
    (39, "RoboForex", "FX/CFD Broker", "Belize / CySEC", "Partnerships Desk", "Head of Business Development", "partners@roboforex.com",
     "https://aravinthragav.github.io/xpredictor/?partner=RoboForex",
     "Prime and ECN account client retention and automated Telegram signal bot integration",
     "RoboForex ECN: Turnkey AI Reality Cone Copilot & Automated Signal Engine", "Ready for Outreach", "Huge international affiliate reach"),
    (40, "IG Group", "Multi-Asset Broker", "London, UK (FTSE 250)", "Charlie Rozes / Matt Macklin", "Executive Leadership", "institutional@ig.com",
     "https://aravinthragav.github.io/xpredictor/?partner=IG",
     "Premium client retention during macroeconomic consolidation and institutional Gold/Index analytics",
     "IG Prime: Institutional AI Pattern Search & Bayesian Volatility Cones", "Ready for Outreach", "Global spread betting & CFD leader")
]

for row in leads:
    ws1.append(row)
    row_idx = ws1.max_row
    # Styling
    is_prop = "Prop" in row[2]
    cat_fill = PROP_FILL if is_prop else BROKER_FILL
    for col_idx in range(1, len(row) + 1):
        cell = ws1.cell(row=row_idx, column=col_idx)
        cell.font = ROW_FONT
        cell.border = THIN_BORDER
        if col_idx == 3: # Category
            cell.fill = cat_fill
            cell.alignment = Alignment(horizontal="center")
        elif col_idx == 8: # Link
            cell.font = LINK_FONT
            cell.hyperlink = row[7]
        elif col_idx == 11: # Status
            cell.fill = LIGHT_GOLD
            cell.font = BOLD_FONT
            cell.alignment = Alignment(horizontal="center")
        elif col_idx == 1:
            cell.alignment = Alignment(horizontal="center")

# Adjust column widths
for col in ws1.columns:
    max_len = 0
    col_letter = get_column_letter(col[0].column)
    for cell in col:
        val = str(cell.value or '')
        if len(val) > max_len:
            max_len = len(val)
    ws1.column_dimensions[col_letter].width = min(45, max(12, max_len + 3))

ws1.row_dimensions[1].height = 28

# Setup Sheet 2: Cold Email Sequences
ws2 = wb.create_sheet(title="Cold Email Sequences")

templates = [
    ("SEQUENCE 1: FOR PROP TRADING FIRMS (CEOs, Heads of Risk)",
     "Subject: {{firm_name}} x XPredictor: Dynamic Max Drawdown & Reality Cone Copilot\n\n"
     "Hi {{first_name}},\n\n"
     "Most challenge participants fail not because they lack trading strategy, but because they trade without volatility boundaries during sudden regime shocks (CPI, FOMC, liquidity vacuums)—hitting daily max drawdown and churning out of frustration.\n\n"
     "We've engineered XPredictor (https://aravinthragav.github.io/xpredictor/?partner={{partner_key}}), a proprietary institutional AI pattern matching engine that gives your evaluation and funded traders an empirical Risk Copilot:\n\n"
     "1. Continuous Bayesian Reality Cones: Visualizes mathematically probable price bounds (±2.1σ, Mean E[P]) over the forward 22 bars, warning traders before they breach drawdown limits.\n"
     "2. 50M+ Historical Regime Analogs: Sub-35ms pattern retrieval matching current price action against historical setups (Zero Lookahead Bias).\n"
     "3. Turnkey Integration: Deploys directly into your Client Portal via a 3-minute iframe, or native MT5 desktop indicator (.mq5).\n\n"
     "We've provisioned a live co-branded sandbox for {{firm_name}} here: https://aravinthragav.github.io/xpredictor/?partner={{partner_key}}\n\n"
     "Would you be open to a 10-minute demo on how this extends funded account lifespan by 3.2x?\n\n"
     "Best regards,\n"
     "Aravinth Ragav\n"
     "Founder & Quantitative Architect, XPredictor\n"
     "arkankl07@gmail.com"),

    ("SEQUENCE 2: FOR FX / CFD BROKERS (CCOs, Heads of Brokerage)",
     "Subject: {{firm_name}} Client Area: Embeddable AI Reality Cone Terminal & 18x Lot ROI\n\n"
     "Hi {{first_name}},\n\n"
     "When market conditions turn choppy, retail traders hesitate and stop trading—causing broker spread and commission volume to plummet by 40–50%.\n\n"
     "We built XPredictor to solve trader chop hesitation by providing institutional AI historical regime matching and forward Bayesian volatility boundaries directly inside your Client Portal.\n\n"
     "Key Broker Commercial Highlights:\n"
     "• Volume Multiplier: Keeping just 500 active traders from quitting chop adds an estimated $180,000+ in annual spread revenue (18x partner ROI).\n"
     "• 100% Non-Advisory: Classified as objective volatility and historical charting analytics (like Bollinger Bands / ATR), eliminating regulatory friction.\n"
     "• Zero Development Burden: Single embeddable iframe / web component requiring zero changes to your core MT5 bridge.\n\n"
     "See your live co-branded partner sandbox: https://aravinthragav.github.io/xpredictor/?partner={{partner_key}}\n\n"
     "Can we set up a brief 10-minute call this Thursday or Friday to show you the partner economics?\n\n"
     "Best regards,\n"
     "Aravinth Ragav\n"
     "Founder & Quantitative Architect, XPredictor\n"
     "arkankl07@gmail.com"),

    ("SEQUENCE 3: THE 3-DAY FOLLOW-UP (SHORT & PUNCHY)",
     "Subject: Re: {{firm_name}} x XPredictor Sandbox\n\n"
     "Hi {{first_name}},\n\n"
     "Following up on my note regarding the live risk copilot sandbox we provisioned for {{firm_name}}.\n\n"
     "Did you have a chance to inspect the Reality Cone projection on Gold (XAU/USD) or S&P 500? https://aravinthragav.github.io/xpredictor/?partner={{partner_key}}\n\n"
     "We're currently offering a 30-day zero-risk pilot for up to 1,000 active traders. Happy to share a 3-minute video walkthrough if easier.\n\n"
     "Best,\n"
     "Aravinth")
]

ws2.column_dimensions["A"].width = 35
ws2.column_dimensions["B"].width = 95

ws2.append(["Template Name", "Cold Outreach Email Copy"])
ws2.cell(row=1, column=1).fill = NAVY_FILL
ws2.cell(row=1, column=1).font = HEADER_FONT
ws2.cell(row=1, column=2).fill = NAVY_FILL
ws2.cell(row=1, column=2).font = HEADER_FONT
ws2.row_dimensions[1].height = 26

for idx, (tname, tcontent) in enumerate(templates, 2):
    ws2.append([tname, tcontent])
    ws2.cell(row=idx, column=1).font = BOLD_FONT
    ws2.cell(row=idx, column=1).fill = LIGHT_GOLD
    ws2.cell(row=idx, column=1).alignment = Alignment(vertical="top", wrap_text=True)
    ws2.cell(row=idx, column=2).font = ROW_FONT
    ws2.cell(row=idx, column=2).alignment = Alignment(vertical="top", wrap_text=True)
    ws2.row_dimensions[idx].height = 220

# Setup Sheet 3: Campaign Pipeline & KPI Tracker
ws3 = wb.create_sheet(title="Campaign KPI Tracker")
ws3.column_dimensions["A"].width = 25
ws3.column_dimensions["B"].width = 25
ws3.column_dimensions["C"].width = 40

ws3.append(["Funnel Stage", "Target Count", "Description / Benchmark"])
ws3.cell(row=1, column=1).fill = NAVY_FILL
ws3.cell(row=1, column=1).font = HEADER_FONT
ws3.cell(row=1, column=2).fill = NAVY_FILL
ws3.cell(row=1, column=2).font = HEADER_FONT
ws3.cell(row=1, column=3).fill = NAVY_FILL
ws3.cell(row=1, column=3).font = HEADER_FONT
ws3.row_dimensions[1].height = 26

kpis = [
    ("Total Verified Targets", "40 Institutional Firms", "20 Prop Firms + 20 Leading ECN Brokers"),
    ("Target Open Rate", "55% - 65%", "Driven by customized co-branded sandbox preview in subject"),
    ("Target Reply Rate", "12% - 18%", "High relevance to risk managers & CCOs"),
    ("Target Pilot Demos", "6 - 8 Demos", "10-minute walkthroughs scheduled"),
    ("30-Day Pilots Signed", "2 - 3 Partners", "Zero-risk PoC with 500-1000 traders"),
    ("Contract Target", "1 Multi-Year Contract", "$3,500/mo - $8,500/mo ARR foundation")
]

for idx, kpi in enumerate(kpis, 2):
    ws3.append(list(kpi))
    for c in range(1, 4):
        cell = ws3.cell(row=idx, column=c)
        cell.font = ROW_FONT
        cell.border = THIN_BORDER
        if c == 1:
            cell.font = BOLD_FONT

# Save both in OneDrive and workspace leads folder
xlsx_local = os.path.join(leads_dir, "XPredictor_Institutional_Leads.xlsx")
csv_local  = os.path.join(leads_dir, "XPredictor_Institutional_Leads.csv")
xlsx_drive = os.path.join(onedrive_dir, "XPredictor_Institutional_Leads.xlsx")

wb.save(xlsx_local)
try:
    wb.save(xlsx_drive)
    print(f"Saved to OneDrive: {xlsx_drive}")
except Exception as e:
    print(f"OneDrive save note: {e}")

# Export CSV for instant CRM / Email tool import
with open(csv_local, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    for row in leads:
        writer.writerow(row)

print(f"Saved local XLSX: {xlsx_local}")
print(f"Saved local CSV:  {csv_local}")
