from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, ExpiredSignatureError, JWTError
from datetime import datetime, timezone, timedelta
from typing import Annotated

from app.db.database import get_db
from app.db.models import User
from app.schemas.user_schema import UserIn
from app.core.security import Hash
from app.core.config import config

# OAuth2PasswordBearer is used to define the token URL for obtaining the OAuth2 password-based bearer token
# It will automatically handle the validation of the token
oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Exception that will be raised when credentials are invalid or missing (Unauthorized request)
# It returns a 401 Unauthorized response with a relevant message and an authentication header
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,  # HTTP Status Code 401 (Unauthorized)
    detail="Could not validate credentials",  # Message indicating invalid credentials
    headers={
        "WWW-Authenticate": "Bearer"
    },  # Header indicating that a Bearer token is required
)


# * GET A USER by email
# Function to retrieve a user from the database by their email.
# It performs a query using SQLAlchemy's select statement to find a user whose email matches the provided email.
# The result is a single user object, and if no user is found, it returns None.
async def get_user_by_email(email: str, db: AsyncSession) -> User:
    # Querying the database for a user with the given email using SQLAlchemy's 'select' and 'where' methods
    user = await db.scalar(select(User).where(User.email == email))

    # Returning the found user, or None if no match is found
    return user


# * CREATE A USER
# Function to create a new user in the database.
# This function first checks if a user already exists with the provided email.
# If a user exists, it raises an HTTPException with a conflict error.
# Then, it hashes the password and prepares the user data.
# It inserts the new user into the database and commits the transaction.
# After that, it retrieves the newly inserted user by email to confirm the creation.
# If the user is not found, it raises an HTTPException indicating an issue with the input data.
async def create_user(request: UserIn, db: AsyncSession) -> User:
    # Check if a user with the same email already exists
    if await get_user_by_email(str(request.email), db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User creation failed: User with {request.email} already exists",
        )

    # Prepare the new user data, including hashing the password
    new_user = {
        **request.model_dump(),
        "password": Hash.get_hash_password(request.password),
    }

    # Execute the insert query to add the new user to the database
    await db.execute(
        insert(User).values(new_user)
    )  # .returning(User)) # returning works on (sqlite, postgresql)
    await db.commit()

    # Retrieve the inserted user from the database to confirm successful creation
    inserted_user = await get_user_by_email(request.email, db)

    # If the inserted user is not found, raise an exception indicating a failure
    if not inserted_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User creation failed: Please ensure all required fields are provided",
        )

    # Return the successfully created user
    return inserted_user


# * GET A USER by email
# Function to retrieve a user from the database by their email.
# This function calls another function `get_user_by_email` to fetch the user.
# If the user is not found, it raises an HTTPException with a 404 Not Found status
# and a message indicating the user could not be found.
# If the user is found, it returns the user object.
async def get_user(email: str, db: AsyncSession) -> User:
    # Attempt to retrieve the user by email from the database
    user = await get_user_by_email(email, db)

    # If no user is found, raise an HTTP exception with a 404 status code
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User selection failed: User not found",
        )

    # Return the found user object
    return user


# Function to get the expiration time for the access token.
# This function retrieves the expiration time in minutes for the access token
# from the configuration (assumed to be stored in the `config` object).
# The value returned by this function is used when creating or validating
# access tokens to set their expiration period.
def access_token_expire_minutes() -> int:
    # Return the expiration time (in minutes) for the access token
    return config.ACCESS_TOKEN_EXPIRE_MINUTES


# Function to create an access token (JWT) for the provided email.
# This function generates a JSON Web Token (JWT) for the specified user email,
# including an expiration time. The token is signed using a secret key and algorithm
# from the application configuration.
def create_access_token(email: str) -> str:
    # Calculate the expiration time for the access token
    # The token will expire after the specified number of minutes
    # from the current UTC time.
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=access_token_expire_minutes()
    )

    # Prepare the payload (JWT data), which includes:
    # - 'sub': The subject (user's email).
    # - 'exp': Expiration time for the token.
    jwt_data = {"sub": email, "exp": expire}

    # Encode the JWT with the provided data, using the secret key and algorithm.
    # The token is signed, ensuring its authenticity.
    encoded_jwt = jwt.encode(
        jwt_data,
        key=config.SECRET_KEY,  # Secret key for signing the token
        algorithm=config.ALGORITHM,  # Algorithm used for signing the token (e.g., 'HS256')
    )

    # Return the generated and signed JWT token.
    return encoded_jwt


# Function to authenticate a user by verifying their email and password.
# This function checks whether a user exists with the provided email,
# and verifies that the provided password matches the stored hashed password.
# If any of the checks fail, it raises an exception.
async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
    # Retrieve the user from the database by email.
    user = await get_user_by_email(email, db)

    # If the user does not exist, raise a credentials exception.
    # This will prevent unauthorized access.
    if not user:
        raise credentials_exception

    # Verify if the provided password matches the stored password hash.
    # Hash.verify_password is expected to compare the plaintext password
    # with the hashed password stored in the database.
    if not Hash.verify_password(password, user.password):
        raise credentials_exception

    # If both the email and password are valid, return the user object.
    return user


# Function to retrieve the current user from the provided JWT token.
# This function decodes the JWT token, validates its payload,
# and retrieves the associated user from the database.
async def get_current_user(
    token: Annotated[
        str, Depends(oath2_scheme)
    ],  # The JWT token from the Authorization header.
    db: AsyncSession = Depends(get_db),  # The database session injected using Depends.
) -> User:
    try:
        # Decode the JWT token to extract the payload.
        # The payload contains the token's claims (in this case, the user's email).
        payload = jwt.decode(
            token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )

        # Extract the email from the payload (the 'sub' field).
        email = payload.get("sub")

        # If there is no email in the payload, raise credentials_exception (Unauthorized).
        if not email:
            raise credentials_exception

    # If the token has expired, raise an HTTPException with a 401 status code.
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",  # Expired token message
            headers={"WWW-Authenticate": "Bearer"},  # Bearer authentication header.
        ) from e

    # If any JWT error occurs (e.g., malformed token, invalid signature), raise credentials_exception.
    except JWTError as e:
        raise credentials_exception from e

    # Retrieve the user from the database using the email extracted from the token.
    user = await get_user_by_email(email, db)

    # If the user is not found in the database, raise credentials_exception (Unauthorized).
    if not user:
        raise credentials_exception

    # If everything is valid (valid token, valid email, and existing user), return the user.
    return user
