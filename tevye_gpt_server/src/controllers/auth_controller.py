from tevye_gpt_server.src.utils.validator import validate


class AuthController:

    def __init__(self):
        self.registration_form = None

    def register_user(self, registration_form):
        self.registration_form = registration_form
        self.validate_registration_form()
        return {'Done!'}

    def validate_registration_form(self):
        email_validation = validate.email(self.registration_form.email)

        valid_form = all([email_validation])

        if valid_form:
            return True
        else:
            raise ValueError("Invalid registration form data")


auth = AuthController()
