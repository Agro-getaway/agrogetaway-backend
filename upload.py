import firebase_admin
from firebase_admin import credentials, storage
import os
from google.cloud import storage as gcs
import base64
from datetime import datetime, timedelta
from mimetypes import guess_type
from dotenv import load_dotenv
import os
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
    
    # def add(self, file, file_name):
    #     try:
    #         bucket = storage.bucket()
    #         blob_path = self.path(self.file_path + file_name)
    #         blob = bucket.blob(blob_path)
    #         mime_type, _ = guess_type(file_name)
    #         blob.upload_from_file(file, content_type=mime_type)
    #         # self.upload_url = blob.public_url
    #         self.upload_url = blob.generate_signed_url(expiration=datetime.timedelta(hours=1), version="v4")
    #         return {"url": self.upload_url}
    #     except Exception as err:
    #         print(f"Error occurred while uploading: {err}")
    #         raise
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
                upload_url = blob.generate_signed_url(expiration=timedelta(hours=1), version="v4")
                results.append({"file_name": file_name, "url": upload_url})

            return results
        except Exception as err:
            print(f"Error occurred while uploading: {err}")
            raise

    def update(self, file, saved_file_path, new_file_name):
        try:
            bucket = storage.bucket()

            old_blob = bucket.blob(self.path(saved_file_path))
            old_blob.delete()
            print(f"Deleted the old file at {saved_file_path}")

            new_blob_path = self.path(self.file_path + new_file_name)
            new_blob = bucket.blob(new_blob_path)
            mime_type, _ = guess_type(new_file_name)
            new_blob.upload_from_file(file, content_type=mime_type)
            self.upload_url = new_blob.generate_signed_url(expiration=datetime.timedelta(hours=1), version="v4")

            return {"url": self.upload_url}
        except Exception as err:
            print("Error occurred while updating:", err)
            raise


    def delete(self, file_path):
        try:
            bucket = storage.bucket()
            blob = bucket.blob(file_path)  
            blob.delete()
        except Exception as err:
            print(f"Error occurred while deleting: {err}")
            raise

### uploading a file and getting the url
# if __name__ == "__main__":
#     file_path = "images/esp1.png"
#     upload_path = "images/"  
#     file_name = "esp6.png"  

#     firebase_upload = FirebaseUpload(upload_path)

#     with open(file_path, "rb") as file:
#         result = firebase_upload.add(file, file_name)
#         print(result)

    # print(os.getenv('PRIVATE_KEY'))
### updating a file and getting the url
# file_path = "images/" 
# saved_file_path = "images/esp4.png" 
# new_file_name = "Animex2.png"  

# firebase_upload = FirebaseUpload(file_path)

# with open("images/Animex.png", "rb") as new_file:
#     result = firebase_upload.update(new_file, saved_file_path, new_file_name)
#     print(result)

# import pyrebase


# firebase = pyrebase.initialize_app(config)
# auth = firebase.auth()

# # adding a new image
# storage = firebase.storage()
# storage.child("image1.png").put("images/Animex.png")

# # ceating a new user
# email = "agrogetaway@gmail.com"
# password = "Agrogetaway12!"
# # getting url of the image

# user = auth.sign_in_with_email_and_password(email, password)
# # url.storage.child("image1.png").get_url(user['idToken'])
# if user:
#     print("User created")
# else:
#     print("User not created")
        

# testing multiple
        
if __name__ == "__main__":
    file_paths = ["images/esp1.png", "images/gen.jpeg"]
    upload_path = "images/"  
    file_names = ["esp60.png", "esp09.png"]

    firebase_upload = FirebaseUpload(upload_path)

    with open(file_paths[0], "rb") as file1, open(file_paths[1], "rb") as file2:
        result = firebase_upload.add([file1, file2], file_names)
        print(result)
