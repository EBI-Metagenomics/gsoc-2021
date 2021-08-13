"""Cookie Auther implementation of Auther."""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from bcrypt import checkpw, gensalt, hashpw

from conductor import DBSession, global_config
from conductor.auther.base import BaseAuther
from conductor.models.protagonist import ProtagonistDB
from conductor.schemas.api.auth.post import AuthUserCreds
from conductor.schemas.api.user.post import UserCreate
from conductor.schemas.user import User

from flask.wrappers import Request

import jwt

from logzero import logger

from sqlalchemy import select


class CookieAuther(BaseAuther):
    """Cookie Auther."""

    def register_user(
        self: "BaseAuther", user_create_list: List[UserCreate]
    ) -> ProtagonistDB:
        """Register user.

        Args:
            user_create_list (List[UserCreate]): List of users to register

        Raises:
            Exception: error

        Returns:
            List(ProtagonistDB): List of registered users
        """
        with DBSession() as session:
            try:
                ProtagonistDB.bulk_create(
                    [
                        {
                            "password": hashpw(
                                user_create["password"].encode(), gensalt()
                            ),
                            **user_create["user"],
                        }  # noqa: E501
                        for user_create in user_create_list
                    ],
                    session,
                )
                return [
                    {**user_create["user"]} for user_create in user_create_list
                ]  # noqa: E501
            except Exception as e:
                session.rollback()
                logger.error(f"Unable to register users due to {e}")
                raise e

    def login_user(
        self: "BaseAuther", user_creds: AuthUserCreds
    ) -> Optional[Tuple[ProtagonistDB, str]]:
        """Login user.

        Args:
            user_creds (AuthUserCreds): user creds

        Raises:
            Exception: error

        Returns:
            Optional[Tuple[ProtagonistDB, str]]: Tuple containing user and cookie or None  # noqa: E501
        """
        with DBSession() as session:
            try:
                # Find user
                stmt = select(ProtagonistDB).where(
                    ProtagonistDB.email == user_creds.email
                )
                user_list: List[ProtagonistDB] = (
                    session.execute(stmt).scalars().all()
                )  # noqa: E501
                # return early if user not found
                if len(user_list) == 0:
                    return None

                # Check password hash
                if checkpw(
                    user_creds.password.encode(), user_list[0].password
                ):  # noqa: E501
                    # Create cookie and return user and cookie
                    user_cookie = jwt.encode(
                        {
                            "exp": datetime.utcnow()
                            + timedelta(
                                minutes=global_config.ACCESS_TOKEN_EXPIRE_MINUTES  # noqa: E501
                            ),
                            "sub": user_list[0].email,
                            "email": user_list[0].email,
                            "name": user_list[0].name,
                            "organisation": user_list[0].organisation,
                        },
                        global_config.SECRET_KEY,
                    )
                    return (user_list[0], user_cookie)
                else:
                    return None
            except Exception as e:
                session.rollback()
                logger.error(f"Unable to login user due to: {e}")
                raise e

    def logout_user(self: "BaseAuther") -> None:
        """Logout user."""
        pass

    def extract_user_from_flask_req(
        self: "BaseAuther", request: Request
    ) -> Optional[ProtagonistDB]:
        """Extract user from flask request.

        Args:
            request (Request): Instance of flask request

        Raises:
            Exception: error

        Returns:
            Optional[ProtagonistDB]: Instance of ProtagonistDB or None
        """
        with DBSession() as session:
            user_cookie_encoded = request.cookies.get(global_config.FLASK_APP)
            # return early if cookie not found in request
            if user_cookie_encoded is None:
                return None
            # try to decode the cookie
            try:
                user_cookie_decoded = jwt.decode(
                    user_cookie_encoded, global_config.SECRET_KEY
                )
            except jwt.DecodeError:
                # return none if failed to decode cookie
                return None
            except Exception as e:
                logger.error(f"Unable to decode cookie due to: {e}")
                raise e

            # Fetch and return user if present or None
            stmt = select(ProtagonistDB).where(
                ProtagonistDB.email == user_cookie_decoded["email"]
            )
            user_list: List[ProtagonistDB] = (
                session.execute(stmt).scalars().all()
            )  # noqa: E501
            # return early if user not found
            if len(user_list) == 0:
                return None
            else:
                return user_list[0]

    def authorize_user(
        self: "BaseAuther", user: User, request: Request
    ) -> bool:  # noqa: E501
        """Authorize user actions on resources.

        Args:
            user (User): Instance of User
            request (Request): Instance of Flask Request

        Returns:
            bool: Authorization decision
        """
        return True
