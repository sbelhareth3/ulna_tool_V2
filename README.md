# Ulna Length Tool

This is a tool used for the conversion of ulnar length to a predicting standing height and predicted normal pulmonary function. Many of the inputs necessary for this computation are not found in a FHIR profile, and thus must be manually input by the physician. 

A future iteration of the app would allow for clinicians to 

Finding a means by which to store relevant information, such as ulnar length, in observation resources as free-text CodeableConcepts, and upload it to a FHIR server is the next major task necessary for this application.

# Setup

First, install Django and any necessary dependencies. 

This can be done by running

```pip install django```

or using a Conda equivalent.

Check the version using:

```python -m django --version```

to make sure you have django installed correctly.

# Ulna Length Tool

In order to start the web application, navigate to , type:

```python manage.py runserver```

then, navigate to http://[LOCAL_HOST]:8000

# Understanding the code

The ```templates``` folder contains the HTML templates used for this web application. The HTML templates include python code that permits conditional statements, in a manner that can be used with Django.

Meanwhile, the ```views.py``` file contains most of the code and logic pertaining to converting ulnar length to predicted standing height and predicted normal pulmonary function.
