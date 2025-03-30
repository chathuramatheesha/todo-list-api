from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.database import get_db
from app.schemas.user_schema import UserIn, UserOut
from app.crud import user_crud as crud

router = APIRouter()

# db_dependency is an alias for the asynchronous database session
# It is used to retrieve the database session (via Depends) from the get_db function
db_dependency: AsyncSession = Depends(get_db)


# POST /register
@router.post(
    "/register",  # This route handles POST requests to the "/register" endpoint
    response_model=UserOut,  # The response will conform to the UserOut model, which defines the structure of the returned user data.
    status_code=status.HTTP_201_CREATED,  # When the user is successfully created, the response will return HTTP status 201 (Created).
)
async def register(user: UserIn, db=db_dependency):
    """
    This endpoint is used to register a new user.

    - It receives user data (in the form of a UserIn model) and a database session (db).
    - The function handles user creation by calling the create_user function in the CRUD module.

    Steps:
    - The user data is validated.
    - The password is hashed before storage.
    - The new user is inserted into the database.
    """
    # Calls the create_user function in the CRUD module to handle user creation.
    # The function will handle validation, hashing the password, and inserting the user into the database.
    # Returns the newly created user after insertion into the database.
    return await crud.create_user(user, db)


# POST /token
# This route handles POST requests to "/token" for logging in and generating access tokens.
@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    # This dependency extracts form data from the request body.
    db=db_dependency,  # Injects the database session into the function using the db_dependency.
):
    # Authenticate the user by calling the authenticate_user function from CRUD operations.
    # The email is retrieved from form_data.username and the password from form_data.password.
    user = await crud.authenticate_user(
        email=form_data.username,  # The 'username' field from the form data represents the email.
        password=form_data.password,  # The 'password' field from the form data represents the password.
        db=db,  # Pass the database session to authenticate the user.
    )

    # After the user is authenticated, generate an access token.
    access_token = crud.create_access_token(user.email)

    # Return the access token and token type as part of the response.
    # This allows the user to access protected endpoints with this token.
    return {"access_token": access_token, "token_type": "bearer"}
