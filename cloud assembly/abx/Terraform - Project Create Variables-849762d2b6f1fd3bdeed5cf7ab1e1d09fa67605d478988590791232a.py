import requests
import json
import boto3
client = boto3.client('ssm','ap-southeast-2') ##AWS SSM

def handler(context, inputs):
        
    baseUri = inputs['baseUri']
    #tfToken = inputs['tfToken']
    tfToken = client.get_parameter(Name="tfToken",WithDecryption=True) ##AWS SSM
    vraToken = client.get_parameter(Name="vraToken",WithDecryption=True)['Parameter']['Value'] ##AWS SSM
    tfAPIVersion = inputs['tfAPIVersion']
    tfOrgName = inputs['tfOrgName']
    vraProjectName = inputs['vRAproject_name']
    tfAPIUri = baseUri + "/" + tfAPIVersion 
    
    headers = { "Accept":"application/json",
                "Content-Type":"application/vnd.api+json",
                "Authorization":"Bearer " + tfToken['Parameter']['Value']}
    
    workspaceUri = tfAPIUri + "/organizations/" + tfOrgName + "/workspaces/" + vraProjectName
    
    print(workspaceUri)
    
    try:
        results = requests.get(
                                    url=workspaceUri, 
                                    headers=headers
                                )
                                    
        workspaceId = results.json()['data']['id']
        
    except KeyError as error:
        raise Exception("There was an error with getting the variables. URL: " + workspaceUri + ", " + str(results))
        
    except Exception as error:
        print("There was a problem with getting the variables: " + str(error))
        raise Exception("There was an error with getting the variables: " + str(error))
    
    inputVars = {
        'project_name': inputs['vRAproject_name'],
        'project_desc': inputs['vRAproject_desc'],
        'refresh_token': vraToken
        }
        
    hclVars = {
        'project_admins': inputs['vRAproject_admins'],
        'project_members': inputs['vRAproject_members']
        }
        
    for inputVar in inputVars:
        
        payload = {  
                "data": {
                    "type":"vars",
                    "attributes": {
                        "key": inputVar,
                        "value":inputVars[inputVar],
                        "category":"terraform",
                        "hcl":False,
                        "sensitive":False
                        },
                    "relationships": {
                         "workspace": {
                            "data": {
                                "id": workspaceId,
                                "type":"workspaces"
                                }
                            }
                        }
                    }
                }
        
        #print(json.dumps(payload, indent=2) )
        
        varsUri = tfAPIUri + "/vars"
        
        try:
            results = requests.request( method="POST",
                                    url=varsUri, 
                                    headers=headers,
                                    data=json.dumps(payload)
                                  )
                                    
            response = results.json()
            print(response)
            
        except KeyError as error:
            raise Exception("There was an error with getting the variables. URL: " + varsUri + ", " + response + ": " + str(results))
        
        except Exception as error:
            print("There was a problem with getting the variables: " + str(error))
            raise Exception("There was an error with getting the variables: " + str(error))
    
    for hclVar in hclVars:
        
        payload = {  
                "data": {
                    "type":"vars",
                    "attributes": {
                        "key": hclVar,
                        "value":hclVars[hclVar],
                        "category":"terraform",
                        "hcl":True,
                        "sensitive":False
                        },
                    "relationships": {
                         "workspace": {
                            "data": {
                                "id": workspaceId,
                                "type":"workspaces"
                                }
                            }
                        }
                    }
                }
        
        #print(json.dumps(payload, indent=2) )
        
        varsUri = tfAPIUri + "/vars"
        
        try:
            results = requests.request( method="POST",
                                    url=varsUri, 
                                    headers=headers,
                                    data=json.dumps(payload)
                                  )
                                    
            response = results.json()
            print(response)
            
        except KeyError as error:
            raise Exception("There was an error with getting the variables. URL: " + varsUri + ", " + response + ": " + str(results))
        
        except Exception as error:
            print("There was a problem with getting the variables: " + str(error))
            raise Exception("There was an error with getting the variables: " + str(error))