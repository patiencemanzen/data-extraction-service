from django.apps import AppConfig # type: ignore
import subprocess
import os
import sys

class VerificationServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_extraction_app"

    def ready(self):
        # Ensure this runs only once
        if os.environ.get('RUN_MAIN') == 'true' or 'runserver' not in sys.argv:
            return

        subprocess.Popen(['celery', '-A', 'data_extraction_service', 'worker', '--loglevel=info'])
