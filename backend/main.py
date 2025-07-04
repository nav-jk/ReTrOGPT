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
    
    
#GPT-2 model form here, add http later



import math
import torch
import tiktoken
import torch.nn as nn
from torch.nn import functional as F
from dataclasses import dataclass

#gptconfig dataclass settings

@dataclass
class gptconfig:
    block_size: int=1024
    vocab_size: int=50257
    n_layer: int=12
    n_head: int=12
    n_embd: int=768

#setting up the decoder class from scratch

#general attention

class Attention(nn.Module):

    def __init__(self,config):
        super().__init__()
        assert config.n_embd % config.n_head == 0, "error"
        #key, query , value vectors projections 
        self.c_attn=nn.Linear(config.n_embd,3*config.n_embd)
        #obtained output in c_proj
        self.c_proj=nn.Linear(config.n_embd,config.n_embd)
        self.n_head=config.n_head
        self.n_embd=config.n_embd
        #setting the buffer tensor (self.mask)
        self.register_buffer("mask",torch.tril(torch.ones(config.block_size,config.block_size)).view(1,1,config.block_size,config.block_size))

    def forward(self,x):
        #batch size, sequence length, embedding dimensions
        B,T,C=x.size()
        qkv=self.c_attn(x)
        #qkv decomposition
        q,k,v=qkv.split(self.n_embd,dim=2)
        #modifying the dimensions to match the below scheme
        #(batch size, number of heads, sequence length, head size)
        k=k.view(B,T,self.n_head,C//self.n_head).transpose(1,2) 
        q=q.view(B,T,self.n_head,C//self.n_head).transpose(1,2) 
        v=v.view(B,T,self.n_head,C//self.n_head).transpose(1,2)
        #attention (attention=softmax(q*k)*v
        att=(q@k.transpose(-2,-1))*(1./math.sqrt(k.size(-1)))
        #masking the future tokens and changing zeros to -inf to softmax
        att=att.masked_fill(self.mask[:,:,:T,:T]==0,float('-inf'))
        att=F.softmax(att,dim=-1)
        y=att@v
        y=y.transpose(1,2).contiguous().view(B,T,C)
        #output probability
        y=self.c_proj(y)
        return y

#Feed forward net (multi layer perceptron)

class MLP(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.c_fc=nn.Linear(config.n_embd,4*config.n_embd)
        self.gelu=nn.GELU(approximate='tanh')
        self.c_proj=nn.Linear(4*config.n_embd,config.n_embd)

    def forward(self, x):
        x=self.c_fc(x)
        x=self.gelu(x)
        x=self.c_proj(x)
        return x


class Block(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.ln_1=nn.LayerNorm(config.n_embd)
        self.attn=Attention(config)  
        self.ln_2=nn.LayerNorm(config.n_embd)
        self.mlp=MLP(config)

    def forward(self, x):
        x=x+self.attn(self.ln_1(x))
        x=x+self.mlp(self.ln_2(x))
        return x
    
#Decoder only Transformer 

class GPT(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.config=config
        self.transformer=nn.ModuleDict(dict(
            wte=nn.Embedding(config.vocab_size,config.n_embd),
            wpe=nn.Embedding(config.block_size,config.n_embd),
            h=nn.ModuleList([Block(config) for _ in range(config.n_layer)]),
            ln_f=nn.LayerNorm(config.n_embd),
            ))
        #projecting the last layer on to the vocab size
        self.lm_head=nn.Linear(config.n_embd,config.vocab_size,bias=False)

    def forward(self,idx):
        B,T=idx.size()
        assert T<=self.config.block_size, "Error"
        pos=torch.arange(0,T,dtype=torch.long,device=idx.device)
        pos_emb=self.transformer.wpe(pos)
        tok_emb=self.transformer.wte(idx)
        x=tok_emb+pos_emb
        for block in self.transformer.h:
            x=block(x)
        x=self.transformer.ln_f(x)
        logits=self.lm_head(x)
        return logits

    #loading GPT-2 model weights from huggingface
    @classmethod
    def from_pretrained(cls,model_type):
        assert model_type in {'gpt2','gpt2-medium','gpt2-large','gpt2-xl'}
        from transformers import GPT2LMHeadModel
        #124M,350M,774M,1558M model configurations
        #the other models can be loaded in similarly after gptconfig() is modified
        config_args={
            'gpt2':dict(n_layer=12,n_head=12,n_embd=768),
            'gpt2-medium':dict(n_layer=24,n_head=16,n_embd=1024),
            'gpt2-large':dict(n_layer=36,n_head=20,n_embd=1280),
            'gpt2-xl':dict(n_layer=48,n_head=25,n_embd=1600),
        }[model_type]
        config_args['vocab_size']=50257
        config_args['block_size']=1024
        config_args['bias']=True
        config=gptconfig()
        model=GPT(config)
        sd=model.state_dict()
        sd_keys=sd.keys()
        sd_keys=[k for k in sd_keys if not k.endswith('.attn.bias')]
        #had to use the next extra line because of my stupid naming convention
        sd_keys=[k for k in sd_keys if not k.endswith('.attn.mask')]

        #loading the huggingface model
        model_hf=GPT2LMHeadModel.from_pretrained(model_type)
        sd_hf=model_hf.state_dict()

        sd_keys_hf=sd_hf.keys()
        sd_keys_hf=[k for k in sd_keys_hf if not k.endswith('.attn.masked_bias')] 
        sd_keys_hf=[k for k in sd_keys_hf if not k.endswith('.attn.bias')]
        #Manual transposition of a few weights to adjust to our model
        transposed=['attn.c_attn.weight','attn.c_proj.weight','mlp.c_fc.weight','mlp.c_proj.weight']

        assert len(sd_keys_hf)==len(sd_keys), "Mismatch observed"
        #copy the weights into our model params (sd_keys_hf to sd_keys)
        for k in sd_keys_hf:
            if any(k.endswith(w) for w in transposed):
                assert sd_hf[k].shape[::-1]==sd[k].shape
                with torch.no_grad():
                    sd[k].copy_(sd_hf[k].t())
            else:
                assert sd_hf[k].shape==sd[k].shape
                with torch.no_grad():
                    sd[k].copy_(sd_hf[k])
        return model


model=GPT.from_pretrained('gpt2')
model.eval()

#number of continuations to generate, the maximum length of each of them and an example prompt
num_sequences=4
max_length=30
example_prompt="hello, good morning"

#using tiktoken to encode our example prompt
encodings=tiktoken.get_encoding('gpt2')
tokens=encodings.encode(example_prompt)
tokens=torch.tensor(tokens,dtype=torch.long)
tokens=tokens.unsqueeze(0).repeat(num_sequences,1)
x=tokens

#intialize a seed and run the input tokens through the model
torch.manual_seed(42)
while x.size(1)<max_length:
    with torch.no_grad():
        logits=model(x)
        #logits to be the last layer's projection
        logits=logits[:,-1,:]
        probs=F.softmax(logits,dim=-1)
        #sampling the top 50 tokens (B,50)
        topk_probs,topk_indices=torch.topk(probs,50,dim=-1)
        #a token from the topk probabilities(B,1)
        ix=torch.multinomial(topk_probs,1)
        #gather the indices and append it to the sequence
        xcol=torch.gather(topk_indices,-1,ix)
        x=torch.cat((x,xcol),dim=1)

#printing the continuations
for i in range(num_sequences):
    tokens=x[i,:max_length].tolist()
    decoded=encodings.decode(tokens)
    print(f"{i+1} ==> {decoded}")
