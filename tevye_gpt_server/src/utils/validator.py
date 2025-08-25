class Validator:

    def email(self, email: str) -> bool:
        return "@" in email and "." in email.split("@")[-1]


validate = Validator()
