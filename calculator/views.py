from datetime import date

import fhirclient.models.patient as p
import fhirclient.models.procedure as pro
import requests
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import fhirclient.models.observation as obs
from fhirclient import client
from fhirclient.models import bundle
import pandas
import os
import re


# Create your views here.
settings = {
    'app_id': 'my_web_app',
    'api_base': 'https://r4.smarthealthit.org'
}
smart = client.FHIRClient(settings=settings)

# since this is proof of concept, we use a dictionary, but this is where we connect to patient database
patient_db = {
    "Bradly Pfannerstill": "c20ccf5d-19ac-4dfe-bdc3-3d1d6344facc",
    "Morgan Gislason": "9af8e1d3-885b-4356-bf48-b60297671f9b",
}



# calculator code
def ulna_to_height(sex, age, ulna_length, race, FEV1, FVC):
    """Requires:
        sex                             - "male" or "female" string
        age                             - string or int
        ulna_length                     - string or int
    """
    
    #be liberal in what we accept...massage the input
    if sex in ("MALE", "m", "M", "boy", "xy", "male", "Male"):
        sex = "male"
    if sex in ("FEMALE", "f", "F", "girl", "xx", "female", "Female"):
        sex = "female"    
    

    #intialize some things -----------------------------------------------------
    errors = [] #a list of errors
    standing_height = 0 
    PRD_FEV1 = 0
    PRD_FVC = 0
    age = int(age)
    ulna_length = int(ulna_length)
    FEV1 = float(FEV1)
    FVC = float(FVC)
    FEV1_fraction = 0
    FVC_fraction = 0

    # Intitalize our response dictionary
    response = {"status": 200,
                "sex":sex,
                "message": "OK",
                "age": age,
                "ulna_length":ulna_length,
                "standing_height":standing_height,
                "errors": errors,
                "race": race,
                "FEV1": FEV1,
                "FVC": FVC,
                "PRD_FVC":PRD_FVC,
                "PRD_FEV1":PRD_FEV1,
                "FVC_fraction": FVC_fraction,
                "FEV1_fraction": FEV1_fraction
                }
    
    
    #run some sanity checks ----------------------------------------------------
    if not 5 <= age <=18:
        errors.append("Age must be within the range of 5 to 18.")
        
    if sex.lower() not in ('male', 'female'):
        errors.append("Sex must be male or female.")

    if race == 'Asian':
        if sex == 'male':
            standing_height = 4.171*ulna_length + 1.594*age + 33.650 
            # (R2=0.95)
        if sex == 'female': 
            standing_height = 4.665*ulna_length + 1.079*age + 29.115 
            # (R2=0.93)
    else:
        if sex == 'male':
            standing_height = 4.605*ulna_length + 1.308*age + 28.003 
            # (R2=0.96)
        if sex == 'female': 
            standing_height = 4.459*ulna_length + 1.315*age + 31.485 
            # (R2=0.94)


#Equations below are the lower limit of normal equations. 
#Patients' values are found to be below these calculated values,
#it may be cause for concern
#Taken from NHANES III (Hankinson 1999)

    if race == 'African-American':
        if sex == 'male':
            PRD_FEV1 = -0.05711*age + 0.004316*age*age + 0.00010561*standing_height*standing_height - 0.7048
            PRD_FVC = -0.15497*age + 0.007701*age*age + 0.00013670*standing_height*standing_height - 0.4971

        if sex == 'female': 
            PRD_FEV1 = 0.05799*age + 0.00008546*standing_height*standing_height - 0.9630
            PRD_FVC = -0.04687*age + 0.003602*age*age + 0.00010916*standing_height*standing_height - 0.6166

    else:
        if sex == 'male':
            PRD_FEV1 = -0.04106*age + 0.004477*age*age + 0.00011607*standing_height*standing_height - 0.7453
            PRD_FVC = -0.20415*age + 0.010133*age*age + 0.00015695*standing_height*standing_height - 0.2584  

        if sex == 'female': 
            PRD_FEV1 = 0.06537*age + 0.00009283*standing_height*standing_height - 0.8710
            PRD_FVC = 0.05916*age + 0.00012198*standing_height*standing_height - 1.2082

    FEV1_fraction = FEV1/PRD_FEV1
    FVC_fraction = FVC/PRD_FVC

    if errors:
        response['status']=422
        response['message'] = "The request contained errors and was unable to process."
        response['errors']=errors
        response['standing_height']=0
    else:
        response['standing_height']=round(standing_height ,1)
        response['PRD_FVC']=round(PRD_FVC,2)
        response['PRD_FEV1']=round(PRD_FEV1,2)
        response['FEV1_fraction']=round(FEV1_fraction,2)
        response['FVC_fraction']=round(FVC_fraction,2)

    
    return response

@csrf_exempt
def home(request):
    template = loader.get_template('calculator/calculator.html')
    context = {}

    if request.POST.get('patients', False) != 'empty':
        context = {'name': request.POST.get('patients', False), "pats": patient_db}
        
    if request.method == 'POST' and request.POST.get('patients', False) != 'empty':

        p_id = patient_db[request.POST.get('patients', False)]
        patient = p.Patient.read(p_id, smart.server)
        sex = patient.gender
        age = date.today().year - int(patient.birthDate.as_json()[:4])
        ulna_length = request.POST['ulna_length']
        print(dir(patient))
        race = request.POST['race']
        FEV1 = request.POST['FEV1']
        FVC = request.POST['FVC']
        
        # calling the calculator
        calculation = ulna_to_height(sex=sex, age=age, ulna_length=ulna_length, race=race, FEV1=FEV1, FVC=FVC)

        # checking if the calculation was a success
        if calculation['status'] == 200:
            result = calculation

            context = {
                "result": result,
                "name": request.POST.get('patients', False),
                "pats": patient_db
            }
        else:
            result = calculation['errors']
            context = {
                "result": result,
            }
            print(result)

    return HttpResponse(template.render(context, request))

    