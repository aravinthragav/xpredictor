"""
infra/docker/qdrant_init.py
Initializes Qdrant partitioned collections for XPredictor with HNSW tuning
and RAM-resident int8 scalar quantization.
"""

import os
import requests

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
BASE_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"

COLLECTIONS = ["xpredictor_w32", "xpredictor_w64", "xpredictor_w128"]

COLLECTION_CONFIG = {
    "vectors": {
        "size": 768,
        "distance": "Cosine",
        "on_disk": True
    },
    "hnsw_config": {
        "m": 32,
        "ef_construct": 200,
        "on_disk": False
    },
    "quantization_config": {
        "scalar": {
            "type": "int8",
            "quantile": 0.99,
            "always_ram": True
        }
    }
}


def init_collections():
    print(f"Connecting to Qdrant at {BASE_URL}...")
    for col_name in COLLECTIONS:
        url = f"{BASE_URL}/collections/{col_name}"
        # Check if collection exists
        res = requests.get(url)
        if res.status_code == 200:
            print(f"[EXISTS] Collection '{col_name}' already initialized.")
            continue

        create_res = requests.put(url, json=COLLECTION_CONFIG)
        if create_res.status_code in [200, 201]:
            print(f"[CREATED] Collection '{col_name}' created successfully with int8 scalar quantization.")
        else:
            print(f"[ERROR] Failed to create collection '{col_name}': {create_res.text}")

        # Create payload indexes for fast filtering
        index_url = f"{BASE_URL}/collections/{col_name}/index"
        for field in ["symbol", "asset_class", "timeframe", "start_ts", "end_ts"]:
            payload_field = {
                "field_name": field,
                "field_schema": "keyword" if field in ["symbol", "asset_class", "timeframe"] else "integer"
            }
            requests.put(index_url, json=payload_field)
            print(f"  Indexed payload field: {field}")


if __name__ == "__main__":
    init_collections()
