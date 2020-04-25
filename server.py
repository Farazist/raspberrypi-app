from requests import post
import json

url = 'https://farazist.ir'

class Server:
    
    @staticmethod
    def makeQrcodeSignInToken(system_id):
        data = {'system_id':system_id}
        try:
            response = post(url=url+'/api/make-qrcode-signin-token', data=data, verify=True)
            return response.text
        except:
            return None

    @staticmethod
    def checkQrcodeSignInToken(qrcode_signin_token):
        data = {'qrcode_signin_token':qrcode_signin_token}
        try:        
            response = post(url=url+'/api/check-qrcode-signin-token', data=data, verify=True)
            return json.loads(response.text)
        except:
            return 0

    @staticmethod
    def signInUser(mobile_number, password):
        data = {'mobile_number':mobile_number, 'password':password,}

        try:        
            response = post(url=url+'/api/signin-user', data=data, verify=True)
            return json.loads(response.text)
        except:
            return None

    @staticmethod
    def getUser(user):
        headers = {
            'authorization': 'Bearer ' + user['access_token'], 
            'Content-Type': 'application/json'
        }

        try:
            response = post(url=url + '/api/get-user', headers=headers, verify=True)
            return json.loads(response.text)
        except:
            return None
        
    @staticmethod
    def getCategories():
        try:
            response = post(url=url + '/api/get-categories')
            return json.loads(response.text)
        except:
            return None
        
    @staticmethod
    def getItems(user_id):
        data = {'user_id': user_id}
        headers = {'Content-Type': 'application/json'}

        try:
            response = post(url=url+'/api/get-items', data=json.dumps(data), headers=headers, verify=True)
            return json.loads(response.text)
        except:
            return None

    @staticmethod
    def getSystem(system_id):
        data = {'id': system_id}
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = post(url=url + '/api/get-system', data=json.dumps(data), headers=headers, verify=True)
            return json.loads(response.text)
        except:
            return None
        
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
        
        try:
            response = post(url=url + '/api/add-new-delivery', data=json.dumps(data), headers=headers, verify=True)
            return json.loads(response.text)
        except:
            return None

    @staticmethod
    def transfer(user, items, system_id):
        headers = {
            'authorization': 'Bearer ' + user['access_token'], 
            'Content-Type': 'application/json'
        }
        
        data = {'user_id': user['id'], 'system_id': system_id, 'state': 'done', 'items': items}
        
        try:
            response = post(url=url + '/api/add-new-delivery', data=json.dumps(data), headers=headers, verify=True)
            return json.loads(response.text)
        except:
            return None

    @staticmethod
    def transferSecure(user, system_id, amount):
        headers = {
            'authorization': 'Bearer ' + user['access_token'], 
            'Content-Type': 'application/json'
        }
        
        data = {'system_id': system_id, 'amount': amount, 'APP_KEY': APP_KEY, 'description': 'تحویل پسماند در دستگاه'}
        
        try:
            response = post(url=url + '/api/transfer-secure', data=json.dumps(data), headers=headers, verify=True)
            return response.json()
        except:
            return None