from google.cloud import storage
import os

def getClient():
    # Explicitly use service account credentials by specifying the private key file.
    service_account_path = 'ServiceAccount.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
    return storage.Client()

# Now, when you call getClient in your main code, it should not raise the DefaultCredentialsError.
if __name__ == "__main__":
    client = getClient()
    print(client)

