from pydantic import BaseModel


class Team(BaseModel):
    id: int
    name: str
    city: str
    stadium: str
    founded_year: int


class GetTeamsResponse(BaseModel):
    teams: list[Team]


class TeamMessageResponse(BaseModel):
    message: str
