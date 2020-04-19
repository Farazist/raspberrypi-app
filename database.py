import mysql.connector
from requests import post
import json
from app import *

class Database:
    
    @staticmethod
    def signInUser(mobile_number, password):
        
        data = {'mobile_number':mobile_number, 'password':password,}
        
        response = post(url=url+'/api/signin-user', data=data)
        
        try:
            return json.loads(response.text)
        except:
            return None

    @staticmethod
    def getUser(user):
        headers = {
            'authorization': 'Bearer ' + user['access_token'], 
            'Content-Type': 'application/json'
        }

        response = post(url=url + '/api/get-user', headers=headers)
        return json.loads(response.text)
        
    @staticmethod
    def getCategories():
        response = post(url=url + '/api/get-categories')
        return json.loads(response.text)
        
    @staticmethod
    def getItems():
        response = post(url=url + '/api/get-default-items')
        return response.json()

    @staticmethod
    def getSystem(system_id):
        data = {'id': system_id}

        response = post(url=url + '/api/get-system', data=json.dumps(data))
        return response.json()
        
    @staticmethod
    def addNewDelivery(user, system_id, items):
        headers = {
            'authorization': 'Bearer ' + user['access_token'], 
            'Content-Type': 'application/json'
        }
        
        data = {
            'user_id': user['id'], 
            'system_id': system_id, 
            'state': 'done', 
            'items': items
        }
        
        response = post(url=url + '/api/add-new-delivery', data=json.dumps(data), headers=headers)

        return response.json()

    @staticmethod
    def transfer(user, items, system_id):
        headers = {
            'authorization': 'Bearer ' + user['access_token'], 
            'Content-Type': 'application/json'
        }
        
        data = {'user_id': user['id'], 'system_id': system_id, 'state': 'done', 'items': items}
        
        response = post(url=url + '/api/add-new-delivery', data=json.dumps(data), headers=headers)

        return response.json()

    @staticmethod
    def transferSecure(user, system_id, amount):
        headers = {
            'authorization': 'Bearer ' + user['access_token'], 
            'Content-Type': 'application/json'
        }
        
        data = {'system_id': system_id, 'amount': amount}
        
        response = post(url=url + '/api/transfer-secure', data=json.dumps(data), headers=headers)

        #return response.json()