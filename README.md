# 🕹️ ReTrOGPT

**ReTrOGPT** is a nostalgic, retro-themed adaptation of **GPT-2**, built as a homebrew project. It features a simulated BIOS boot sequence and CRT terminal interface, all wrapped in a vintage aesthetic.

> 🚧 **Note:** A custom-trained GPT-2 model is currently under construction and will soon replace the temporary Hugging Face-hosted model.

---

## 📦 Clone the Repository

```bash
git clone https://github.com/nav-jk/ReTrOGPT.git
```
# 🚀 Running the Project
##🖥️ Frontend Setup (React + CRT Terminal)

```
cd gpt
npm install react react-dom crt-terminal
npm run dev

```

- Tech Stack: React, CRT-Terminal
- Interface: Classic terminal with CRT-style visuals
- Features: Typewriter animation, retro UI, interactive boot screen

##⚙️ Backend Setup (FastAPI)
```
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```
- Framework: FastAPI
- Port: 3000
- Dev Mode: Hot reload enabled

###⚠️ Model Status
- 🧪 Currently Using: A placeholder GPT-2 model hosted on Hugging Face
- 🔧 Coming Soon: A fully custom-trained GPT-2 model built and fine-tuned by the project author
