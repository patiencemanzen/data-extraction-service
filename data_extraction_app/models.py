from django.db import models # type: ignore
from datetime import datetime
import os
import hashlib
import uuid

DEFAULT_USER_ID = 1

# Function to upload the uploaded ID file
def upload_id_file(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = f"murugo_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    return os.path.join('upload_ID_files/', new_filename)

# Function to upload the uploaded image file
def upload_image_file(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = f"murugo_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    return os.path.join('uploaded_image_files/', new_filename)
    
class UploadedFile(models.Model):
    file = models.FileField(upload_to=upload_id_file)
    image_file = models.FileField(upload_to=upload_image_file)
    extracted_data = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File {self.id} uploaded at {self.uploaded_at}"
    