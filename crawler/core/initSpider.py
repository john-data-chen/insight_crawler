
class initDefault(object):
    def __init__(self):
        pass

    def check_login_response(self, response):
        return "self.initialized()"

    def login(self, response):
        return "FormRequest.from_response(response, formdata={},\
            callback=self.check_login_response)"
