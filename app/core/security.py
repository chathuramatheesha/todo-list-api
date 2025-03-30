from passlib.hash import bcrypt


# Hash class to handle password hashing and verification
class Hash:
    # Static method to hash a password using bcrypt
    @staticmethod
    def get_hash_password(password: str) -> str:
        return bcrypt.hash(password)  # Hash the password

    # Static method to verify if the given plain password matches the hashed password
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(
            plain_password, hashed_password
        )  # Verify the hashed password
