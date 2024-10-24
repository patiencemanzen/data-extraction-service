from celery import shared_task
from .services import DataExtractionService
from .models import UploadedFile

@shared_task
def extract_data_task(file_id, submitted_data, murugo_user_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)
        initsession = DataExtractionService.initChatSession() 
        extracted_data = DataExtractionService.handleFileDataExtraction(uploaded_file, submitted_data)
        sendCallback = DataExtractionService.send_callback_to_custom_api(murugo_user_id, extracted_data)
        
        print(f"Callback response: {sendCallback}")
    except Exception as e:
        print(f"Error during data extraction: {e}")
