import re
import torch
from torch import nn

# The raw tokens keep their original spelling and spacing for reconstruction.
def tokenize(text):
    return re.findall(r'<<|>>|==|<=|>=|\w+|[^\w\s]|\s+', text)

SYMBOLS = ["PAD","START","SEP","END","NAME","NUMBER","SPACE","OTHER","cout","endl","if","return","<","<<",">",">>","[","]","(",")",";","=","+","cin","while","for","int","long","double","auto","bool","break","continue","{","}",",","-","==","++","<=",">="]
ACTIONS = ["copy","double_less","close_index","end_statement","close_call","double_greater"]
VOCAB = {t:i for i,t in enumerate(SYMBOLS + ACTIONS)}

def symbol(t):
    if t.isspace(): return "SPACE"
    if t in SYMBOLS[9:]: return t
    if t.isidentifier(): return "NAME"
    if t.isdigit(): return "NUMBER"
    return "OTHER"

def prefix(tokens):
    return [VOCAB["START"]] + [VOCAB[symbol(t)] for t in tokens] + [VOCAB["SEP"]]

class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(len(VOCAB), 144)
        self.position = nn.Embedding(192, 144)
        layer = nn.TransformerEncoderLayer(144, 4, 576, dropout=0, batch_first=True)
        # A causal mask turns this self-attention stack into a GPT-style decoder.
        self.blocks = nn.TransformerEncoder(layer, 4,enable_nested_tensor=False)
        self.output = nn.Linear(144,len(ACTIONS))

    def forward(self, ids):
        n = ids.shape[1]
        x = self.embedding(ids) + self.position(torch.arange(n,device=ids.device))
        mask = torch.ones(n,n,device=ids.device,dtype=torch.bool).triu(1)
        return self.output(self.blocks(x,mask=mask))

def render(token, action):
    if action == "double_greater": return ">>"
    if action == "double_less": return "<<"
    if action == "close_index": return token + "]"
    if action == "end_statement": return token + ";"
    if action == "close_call": return token + ")"
    return token

@torch.inference_mode()
def repair(model, text):
    raw = tokenize(text)
    tokens = [t for t in raw if not t.isspace()]
    if not tokens or len(tokens)>60: raise ValueError("Use 1 to 60 tokens.")
    seq = prefix(tokens)
    output = []
    for token in tokens + [""]:
        seq.append(VOCAB[symbol(token) if token else "END"])
        logits = model(torch.tensor([seq],device=next(model.parameters()).device))
        action = ACTIONS[int(logits[0,-1].argmax())]
        output.append(render(token,action))
        seq.append(VOCAB[action])
    parts = iter(output[:-1])
    return "".join(t if t.isspace() else next(parts) for t in raw) + output[-1]
