import mysql.connector
import requests
import json
from app import *

class Database:
    
    @staticmethod
    def signInUser(mobile_number, password):
        
        data = {'mobile_number':mobile_number, 'password':password,}
        
        response = requests.post(url=url + '/api/signin-user', data=data)
        
        return response.json()

    @staticmethod
    def getCategories():
        response = requests.post(url=url + '/api/get-categories')
        return json.loads(response.text)
        
    @staticmethod
    def getItems():
        response = requests.post(url=url + '/api/get-items')
        return response.json()

    @staticmethod
    def getSystem(system_id):
        data = {'id': system_id}

        response = requests.post(url=url + '/api/get-system', data=json.dumps(data))
        return response.json()
        
    @staticmethod
    def addNewDelivery(user, items, system_id):
        headers = {
            'authorization': 'Bearer ' + user['access_token'], 
            'Content-Type': 'application/json'
        }
        
        data = {'user_id': user['id'], 'system_id': system_id, 'state': 'done', 'items': items}
        
        response = requests.post(url=url + '/api/add-new-delivery', data=json.dumps(data), headers=headers)

        return response.json()

    @staticmethod
    def transfer(user, items, system_id):
        headers = {
            'authorization': 'Bearer ' + user['access_token'], 
            'Content-Type': 'application/json'
        }
        
        data = {'user_id': user['id'], 'system_id': system_id, 'state': 'done', 'items': items}
        
        response = requests.post(url=url + '/api/add-new-delivery', data=json.dumps(data), headers=headers)

        return response.json()