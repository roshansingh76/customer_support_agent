from pydantic import BaseModel,ConfigDict,EmailStr,Field




class UserCreate(BaseModel):
      email:EmailStr
      password:str=Field(min_length=8)
      name:str=Field(max_length=200)


class UserLogin(BaseModel):
      email:EmailStr
      password:str=Field(min_length=8)
             
class UserOut(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id:int
        email:EmailStr
        name:str=Field(max_length=200)

class Token(BaseModel):
       access_token:str
       token_type:str="bearer"