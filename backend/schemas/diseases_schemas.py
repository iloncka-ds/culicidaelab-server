from pydantic import BaseModel


class DiseaseBase(BaseModel):
    name: str | None = None
    description: str | None = None
    symptoms: str | None = None
    treatment: str | None = None
    prevention: str | None = None
    prevalence: str | None = None
    image_url: str | None = None
    vectors: list[str] | None = []


class Disease(DiseaseBase):
    id: str

    class Config:
        from_attributes = True


class DiseaseListResponse(BaseModel):
    count: int
    diseases: list[Disease]
