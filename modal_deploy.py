"""
modal_deploy.py
Deploys XPredictor Gateway API & Kronos Engine onto Modal Serverless infrastructure.
Connects directly to Qdrant Cloud.
"""

import modal

app = modal.App("xpredictor-api")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi>=0.110.0",
        "uvicorn>=0.28.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "numpy>=1.24.0",
        "torch",
        extra_index_url="https://download.pytorch.org/whl/cpu",
    )
    .add_local_dir("services/api", remote_path="/root/services/api")
    .add_local_dir("services/kronos-embedder", remote_path="/root/services/kronos-embedder")
    .add_local_dir("data_lake", remote_path="/root/data_lake")
)

@app.function(
    image=image,
    timeout=60,
    cpu=2.0,
    memory=2048,
    secrets=[
        modal.Secret.from_dict({
            "QDRANT_URL": "https://317060a8-849e-400b-9c7b-0c2d561f6c04.sa-east-1-0.aws.cloud.qdrant.io:6333",
            "QDRANT_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NjE4ODY2MzMtMTE3OC00YzMwLTkwZDUtZDFiOGIwNWVjODRiIn0.mUZrt_JLeLEE6yFtFXC3yr-SbiEGvGQfh9HKcFyxas8",
            "QDRANT_HOST": "317060a8-849e-400b-9c7b-0c2d561f6c04.sa-east-1-0.aws.cloud.qdrant.io",
        })
    ]
)
@modal.asgi_app()
def fastapi_app():
    import sys
    sys.path.append("/root/services/api")
    sys.path.append("/root/services/kronos-embedder")
    from main import app as web_app
    return web_app
