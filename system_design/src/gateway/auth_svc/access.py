import os, requests

def login(request):
    print(request)
    type(request)
    auth = request.authorization
    if not auth:
        return None, ("Missing Credentials", 401)

    basicAuth  = (auth.username, auth.password)
    print(basicAuth)

    response = requests.post(f"http://${os.environ.get('AUTH_SVC_ADDRESS')}/login", auth=basicAuth)
    print(f'Login Response: {response}')

    if response.status_code == 200:
        return response.txt, None
    else:
        return None, (response.txt, response.status_code)
