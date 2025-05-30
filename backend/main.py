from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS from frontend (adjust the origin if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load GPT-2 model
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)
model.config.pad_token_id = model.config.eos_token_id

class Prompt(BaseModel):
    text: str

@app.post("/generate")
async def generate_text(prompt: Prompt):
    input_ids = tokenizer.encode(prompt.text, return_tensors="pt")
    attention_mask = torch.ones_like(input_ids)
    output = model.generate(
        input_ids,
        attention_mask=attention_mask,
        pad_token_id=model.config.pad_token_id,
        max_length=100,
        do_sample=True
    )
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return {"response": response}
