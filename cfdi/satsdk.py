import requests
from zeep import Client
from .sat_endpoint import SAT_AUTENTICACION
url = "https://pruebacfdiconsultaqr.cloudapp.net/"

class SATSDK:

    def autenticar(self):
        c = Client(SAT_AUTENTICACION)
        print(c.service)
        return