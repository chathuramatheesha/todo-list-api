from passlib.hash import bcrypt


class Hash:
    @staticmethod
    def get_hash_password(password: str) -> str:
        return bcrypt.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)
