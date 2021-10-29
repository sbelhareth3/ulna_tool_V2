# Ulna Length Tool

This is a tool used for the conversion of ulnar length to standing height. Many of the inputs necessary for this computation are not found in a FHIR profile, and thus must be manually input by the physician. 

Finding a means by which to store relevant information, such as ulnar length, in observation resources as free-text CodeableConcepts, and upload it to a FHIR server is the next major task necessary for this application.

# Setup

First, install Django and any necessary dependencies. 

command to run:

python manage.py runserver
