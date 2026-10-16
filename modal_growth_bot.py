"""
modal_growth_bot.py
Deploy the XPredictor Autonomous Social Media & Alpha Growth Engine on Modal.
Runs on a serverless cron schedule (every 15 minutes), monitoring market regimes
and auto-publishing high-conviction reality cone alerts.
"""

import modal

app = modal.App("xpredictor-growth-bot")

growth_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "requests>=2.31.0",
        "pillow>=10.0.0",
        "requests-oauthlib>=1.3.1"
    )
    .add_local_dir("services/growth-bot", remote_path="/root/services/growth-bot")
)


@app.function(
    image=growth_image,
    timeout=120,
    cpu=1.0,
    memory=1024,
    schedule=modal.Cron("*/15 * * * *"),  # Runs automatically every 15 minutes
    secrets=[
        modal.Secret.from_dotenv(path=".env")  # Pulls your .env secrets automatically
    ]
)
def cron_signal_broadcast():
    """Scheduled cron handler for market scans and alert publishing."""
    import sys
    sys.path.append("/root/services/growth-bot")
    from bot import ConfidenceGrowthBot

    print("[Modal Cloud] Initializing XPredictor Growth Bot Cron Cycle...")
    bot = ConfidenceGrowthBot()
    bot.run_check_cycle(dry_run=False)
    print("[Modal Cloud] Market scan and broadcast cycle completed.")


@app.local_entrypoint()
def test_cloud_run():
    """Run a single test cycle on Modal cloud via CLI."""
    cron_signal_broadcast.remote()
