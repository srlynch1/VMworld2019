import requests
import json
import boto3
client = boto3.client('ssm','ap-southeast-2') ##AWS SSM

def handler(context, inputs):
    
    if inputs['configureBlueprints'] == 'true':
            
        baseUri = inputs['baseUri']
        
        vraToken = client.get_parameter(Name="vraToken",WithDecryption=True)['Parameter']['Value'] ##AWS SSM
        url = baseUri + "/iaas/login"
        headers = {"Accept":"application/json","Content-Type":"application/json"}
        payload = {"refreshToken":vraToken}

        results = requests.post(url,json=payload,headers=headers)
        bearer = "Bearer "
        bearer = bearer + results.json()["token"]
        
        headers = {"Accept":"application/json","Content-Type":"application/json", "Authorization":bearer }
        
        projUri = baseUri + "/iaas/projects?$filter=name eq '" + inputs["vRAproject_name"] + "'"
        results = requests.get(projUri,json=payload, headers=headers)
        projectId = (results.json()['content'][0]['id'])
        print(projectId)
        
        contentURI = baseUri + "/content/api/sources"
        print(contentURI)
        
    
        payload =   {
                        "name": inputs['name'],
                        "typeId": inputs['typeId'],
                        "type": inputs['type'],
                        "projectId": projectId,
                        "config":inputs['configBlueprint'],
                        "syncEnabled": inputs['syncEnabled']
                    }
        results = requests.post(contentURI,json=payload, headers=headers)
        print(results.json() )
        
        outputs = {}

        return outputs
    else:
        print("skipping blueprint git configuration")