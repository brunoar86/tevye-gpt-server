class Validator:

    def validate_email(self, email: str) -> bool:
        return "@" in email and "." in email.split("@")[-1]
