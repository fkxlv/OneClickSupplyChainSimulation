class Response():
    status_code: int

    def __init__(self, status_code):
        self.status_code = status_code

def send_email(email):
    return Response(200)