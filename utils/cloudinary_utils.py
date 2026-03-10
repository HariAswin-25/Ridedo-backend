import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

# Debug: Check if env variables are loaded
cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
api_key = os.getenv("CLOUDINARY_API_KEY")
api_secret = os.getenv("CLOUDINARY_API_SECRET")

print(f"--- Cloudinary Debug ---")
print(f"Cloud Name: {cloud_name}")
print(f"API Key: {api_key[:4]}...{api_key[-4:] if api_key else ''}")
print(f"API Secret Loaded: {'Yes' if api_secret else 'No'}")
print(f"------------------------")


cloudinary.config(
    cloud_name=cloud_name,  
    api_key=api_key,
    api_secret=api_secret,
    secure=True
)

import traceback

def upload_image(file):
    print("DEBUG: Cloudinary upload_image called.")
    try:
        # Reset file pointer to beginning
        file.seek(0)
        print(f"DEBUG: Attempting upload with preset: ridedo_app")
        upload_result = cloudinary.uploader.upload(
            file, 
            upload_preset="ridedo_app"
        )
        print(f"DEBUG: Cloudinary Upload SUCCESS. Result URL: {upload_result.get('secure_url')}")
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"DEBUG: Cloudinary Upload FAILED. Error: {e}")
        # Try without preset if it failed, maybe preset is not set correctly
        try:
            print("DEBUG: Retrying without upload_preset...")
            file.seek(0)
            upload_result = cloudinary.uploader.upload(file)
            print(f"DEBUG: Cloudinary Retry SUCCESS. Result URL: {upload_result.get('secure_url')}")
            return upload_result.get("secure_url")
        except Exception as retry_err:
            print(f"DEBUG: Cloudinary Retry FAILED. Error: {retry_err}")
            traceback.print_exc()
            return None
