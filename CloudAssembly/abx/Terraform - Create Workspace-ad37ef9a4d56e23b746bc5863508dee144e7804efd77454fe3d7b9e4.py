from botocore.vendored import requests
import json
import boto3
client = boto3.client('ssm','ap-southeast-2') ##AWS SSM

def handler(context, inputs):
    url = inputs['baseURI'] + "/organizations/" + inputs['tfOrgName'] + "/workspaces"
    
    tfToken = client.get_parameter(Name="tfToken",WithDecryption=True) ##AWS SSM
    token = 'Bearer ' + tfToken['Parameter']['Value']
    
    headers = {'Content-type': 'application/vnd.api+json', 'Accept': 'application/json', 'Authorization': token }
    method = "POST"
    payload = {
                "data": {
                "attributes": {
                "name": inputs['vRAproject_name'],
                "terraform_version": inputs['tfVersion'],
                "working-directory": inputs['repo-workingDir'],
                "auto-apply": False,
                "queue-all-runs": False,
                "environment": "default",
                "vcs-repo": {
                    "identifier": inputs['repo-id'],
                    "oauth-token-id": inputs['repo-tokenId'],
                    "default-branch": True,
                    "ingress-submodules": True,
                    "github-app-installation-id": inputs['repo-githubId']
                    }
                },
                "type": "workspaces"
                }
            }
    print("Performing {} request to {}".format(method, url))
    
    print(json.dumps(payload, indent=2))

    try:
        response = requests.request(method=method,
                                    url=url,
                                    headers=headers,
                                    data=json.dumps(payload),
                                    verify=False)

        print("Got {}: {}".format(response.status_code, response.reason))

        # extract header values to plain dict so that json.dumps won't fail
        headers_out = {}
        for k, v in response.headers.items():
            headers_out[k] = v

        #context.outputs["responseBody"] = response.text
        #context.outputs["responseHeaders"] = headers_out
        
        return {'responseBody' : response.text, 'responseHeaders': headers_out}
    except Exception as e:
        print("Got exception: " + str(e))
        raise
