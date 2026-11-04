from fastapi import APIRouter, HTTPException, Query, status

from models.teams import GetTeamsResponse, Team, TeamMessageResponse

router = APIRouter()

teams: list[Team] = [
    Team(
        id=1,
        name="River Plate",
        city="Buenos Aires",
        stadium="Monumental",
        founded_year=1901,
    ),
    Team(
        id=2,
        name="Talleres",
        city="Cordoba",
        stadium="Mario Alberto Kempes",
        founded_year=1913,
    ),
]


@router.get("/team")
def get_teams(
    city: str | None = Query(default=None),
) -> GetTeamsResponse:
    if city is None:
        filtered_teams = teams
    else:
        filtered_teams = [
            team for team in teams if team.city.lower() == city.lower()
        ]
    return GetTeamsResponse(teams=filtered_teams)


@router.get("/team/{id}", response_model=Team)
def get_team(id: int) -> Team:
    for team in teams:
        if team.id == id:
            return team
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Equipo no encontrado",
    )


@router.post("/team", response_model=Team, status_code=status.HTTP_201_CREATED)
def create_team(team: Team) -> Team:
    if any(existing_team.id == team.id for existing_team in teams):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un equipo con ese id",
        )
    teams.append(team)
    return team


@router.put("/team/{id}", response_model=Team)
def update_team(id: int, updated_team: Team) -> Team:
    if updated_team.id != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El id de la URL debe coincidir con el id del equipo",
        )

    for index, team in enumerate(teams):
        if team.id == id:
            teams[index] = updated_team
            return updated_team

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Equipo no encontrado",
    )


@router.delete("/team/{id}", response_model=TeamMessageResponse)
def delete_team(id: int) -> TeamMessageResponse:
    for index, team in enumerate(teams):
        if team.id == id:
            teams.pop(index)
            return TeamMessageResponse(message="Equipo eliminado")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Equipo no encontrado",
    )
