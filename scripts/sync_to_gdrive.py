"""
scripts/sync_to_gdrive.py
Uploads the consolidated historical index data lake (ZIP and manifest) directly
to the user's Google Drive under 'xpredictor/data_lake'.
Uses credentials at C:\\Users\\ragav\\AppData\\Local\\hermes\\google_token.json.
"""

import os
import sys
import mimetypes
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN = r"C:\Users\ragav\AppData\Local\hermes\google_token.json"
FOLDER_MIME = "application/vnd.google-apps.folder"

def main():
    if not os.path.exists(TOKEN):
        print(f"Token file not found at {TOKEN}")
        return

    creds = Credentials.from_authorized_user_file(TOKEN)
    svc = build("drive", "v3", credentials=creds)

    def find_folder(name, parent=None):
        q = f"mimeType='{FOLDER_MIME}' and name='{name}' and trashed=false"
        if parent:
            q += f" and '{parent}' in parents"
        r = svc.files().list(q=q, spaces="drive", fields="files(id,name)").execute().get("files", [])
        return r[0]["id"] if r else None

    def create_folder(name, parent=None):
        fid = find_folder(name, parent)
        if fid:
            print(f"Found Google Drive folder '{name}' (ID: {fid})")
            return fid
        body = {"name": name, "mimeType": FOLDER_MIME}
        if parent:
            body["parents"] = [parent]
        fid = svc.files().create(body=body, fields="id").execute()["id"]
        print(f"Created Google Drive folder '{name}' (ID: {fid})")
        return fid

    def upload_file(local_path, filename, parent_id):
        q = f"name='{filename}' and '{parent_id}' in parents and trashed=false"
        ex = svc.files().list(q=q, spaces="drive", fields="files(id)").execute().get("files", [])
        mt = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        media = MediaFileUpload(local_path, mimetype=mt, resumable=True)
        if ex:
            file_id = ex[0]["id"]
            svc.files().update(fileId=file_id, media_body=media).execute()
            print(f"Updated Google Drive file '{filename}' (ID: {file_id})")
            return file_id
        else:
            file_id = svc.files().create(body={"name": filename, "parents": [parent_id]}, media_body=media, fields="id").execute()["id"]
            print(f"Uploaded Google Drive file '{filename}' (ID: {file_id})")
            return file_id

    # 1. Target folder on Google Drive
    root_folder = create_folder("xpredictor")
    data_lake_folder = create_folder("historical_data_lake", parent=root_folder)

    # 2. Files to upload
    zip_path = r"C:\Users\ragav\OneDrive\XPredictor_Historical_Indices_DataLake.zip"
    manifest_path = r"C:\Users\ragav\OneDrive\XPredictor_Data_Lake\manifest.json"

    if os.path.exists(zip_path):
        print(f"Uploading ZIP package ({os.path.getsize(zip_path) / (1024*1024):.2f} MB)...")
        upload_file(zip_path, "XPredictor_Historical_Indices_DataLake.zip", data_lake_folder)

    if os.path.exists(manifest_path):
        print("Uploading manifest.json...")
        upload_file(manifest_path, "manifest.json", data_lake_folder)

    # Also upload individual index JSON files
    lake_dir = r"C:\Users\ragav\OneDrive\XPredictor_Data_Lake"
    for fname in os.listdir(lake_dir):
        if fname.endswith(".json") and fname != "manifest.json":
            fpath = os.path.join(lake_dir, fname)
            print(f"Uploading {fname} ({os.path.getsize(fpath) / 1024:.1f} KB)...")
            upload_file(fpath, fname, data_lake_folder)

    print("\n[SUCCESS] All historical data successfully uploaded and synchronized with Google Drive!")

if __name__ == "__main__":
    main()
