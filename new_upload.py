import os
import base64
from google.cloud import storage as gcs
import firebase_admin
from firebase_admin import credentials, storage
from mimetypes import guess_type
from dotenv import load_dotenv
import urllib.parse
from datetime import datetime, timedelta
from Connections.token_and_keys import STORAGE_BUCKET

load_dotenv()

class FirebaseUpload:
    def __init__(self, file_path):
        self.file_path = file_path
        self.upload_url = ""
        if not firebase_admin._apps:
            cred = credentials.Certificate({
                "type": os.getenv('TYPE'),
                "project_id": os.getenv('PROJECT_ID'),
                "private_key_id": os.getenv('PRIVATE_KEY_ID'),
                "private_key": os.getenv('PRIVATE_KEY'),
                "client_email": os.getenv('CLIENT_EMAIL'),
                "client_id": os.getenv('CLIENT_ID'),
                "auth_uri": os.getenv('AUTH_URI'),
                "token_uri": os.getenv('TOKEN_URI'),
                "auth_provider_x509_cert_url": os.getenv('AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": os.getenv('CLIENT_X509_CERT_URL'),
                "universe_domain": os.getenv('UNIVERSE_DOMAIN')
            })
            firebase_admin.initialize_app(cred, {
                'storageBucket': STORAGE_BUCKET
            })
    def buffer_to_base64(self, buffer):
        return base64.b64encode(buffer).decode()
    
    def path(self, file_path):
        if not file_path:
            raise ValueError("No file path provided!")
        if file_path.startswith("/"):
            raise ValueError("Invalid file path!")
        is_production = os.getenv('NODE_ENV') == 'production'
        return f"prod/{file_path}" if is_production else f"dev/{file_path}"
    
    def get_firebase_storage_url(self, file_path):
        """
        Generate a Firebase Storage URL for a file.
        """
        bucket_name = os.getenv('STORAGE_BUCKET')
        return f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{urllib.parse.quote(file_path, safe='')}"
    
    def getClient(self):
        # Explicitly use service account credentials by specifying the private key file.
        service_account_path = 'ServiceAccount.json'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
        return gcs.Client()

    def get_file_download_token(self, file_path):
        bucket = storage.bucket()

        client = self.getClient()
        # bucket = os.getenv('STORAGE_BUCKET')
        blob = bucket.blob(file_path)
        print(f"client:{client} bucket{bucket} blob{blob}")
        
        blob.reload()

        if not blob.metadata:
            print(f"No metadata found for {file_path}.")
            return None

        download_tokens = blob.metadata.get('firebaseStorageDownloadTokens')
        return download_tokens
        
    def construct_public_url_with_token(self, file_path):
        download_token = self.get_file_download_token(file_path)
        print(f"download_token{download_token}")
        # if download_token:
        #     encoded_file_path = urllib.parse.quote(file_path, safe='')
        #     bucket_name = os.getenv('STORAGE_BUCKET')
        #     return f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{encoded_file_path}?alt=media&token={download_token}"
        # else:
            # return None

    def add(self, files, file_names):
        try:
            if len(files) != len(file_names):
                raise ValueError("Number of files and file names must match")

            bucket = storage.bucket()
            results = []

            for file, file_name in zip(files, file_names):
                blob_path = self.path(self.file_path + file_name)
                blob = bucket.blob(blob_path)
                mime_type, _ = guess_type(file_name)
                blob.upload_from_file(file, content_type=mime_type)
                
                public_url_with_token = self.construct_public_url_with_token(blob_path)
                results.append({"file_name": file_name, "url": public_url_with_token})

            return results
        except Exception as err:
            print(f"Error occurred while uploading: {err}")
            raise

if __name__ == "__main__":
    file_paths = ["images/esp1.png", "images/gen.jpeg"]
    upload_path = "images/"
    file_names = ["esp71.png", "esp72.png"]
    print("Here")
    firebase_upload = FirebaseUpload(upload_path)

    files_to_upload = [open(file_path, "rb") for file_path in file_paths]
    result = firebase_upload.add(files_to_upload, file_names)
    for r in result:
        print(r)

    for file in files_to_upload:
        file.close()