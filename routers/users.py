from fastapi import APIRouter, HTTPException, Query, status
from models.users import (
    User,
    GetUsersResponse,
    CreateUserResponse,
    DeleteUserResponse,
)

router = APIRouter()

usuarios: list[User] = [
    User(id=1, name="juan perez"),
    User(id=2, name="pepe sanchez"),
]


@router.get("/user", response_model=GetUsersResponse)
def get_users(
    is_active: bool | None = Query(default=None),
) -> GetUsersResponse:
    filtered_users = usuarios
    if is_active is not None:
        filtered_users = [
            user for user in usuarios if user.is_active == is_active
        ]
    return GetUsersResponse(users=filtered_users)


@router.get("/user/{id}", response_model=User)
def get_user(id: int) -> User:
    for user in usuarios:
        if user.id == id:
            return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado",
    )


@router.delete("/user/{id}", response_model=DeleteUserResponse)
def delete_user(id: int) -> DeleteUserResponse:
    for index, user in enumerate(usuarios):
        if user.id == id:
            usuarios.pop(index)
            return DeleteUserResponse(message="Usuario borrado")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado",
    )


@router.post(
    "/user",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: User) -> CreateUserResponse:
    if any(existing_user.id == user.id for existing_user in usuarios):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese id",
        )
    usuarios.append(user)
    return CreateUserResponse(message="Usuario creado")


@router.put("/user/{id}", response_model=User)
def update_user(id: int, updated_user: User) -> User:
    if updated_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El id de la URL debe coincidir con el id del usuario",
        )

    for index, user in enumerate(usuarios):
        if user.id == id:
            usuarios[index] = updated_user
            return updated_user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado",
    )