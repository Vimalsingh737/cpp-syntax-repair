from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from model import Decoder, repair, torch

root=Path(__file__).resolve().parent
torch.set_num_threads(1)
model=Decoder()
model.load_state_dict(torch.load(root/"repair.pt",map_location="cpu",weights_only=True))
model.eval()
app=FastAPI()
class Request(BaseModel):
    code: str=Field(min_length=1,max_length=300)

@app.post("/api/repair")
def suggest(req:Request):
    if not req.code.strip() or "\n" in req.code:
        raise HTTPException(422,"Enter a single nonempty line.")
    try:
        return {"suggestion":repair(model,req.code)}
    except ValueError as error:
        raise HTTPException(422,str(error))

app.mount("/",StaticFiles(directory=root/"frontend"/"dist",html=True),name="frontend")
