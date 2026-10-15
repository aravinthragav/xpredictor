# scripts/run_weekend_sync.ps1
# One-click execution script for the XPredictor Weekend Batch Pipeline.
# Slices mature bars, computes +20b outcomes, generates 768-D embeddings, and refreshes the vector database.

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       XPredictor Weekend Batch Synchronization           " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$uvPath = "C:\Users\ragav\.local\bin\uv.exe"
if (-not (Test-Path $uvPath)) {
    $uvPath = "uv"
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location "$repoRoot"

Write-Host "`n[1/3] Checking Weekday Buffer Status..." -ForegroundColor Yellow
& $uvPath run python -c "from services.ingestion_worker.live_buffer import LiveMarketBuffer; b = LiveMarketBuffer(); print('Buffer status:', b.get_stats())"

Write-Host "`n[2/3] Running Batch Ingestion & Kronos Vectorization for Gold (XAUUSD 1H)..." -ForegroundColor Yellow
& $uvPath run python services/ingestion-worker/weekend_batch.py --symbol XAUUSD --timeframe 1h

Write-Host "`n[3/3] Running Batch Ingestion for Bitcoin (BTCUSD 1H)..." -ForegroundColor Yellow
& $uvPath run python services/ingestion-worker/weekend_batch.py --symbol BTCUSD --timeframe 1h

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  WEEKEND SYNC FINISHED. Vector DB ready for Monday open!  " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
