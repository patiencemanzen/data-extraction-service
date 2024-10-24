import google.generativeai as genai # type: ignore
import pytesseract # type: ignore
import logging
import fitz # type: ignore

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

        self.model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        "You are tasked with extracting key information from the following text:\n\n\"r e p u b u l k u r w n uruhushya rwagateganyo rwo gutwara ibinyabiziga amazina dusingiza rukundo clemence aho yavukiye gasabo indangamuntu 1200070141812073 itariki yavukiyeho 03122000 igitsina gore nimero yuruhushya nyg2006230901090054p igihe rutangiwe 29052024 rutanzwe na polisi yu rwanda kugeza 29052025 icyitonderwa uru ruhushya mu buryo bwikoranabuhanga rwemejwe na polisi yu rwanda kugira ngo wirinde uburiganya reba ko uru ruhushya rufite umwimerere shyiramo nomero ya dosiye b240529123053lqg6 kuri irembogov mbere yo kurukoresha kode ya qr yemezwa na polisi yu rwanda bishyizweho umukono koranabuhanga na komiseri ushinzwe ishami ryibizamini nimpushya zo gutwara ibinyabiziga inyandiko yatangiwe ku\"\n\nPlease extract and provide at least the following information:\n\nFull names\n\nDate of birth\n\nAddress\n\nFormat the extracted information in JSON. Use lowercase keys with underscores instead of spaces. If any specified fields are missing, indicate them as nullable. Include any relevant metadata under the metadata key.\n\nHere is the submitted data:\n\nfirstname: Manirabona\n\nsecondname: Patience\n\nemail: hseal419@gmail.com\n\npersonal_id:\n\naddress: kigali, rwanda\n\ncity: kigali\n\ndob: 28/04/2002\n\ncountry_code: +250\n\ncountry: rwanda\n\nphone_number: 0780289432\n\nValidate the submitted data against the extracted data. Include the following keys in the JSON output:\n\nsubmitted (indicating if the submitted data matches)\n\ndocument (indicating if the extracted data from text provided is correct)\n\nis_match (true or false)\n\nvalid (true or false, indicating if the provided text and submitted data are authentic)\n\nface_matches (true or false, indicating if a face image is provided and matches the reference image)\n\ndocument_type (e.g., personal ID, company registration, etc.)\n\nProcessing Steps:\n\nExtract all structured and unstructured data, formatting them in JSON to ensure each extracted data matches the submitted data.\n\nCheck for mismatches between the submitted data and provided text details, noting any discrepancies.\n\n",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "```json\n{\n  \"full_names\": \"Rukundo Clemence\",\n  \"date_of_birth\": \"03122000\",\n  \"address\": \"Gasabo\",\n  \"metadata\": {\n    \"document_type\": \"Driving License\",\n    \"issuing_authority\": \"Police yu Rwanda\",\n    \"license_number\": \"nyg2006230901090054p\",\n    \"issue_date\": \"29052024\",\n    \"expiry_date\": \"29052025\",\n    \"national_id\": \"1200070141812073\",\n    \"gender\": \"Gore\"\n  },\n  \"submitted\": {\n    \"firstname\": \"Manirabona\",\n    \"secondname\": \"Patience\",\n    \"email\": \"hseal419@gmail.com\",\n    \"personal_id\": null,\n    \"address\": \"kigali, rwanda\",\n    \"city\": \"kigali\",\n    \"dob\": \"28/04/2002\",\n    \"country_code\": \"+250\",\n    \"country\": \"rwanda\",\n    \"phone_number\": \"0780289432\"\n  },\n  \"document\": {\n    \"full_names\": \"Rukundo Clemence\",\n    \"date_of_birth\": \"03122000\",\n    \"address\": \"Gasabo\",\n    \"personal_id\": \"1200070141812073\"\n  },\n  \"is_match\": false,\n  \"valid\": false,\n  \"face_matches\": null, \n  \"processing_steps\": [\n    \"Extracted the full name 'Rukundo Clemence' from the document.\",\n    \"Extracted the date of birth '03122000' from the document, formatted as DDMMYYYY.\",\n    \"Extracted the address 'Gasabo' from the document.\",\n    \"Extracted the national ID '1200070141812073' from the document.\",\n    \"Compared the extracted data to the submitted data. There is a mismatch in all fields except for the country 'rwanda'.\",\n    \"The 'valid' field is set to false due to the mismatch between extracted and submitted data.\",\n    \"Since no face image is provided, the 'face_matches' field is set to null.\"\n  ]\n}\n```\n\n**Explanation:**\n\n1. **Data Extraction:** We extracted the relevant information from the document, including full names, date of birth, address, national ID, and metadata about the driving license.\n2. **Data Validation:** We compared the extracted data to the submitted data. There were mismatches in all fields except for the country. This indicates that the submitted data is not from the same individual as the driving license.\n3. **Face Image:** The text does not include any information about a face image. Therefore, we set the `face_matches` field to `null`. \n4. **Validity:**  Due to the mismatches in the data, the `valid` field is set to `false`. This indicates that the document and submitted data do not appear to be authentic.\n\n**Verification Process with Facial Data:**\n\nIf a face image was provided, we could implement the following steps:\n\n1. **Face Detection:** Use a facial recognition API to detect the face in the provided image.\n2. **Facial Feature Extraction:** Extract key features from the detected face, such as distance between eyes, nose width, etc.\n3. **Comparison:** Compare the extracted features with those extracted from a reference image (if available).\n4. **Matching:** If the features match within a predefined threshold, then the face image would be deemed a match.\n5. **Verification:** The face matching result could be used to verify the identity of the individual in conjunction with other document data.\n\n**Note:** This is a simplified example.  In a real-world scenario, facial recognition systems would typically use more sophisticated techniques for feature extraction and matching. \n",
                    ],
                },
                {
                    "role": "user",
                    "parts": [
                        "You are tasked with extracting key information from the following text:\n\n\"disclaimer avoid fraud check document real searching document number irembo use document issued republic rwanda civil registrars office birth certificate names hirwa manirabona national id 1200280028683038 gender male date birth 28042002 place birth bugesera rwanda father manirabona mother mukankubana issued kimironko gasabo issued umuhoza rwabukumba executive secretary sector kimironko issued 15092022 scan code verify document verify irembo using document b220914212535kch9\"\n\nPlease extract and provide at least the following information:\n\nFull names, Date of birth, Address\n\nFormat the extracted information in JSON. Use lowercase keys with underscores instead of spaces. If any specified fields are missing, indicate them as nullable. Include any relevant metadata under the metadata key.\n\nHere is the submitted data:\n\nfirstname: Manirabona\nsecondname: Patience\nemail: hseal419@gmail.com\npersonal_id:\naddress: kigali, rwanda\ncity: kigali\ndob: 28/04/2002\ncountry_code: +250\ncountry: rwanda\nphone_number: 0780289432\n\nValidate the submitted data against the extracted data. Include the following keys in the JSON output:\nsubmitted (indicating if the submitted data matches)\ndocument (indicating if the extracted document data is correct)\nis_match (true or false)\nvalid (true or false, indicating if the document and submitted data are authentic)\nface_matches (true or false, indicating if a face image is provided and matches the reference image)\ndocument_type (e.g., personal ID, company registration, etc.)\n\nProcessing Steps:\nExtract all structured and unstructured data, formatting them in JSON to ensure each extracted data matches the submitted data.\nCheck for mismatches between the submitted data and document details, noting any discrepancies.\nDescribe any face images found in the document, including details, and compare them to the provided image file.\nOutline the process of verifying identity using facial data if an image is provided.",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "```json\n{\n  \"full_names\": \"Hirwa Manirabona\",\n  \"date_of_birth\": \"28042002\",\n  \"address\": \"Bugesera, Rwanda\",\n  \"metadata\": {\n    \"document_type\": \"Birth Certificate\",\n    \"issuing_authority\": \"Republic of Rwanda Civil Registrars Office\",\n    \"national_id\": \"1200280028683038\",\n    \"gender\": \"Male\",\n    \"place_of_birth\": \"Bugesera, Rwanda\",\n    \"father_name\": \"Manirabona\",\n    \"mother_name\": \"Mukankubana\",\n    \"issue_date\": \"15092022\",\n    \"issue_location\": \"Kimironko, Gasabo\",\n    \"issued_by\": \"Umuhoza Rwabukumba, Executive Secretary, Sector Kimironko\",\n    \"scan_code\": \"b220914212535kch9\"\n  },\n  \"submitted\": {\n    \"firstname\": \"Manirabona\",\n    \"secondname\": \"Patience\",\n    \"email\": \"hseal419@gmail.com\",\n    \"personal_id\": null,\n    \"address\": \"kigali, rwanda\",\n    \"city\": \"kigali\",\n    \"dob\": \"28/04/2002\",\n    \"country_code\": \"+250\",\n    \"country\": \"rwanda\",\n    \"phone_number\": \"0780289432\"\n  },\n  \"document\": {\n    \"full_names\": \"Hirwa Manirabona\",\n    \"date_of_birth\": \"28042002\",\n    \"address\": \"Bugesera, Rwanda\" \n  },\n  \"is_match\": false,\n  \"valid\": false,\n  \"face_matches\": null,\n  \"processing_steps\": [\n    \"Extracted the full name 'Hirwa Manirabona' from the document.\",\n    \"Extracted the date of birth '28042002' from the document, formatted as DDMMYYYY.\",\n    \"Extracted the place of birth 'Bugesera, Rwanda' and used it as the address.\",\n    \"Extracted the national ID '1200280028683038' from the document.\",\n    \"Compared the extracted data to the submitted data. There is a mismatch in the full name and address. The 'dob' field is the same but formatted differently. \",\n    \"The 'valid' field is set to false due to the mismatches between extracted and submitted data.\",\n    \"Since no face image is provided, the 'face_matches' field is set to null.\"\n  ]\n}\n```\n\n**Explanation:**\n\n1. **Data Extraction:** We extracted the relevant information from the text, including the full name, date of birth, address, national ID, and various details about the birth certificate.\n2. **Data Validation:** We compared the extracted data with the submitted data. We found mismatches in the full name and address. The dates of birth are the same but formatted differently.\n3. **Face Image:** There is no mention of a face image in the text, so we set `face_matches` to `null`.\n4. **Validity:** Due to the discrepancies in the data, we set `valid` to `false`. This indicates that the document and submitted data do not appear to be from the same individual.\n\n**Verification Process with Facial Data:**\n\nIf a face image were provided, the process would be the same as outlined in the previous response. However, in this case, the extracted national ID could also be used to compare against a database of IDs associated with facial images if available. This could provide an additional layer of verification.\n\n**Note:** The extracted `address` from the document is \"Bugesera, Rwanda\" because the document mentions \"place birth bugesera rwanda\". It's important to note that this might not be the individual's current address but the location of their birth. \n",
                    ],
                },
                {
                    "role": "user",
                    "parts": [
                        "You are tasked with extracting key information from the following text:\n\n\"DISCLAIMER: To avoid fraud, check if this document is real by searching the document number on Irembo before use.\nDocument Issued on \nREPUBLIC OF RWANDA\nCIVIL REGISTRAR'S OFFICE\n \nBirth Certificate\nNames: HIRWA Manirabona\nNational ID: 1200280028683038\nGender: MALE\nDate of birth: 28/04/2002\nPlace of birth: Bugesera, Rwanda\nFather: Manirabona\nMother: Mukankubana\nIssued at: Kimironko, Gasabo\nIssued by\nUMUHOZA Rwabukumba\nExecutive Secretary\nSector: Kimironko\nIssued on: 15/09/2022\n \n \nScan this code to verify\nthis document\nOR\nVerify on irembo\nusing the document no\nB220914212535KCH9\n\ndisclaimer avoid fraud check document real searching document number irembo use document issued republic rwanda civil registrars office birth certificate names hirwa manirabona national id 1200280028683038 gender male date birth 28042002 place birth bugesera rwanda father manirabona mother mukankubana issued kimironko gasabo issued umuhoza rwabukumba executive secretary sector kimironko issued 15092022 scan code verify document verify irembo using document b220914212535kch9\"\n\nPlease extract and provide at least the following information:\n\nFull names, Date of birth, Address\n\nFormat the extracted information in JSON. Use lowercase keys with underscores instead of spaces. If any specified fields are missing, indicate them as nullable. Include any relevant metadata under the metadata key.\n\nHere is the submitted data:\n\nfirstname: Manirabona\nsecondname: Patience\nemail: hseal419@gmail.com\npersonal_id:\naddress: kigali, rwanda\ncity: kigali\ndob: 28/04/2002\ncountry_code: +250\ncountry: rwanda\nphone_number: 0780289432\n\nValidate the submitted data against the extracted data. Include the following keys in the JSON output:\nsubmitted (indicating if the submitted data matches)\ndocument (indicating if the extracted document data is correct)\nis_match (true or false)\nvalid (true or false, indicating if the document and submitted data are authentic)\nface_matches (true or false, indicating if a face image is provided and matches the reference image)\ndocument_type (e.g., personal ID, company registration, etc.)\n\nProcessing Steps:\nExtract all structured and unstructured data, formatting them in JSON to ensure each extracted data matches the submitted data.\nCheck for mismatches between the submitted data and document details, noting any discrepancies.\nDescribe any face images found in the document, including details, and compare them to the provided image file.\nOutline the process of verifying identity using facial data if an image is provided.",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "```json\n{\n  \"full_names\": \"HIRWA Manirabona\",\n  \"date_of_birth\": \"28/04/2002\",\n  \"address\": \"Bugesera, Rwanda\",\n  \"metadata\": {\n    \"document_type\": \"Birth Certificate\",\n    \"issuing_authority\": \"REPUBLIC OF RWANDA\\nCIVIL REGISTRAR'S OFFICE\",\n    \"national_id\": \"1200280028683038\",\n    \"gender\": \"MALE\",\n    \"place_of_birth\": \"Bugesera, Rwanda\",\n    \"father_name\": \"Manirabona\",\n    \"mother_name\": \"Mukankubana\",\n    \"issue_date\": \"15/09/2022\",\n    \"issue_location\": \"Kimironko, Gasabo\",\n    \"issued_by\": \"UMUHOZA Rwabukumba\\nExecutive Secretary\\nSector: Kimironko\",\n    \"scan_code\": \"B220914212535KCH9\",\n    \"verification_instructions\": \"Scan this code to verify\\nthis document\\nOR\\nVerify on irembo\\nusing the document no\"\n  },\n  \"submitted\": {\n    \"firstname\": \"Manirabona\",\n    \"secondname\": \"Patience\",\n    \"email\": \"hseal419@gmail.com\",\n    \"personal_id\": null,\n    \"address\": \"kigali, rwanda\",\n    \"city\": \"kigali\",\n    \"dob\": \"28/04/2002\",\n    \"country_code\": \"+250\",\n    \"country\": \"rwanda\",\n    \"phone_number\": \"0780289432\"\n  },\n  \"document\": {\n    \"full_names\": \"HIRWA Manirabona\",\n    \"date_of_birth\": \"28/04/2002\",\n    \"address\": \"Bugesera, Rwanda\" \n  },\n  \"is_match\": false,\n  \"valid\": false,\n  \"face_matches\": null,\n  \"processing_steps\": [\n    \"Extracted the full name 'HIRWA Manirabona' from the document.\",\n    \"Extracted the date of birth '28/04/2002' from the document, formatted as DD/MM/YYYY.\",\n    \"Extracted the place of birth 'Bugesera, Rwanda' and used it as the address.\",\n    \"Extracted the national ID '1200280028683038' from the document.\",\n    \"Compared the extracted data to the submitted data. There is a mismatch in the full name and address.  The 'dob' field is the same but formatted differently.\",\n    \"The 'valid' field is set to false due to the mismatches between extracted and submitted data.\",\n    \"Since no face image is provided, the 'face_matches' field is set to null.\"\n  ]\n}\n```\n\n**Explanation:**\n\n1. **Data Extraction:** We extracted the relevant information from the text, including the full name, date of birth, address, national ID, and various details about the birth certificate. \n2. **Data Validation:** We compared the extracted data with the submitted data. We found mismatches in the full name and address. The dates of birth are the same but formatted differently.\n3. **Face Image:** There is no mention of a face image in the text, so we set `face_matches` to `null`.\n4. **Validity:** Due to the discrepancies in the data, we set `valid` to `false`. This indicates that the document and submitted data do not appear to be from the same individual.\n\n**Verification Process with Facial Data:**\n\nIf a face image were provided, the process would be the same as outlined in the previous responses. However, in this case, the extracted national ID could also be used to compare against a database of IDs associated with facial images if available. This could provide an additional layer of verification.\n\n**Note:**  The `address` field is assigned to the \"place of birth\" from the document because it's the only address-like information provided.  The extracted data suggests the individual was born in Bugesera, Rwanda, but their current address is not available in the provided information. \n",
                    ],
                },
            ]
        )

        print("Fine Tuning completed.")

    # Prepare a prompt for the model
    def genAiPrompt(self, extracted_data="", personal_key_information="\\n1. Full names\\n2. Date of birth\\n3. Address\\n4. document type\\n", company_key_information="\\n1. Date of issuance\\n2. company code\\n3. company name\\n4. registration date\\n5. owner details or Any associated identification numbers (e.g., national ID, passport number, TIN number, etc.)", submitted_data="\\n1. firstname: Manirabona \\n2. secondname: Patience \\n\n3.email: hseal419@gmail.com\\n4.personalid: \\n5.address: kigali, rwanda\\n6. city: kigali\\n7. Dob: 28/04/2002\\n8.countryCode: +250\\n9. Country: rwanda\\n10.phoneNumber: 0780289432\\n"):
        """Generates a prompt for the model to use.

            This implementation uses the file's URI as the prompt text.
        """

        return (
            f"You are tasked with extracting key information from the following text that have been extracted from document: {extracted_data}\n"
            f"Please extract and provide at least the following information: {personal_key_information}.\n"
            f"For the company identification, please provide: {company_key_information}.\n\n"
            "Format the extracted information in JSON. Use lowercase keys with underscores instead of spaces. "
            "If any specified fields are missing, indicate them as nullable. Include any relevant metadata under the 'metadata' key.\n\n"
            f"Here is the submitted data: {submitted_data}\n\n"

            "Please validate the submitted data against the extracted data. Include the following keys in the JSON output:\n"
            "- 'document_type': (e.g., personal ID, company registration, etc.)\n"
            "- 'extracted_data': indicating all extracted data from text and formated.\n"
            "- 'submitted_data': indicating all submitted data.\n"
            "- 'validatios': combine both extracted_data and submitted_data but validate matches, and it should be like key pair {'firstname': 'john', 'lastname': 'doe', 'matched': true} \n"
            "- 'is_match': indicating & check if overall both submitted data and extracted data matches.\n"

            "Processing Steps:\n"
            "- Extract all structured and unstructured data.\n"
            "- Formatting them in consistency JSON to ensure each extracted data matches the submitted data."
            "- Check for mismatches between the submitted data and provided text details, noting any discrepancies.\n"
        )

    # Extract data from the uploaded file
    def extractData(self, uploaded_file, uploaded_image, submitted_data):
        # Upload the file to Gemini
        self.file = uploaded_file
        self.image = uploaded_image
        self.submitted_data = submitted_data

        # Extract Data From File
        files = [uploaded_file] 
        extracted_text = self.extract_text_from_files(files)

        # Build custom Prompt
        if submitted_data is None:
            prompt = self.genAiPrompt()
        else:
            prompt = self.genAiPrompt(extracted_data=extracted_text, submitted_data=self.formatSubmittedData(submitted_data))

        # Start a new chat session with the new document
        model_session = self.model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [ prompt ],
                },
            ]
        )

        # Send a message to the chat session to continue processing
        chat_response = model_session.send_message("Please extract all relevant details from this text, validate the submitted data and verify the records if applicable.")
        return chat_response.text

    def extract_text_from_files(self, file_paths):
        combined_text = ""

        for file_path in file_paths:
            if file_path.endswith('.pdf'):
                combined_text += self.extract_text_from_pdf(file_path) + "\n"
            elif file_path.endswith('.docx'):
                combined_text += self.extract_text_from_docx(file_path) + "\n"
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                combined_text += self.extract_text_from_image(file_path) + "\n"
            else:
                print(f"Unsupported file type: {file_path}")
        return combined_text
    
    # Function to extract text from an image
    def extract_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            # Use Pytesseract  do OCR (Optical Character Recognition) on the image
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""

    # Function to extract text from a PDF
    def extract_text_from_pdf(self, pdf_path):
        text = ""
        try:
            # Open the PDF file
            document = fitz.open(pdf_path)
            for page in document:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    # Function to Extractr text from docx
    def extract_text_from_docx(self, docx_path):
        text = ""
        try:
            document = Document(docx_path)
            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""

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