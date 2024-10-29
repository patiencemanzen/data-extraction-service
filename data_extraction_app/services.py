import google.generativeai as genai # type: ignore
import logging
import time
import os
import mimetypes
from google.generativeai.types import HarmCategory, HarmBlockThreshold # type: ignore
from googleapiclient.errors import HttpError # type: ignore
from PIL import Image # type: ignore
from docx import Document # type: ignore
import requests # type: ignore
import environ # type: ignore

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
)

logger = logging.getLogger(__name__)
defaultCallbackURL = env('CLIENT_CALLBACK_URL', default="https://test.murugocloud.com/api/v2/user/verification/callback")
genai.configure(api_key=env('GEMINI_API_KEY', default="AIzaSyBfOk5t2RSgj88i91zXQLLLrgqN5vh05gw"))

class GenFileDataExtractionService:
    # Initialize the service
    def __init__(self):
        print("Initializing Gen AI Model Chat Session...")

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
            }
        )

        self.model = model
        self.prompt = self.genAiPrompt()

        print("Gen AI Model Chat Session initialized.")

    # Start a chat session with the model
    def initChatSession(self):
        print("Starting Fine Tuning...")

        base_path = "data_extraction_app/model_testing_files"

        files = [
            self.upload_to_gemini(os.path.join(base_path, "Scan9.pdf"), mimeType="application/pdf"),
            self.upload_to_gemini(os.path.join(base_path, "Snapinsta.app_448680430_427118100148525_4033672847218066239_n_1080.jpg"), mimeType="image/jpeg"),
            self.upload_to_gemini(os.path.join(base_path, "DisplayDomesticNormalReport.pdf"), mimeType="application/pdf"),
            self.upload_to_gemini(os.path.join(base_path, "Snapinsta.app_448680430_427118100148525_4033672847218066239_n_1080.jpg"), mimeType="image/jpeg"),
        ]

        # Some files have a processing delay. Wait for them to be ready.
        self.wait_for_files_active(files)

        self.model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        files[0],
                        files[1],
                        "You are tasked with extracting basic information from two files, which may be in PDF, DOCX, or image format.  1. First File: This file could contain a corporate document, company registration details, or personal information. Extract the relevant information and format it as structured JSON. 2. Second File: This could either be a simple document or an image of the owner of the first document. Again, extract the pertinent information and format it in a similar structured JSON format. After completing these tasks, perform a simple validation to determine whether there is a relationship between the two files, specifically whether the information pertains to the same individual. Additionally, if images are included, verify whether they depict the same person.\n\nWhat is mostly needed from personal docs:\n1. Full name\n2. date of birth\n3. id\n4. contacts\n\nWhat is mostly needed from corporate docs or company registration:\n1. company code\n2. company name\n3. registration date\n4. contacts\n \nProcessing Steps:\n1. extract both file's details\n2. combine for info in one JSON\n3. validate both files and append the result in the previous JSON\n4. return one JSON format and be consistent",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "```json\n{\n  \"personal_info\": {\n    \"full_name\": \"MANIRABONA Hirwa Patience\",\n    \"date_of_birth\": \"28/04/2002\",\n    \"id\": \"1 2002 8 0028683 1 24\",\n    \"contacts\": []\n  },\n  \"corporate_info\": {\n    \"company_code\": null,\n    \"company_name\": null,\n    \"registration_date\": null,\n    \"contacts\": []\n  },\n  \"validation\": {\n    \"files_match\": false,\n    \"images_match\": false,\n    \"relationship_notes\": \"The files appear to be unrelated. The personal file contains information about an individual, while the second file is a corporate document.\"\n  }\n}\n```",
                    ],
                },
                {
                    "role": "user",
                    "parts": [
                        files[2],
                        files[3],
                        "try this also",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "```json\n{\n  \"personal_info\": {\n    \"full_name\": \"MANIRABONA Hirwa Patience\",\n    \"date_of_birth\": null,\n    \"id\": \"1200280028683124\",\n    \"contacts\": []\n  },\n  \"corporate_info\": {\n    \"company_code\": \"123072484\",\n    \"company_name\": \"WADDLE Ltd\",\n    \"registration_date\": \"06/08/2024\",\n    \"contacts\": [\n      {\n        \"type\": \"phone\",\n        \"value\": \"+2500780289432\"\n      },\n      {\n        \"type\": \"email\",\n        \"value\": \"hseal419@gmail.com\"\n      }\n    ]\n  },\n  \"validation\": {\n    \"files_match\": true,\n    \"images_match\": false,\n    \"relationship_notes\": \"The personal information in the first file matches the information about the Chief Executive Officer in the second file, indicating a relationship between the files.\"\n  }\n}\n```",
                    ],
                },
            ]
        )

        print("Fine Tuning completed.")

    # Upload a file to Gemini
    def upload_to_gemini(self, file_path, mimeType=None):
        """Uploads the given file to Gemini.

            See https://ai.google.dev/gemini-api/docs/prompting_with_media
        """
        file = genai.upload_file(path=file_path, mime_type=mimeType)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")

        return file

    # Wait for the files to be active
    def wait_for_files_active(self, files):
        """Waits for the given files to be active.

            Some files uploaded to the Gemini API need to be processed before they can be
            used as prompt inputs. The status can be seen by querying the file's "state"
            field.

            This implementation uses a simple blocking polling loop. Production code
            should probably employ a more sophisticated approach.
        """
        print("Waiting for file processing...")

        for name in (file.name for file in files):
            file = genai.get_file(name)
            while file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(10)
                file = genai.get_file(name)
            if file.state.name != "ACTIVE":
                raise Exception(f"File {file.name} failed to process")
            
        print("...all files ready")
        print()

    # Prepare a prompt for the model
    def genAiPrompt(self):
        """Generates a prompt for the model to use.

            This implementation uses the file's URI as the prompt text.
        """

        return (
            f"""
                You are tasked with extracting basic information from two files, which may be in PDF, DOCX, or image format.

                1. **First File**: This file could contain a corporate document, company registration details, or personal information. Extract the relevant information and format it as structured JSON.
                2. **Second File**: This could either be a simple document or an image of the owner of the first document. Again, extract the pertinent information and format it in a similar structured JSON format.

                After completing these tasks, perform a simple validation to determine whether there is a relationship between the two files, specifically whether the information pertains to the same individual. Additionally, if images are included, verify whether they depict the same person.

                ### What is mostly needed from personal docs:
                1. Full name
                2. Date of birth
                3. ID
                4. Contacts

                ### What is mostly needed from corporate docs or company registration:
                1. Company code
                2. Company name
                3. Registration date
                4. Contacts

                ### Processing Steps:
                1. Extract both file's details.
                2. Combine the information into one JSON.
                3. Validate both files and append the result in the previous JSON.
                4. Return one JSON format and be consistent.
                """
        )

    # Extract data from the uploaded file
    def extractData(self, uploaded_file, uploaded_image, submitted_data):
        # Upload the file to Gemini
        self.file = uploaded_file
        self.image = uploaded_image
        self.submitted_data = submitted_data

        # Guess the MIME types
        file_mime_type, _ = mimetypes.guess_type(self.file)
        image_mime_type, _ = mimetypes.guess_type(self.image)

        uploadedFiles = [
            self.upload_to_gemini(self.file, mimeType=file_mime_type),
            self.upload_to_gemini(self.image, mimeType=image_mime_type),
        ]

        # Some files have a processing delay. Wait for them to be ready.
        self.wait_for_files_active(uploadedFiles)

        # Start a new chat session with the new document
        model_session = self.model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        uploadedFiles[0],
                        uploadedFiles[1],
                        self.prompt,
                    ],
                },
            ]
        )

        # Send a message to the chat session to continue processing
        chat_response = model_session.send_message("Extract any additional personal identifiers, contacts, or addresses if available, and add them to the JSON output.")

        return chat_response.text

    # Format the extracted data
    def formatSubmittedData(self, data):
        return (
            f"\\n1. firstname: {data['firstname']} "
            f"\\n2. secondname: {data['secondname']} "
            f"\\n3. email: {data['email']} "
            f"\\n4. personalid: {data['personalid']} "
            f"\\n5. address: {data['address']} "
            f"\\n6. city: {data['city']} "
            f"\\n7. Dob: {data['dob']} "
            f"\\n8. countryCode: {data['countryCode']} "
            f"\\n9. Country: {data['country']} "
            f"\\n10. phoneNumber: {data['phoneNumber']}\\n"
        )
    
    # Handle the data extraction process
    def handleFileDataExtraction(self, uploaded_file, submitted_data):
        try:
            # Extract data from the uploaded file
            extracted_data = self.extractData(uploaded_file=uploaded_file.file.path, uploaded_image=uploaded_file.image_file.path, submitted_data=submitted_data)

            # Log the extracted data for debugging
            logging.debug(f"Extracted data (raw): {extracted_data}")

            # Clean up the extracted data by removing unwanted characters
            cleaned_data_str = extracted_data.strip().replace("```json\n", "").replace("```", "")

            logging.debug(f"Cleaned extracted data: {cleaned_data_str}")

            # Store extracted data in the database with the file record
            uploaded_file.extracted_data = cleaned_data_str
            uploaded_file.save()

            return uploaded_file.extracted_data
        except HttpError as e:
            if e.resp.status == 503:
                logger.warning(f"Service unavailable.")
            else:
                logger.error(f"Failed to upload file: {e}")
                raise

    # Send the extracted data to the custom API
    def send_callback_to_custom_api(self, murugo_user_id, extracted_data): 
        # Convert extracted_data to a list if it's a set
        if isinstance(extracted_data, set):
            extracted_data = list(extracted_data)
        
        payload = {
            "murugo_user_id": murugo_user_id,
            "extracted_data": extracted_data
        }

        print(payload)
        
        try:
            response = requests.post(defaultCallbackURL, json=payload, headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            })

            response.raise_for_status()
            
            # Check if the response is empty
            if response.text.strip() == "":
                logger.error("Received empty response from the server")
                return {"error": "Received empty response from the server"}
            
            try:
                response_data = response.text
                logger.info(f"Successfully sent callback with data: {response_data}")
                return response_data
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return {"error": f"Failed to parse JSON response: {e}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send callback with data Error: {e}")
            return {"error": f"Failed to send callback with data Error: {e}"}

DataExtractionService = GenFileDataExtractionService()