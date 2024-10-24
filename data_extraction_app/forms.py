from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(required=True)
    image_file = forms.FileField(required=True)
    murugo_user_id = forms.CharField(max_length=100, required=True)
    firstname = forms.CharField(max_length=100, required=True)
    secondname = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    personalid = forms.CharField(max_length=100, required=True)
    address = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=100, required=True)
    dob = forms.CharField(required=True)
    countryCode = forms.CharField(max_length=10, required=True)
    country = forms.CharField(max_length=100, required=True)
    phoneNumber = forms.CharField(max_length=15, required=True)
    id_type = forms.CharField(max_length=50, required=True)