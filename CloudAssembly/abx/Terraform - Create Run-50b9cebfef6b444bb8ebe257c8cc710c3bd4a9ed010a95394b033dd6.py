import requests
import json
import time
import sys
import boto3
client = boto3.client('ssm','ap-southeast-2') ##AWS SSM

def handler(context, inputs):
        
    baseUri = inputs['baseUri']
    #tfToken = inputs['tfToken']
    tfToken = client.get_parameter(Name="tfToken",WithDecryption=True)['Parameter']['Value'] ##AWS SSM
    
    tfAPIVersion = inputs['tfAPIVersion']
    tfOrgName = inputs['tfOrgName']
    tfWorkspaceName = inputs['vRAproject_name']
    tfAPIUri = baseUri + "/" + tfAPIVersion 
    headers = {"Accept":"application/json","Content-Type":"application/vnd.api+json","Authorization":"Bearer " + tfToken}
    try:
        tempUri = tfAPIUri + "/organizations/" + tfOrgName + "/workspaces/" + tfWorkspaceName
        results = requests.get(tempUri, headers=headers)
        tfWorkspace = results.json()['data']
        print(results)
    except KeyError as error:
        raise Exception("There was an error with getting the Terraform workspace. URL: " + tempUri + ", " + str(results))
    except Exception as error:
        print("There was a problem with getting the Terraform workspace: " + str(error))
        raise Exception("There was an error with getting the Terraform workspace: " + str(error))
    body = {}
    data = {}
    attributes = {}
    relationships = {}
    relationshipWorkspace = {}
    workspaceData = {}
    
    attributes['is-destroy'] = False
    attributes['message'] = "Queued manually via the API"
    
    data['attributes'] = attributes
    
    workspaceData['type'] = "workspaces"
    workspaceData['id'] = tfWorkspace['id']
    
    relationshipWorkspace['data'] = workspaceData
    
    relationships['workspace'] = relationshipWorkspace
    
    data['relationships'] = relationships
    
    body['data'] = data
    body['type'] = "runs"
    try:
        tempUri = tfAPIUri + "/runs"
        results = requests.post(tempUri,json=body, headers=headers)
        tfRun = results.json()['data']
        print(tfRun['id'])
    except KeyError as error:
        raise Exception("There was an error with creating the run. URL: " + tempUri + ", " + str(results))
    except Exception as error:
        print("There was a problem with creating the Terraform run: " + str(error))
        raise Exception("There was an error with creating the run: " + str(error))

    isPlanned = False
    isFailed = False 
    isPlannedAndFinished = False
    print("Waiting for the plan to finish...")
    while isPlanned != True or isFailed != True:
        try:
            tempUri = tfAPIUri + "/runs/" + tfRun['id']
            results = requests.get(tempUri, headers=headers)
            runDetails = results.json()['data']
            if runDetails['attributes']['status'] == 'planned':
                isPlanned = True
                print("Status of run is: planned")
                break
            if runDetails['attributes']['status'] == "errored":
                print("Status is " + runDetails['attributes']['status'])
                isFailed = True
                break
            if runDetails['attributes']['status'] == "planned_and_finished" :
                isPlannedAndFinished = True
                break
            time.sleep(10)
        except KeyError as error:
            raise Exception("There was an error with getting the run details. URL: " + tempUri + ", " + str(results))
        except Exception as error:
            print("There was a problem with getting the run details: " + str(error))
            raise Exception("There was an error with getting the run details: " + str(error))
    
    if isFailed == True or isPlannedAndFinished == True:
        tempUri = tfAPIUri + "/runs/" + tfRun['id'] + "/plan"
        results = requests.get(tempUri, headers=headers)
        plan = results.json()['data']
        tempUri = plan['attributes']['log-read-url']
        print("Getting " + tempUri)
        results = requests.get(tempUri, headers=headers)
        rawLog = results.json()['data']
        rawLog = rawLog.replace("[0m", "").replace("[1m", "").replace("[32m", "").replace(chr(2), "").replace(chr(27),"").replace("[4m", "").replace("[31m","")
        print(rawLog)
        if isPlannedAndFinished == True:
            planSummary = rawLog[rawLog.index("--\n")+4:len(rawLog)-2]
        if isFailed == True:
            planSummary = rawLog[rawLog.index("Error:"):len(rawLog)-2]
        raise Exception("There was an error with applying the run. Status is: " + runDetails['attributes']['status'] + " Plan summary: " + planSummary)
       
    if isPlanned == True:
        time.sleep(15)
        print("Plan is successful. Trying to apply...")
        print(tfRun['id'])
        isApplied = False
        try:
            tempUri = tfAPIUri + "/runs/" + tfRun['id'] + "/actions/apply"
            body = {
                'comment': 'Test'
            }
            tfApply = requests.post(tempUri, json=body, headers=headers)
            print(tfApply)
        except Exception as error:
            print("There was a problem with applying the run: " + str(error))
            raise Exception("There was an error with applying the run: " + str(error))
        while isApplied != True or isFailed != True:
            try:
                tempUri = tfAPIUri + "/runs/" + tfRun['id']
                results = requests.get(tempUri, headers=headers)
                runDetails = results.json()['data']
                print ("!!!!! " + runDetails['attributes']['status'])
            except KeyError as error:
                raise Exception("There was an error with getting the run-apply details. URL: " + tempUri + ", " + str(results))
            except Exception as error:
                print("There was a problem with getting the run-apply details: " + str(error))
                raise Exception("There was an error with getting the run-apply details: " + str(error))
            if runDetails['attributes']['status'] == "applied":
                isApplied = True
                print("Status of run is: applied")
                break
            if runDetails['attributes']['status'] == "errored":
                print("Status is " + runDetails['attributes']['status'])
                isFailed = True
                break
            time.sleep(10)
        
        if isFailed == True:
            tempUri = tfAPIUri + "/runs/" + tfRun['id'] + "/plan"
            results = requests.get(tempUri, headers=headers)
            plan = results.json()['data']
            tempUri = plan['attributes']['log-read-url']
            results = requests.get(tempUri, headers=headers)
            rawLog = results.json()['data']
            rawLog = rawLog.replace("[0m", "").replace("[1m", "").replace("[32m", "").replace(chr(2), "").replace(chr(27),"").replace("[4m", "").replace("[31m","")
            print(rawLog)
            planSummary = rawLog[rawLog.index("Error:"):len(rawLog)-2]
            raise Exception("There was an error with applying the run. Status is: " + runDetails['attributes']['status'] + " Plan summary: " + planSummary)
            
        if isApplied == True:
            print(runDetails)
            print("Terraform Plan successfully applied.")
            return {"Result":"Terraform Plan successfully applied."}