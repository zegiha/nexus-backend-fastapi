from pydantic import BaseModel, TypeAdapter


class Press(BaseModel):
    name: str
    description: str
    profile_image_url: str
    signature_color: str

press_adapter = TypeAdapter(Press)