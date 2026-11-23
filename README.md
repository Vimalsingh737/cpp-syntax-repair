---
title: Cpp Syntax Repair
sdk: docker
app_port: 7860
---

# C++ Syntax Repair
A causal Transformer reads a broken C++ line and generates token edits. FastAPI serves the React frontend and POST /api/repair on the same port. User input is processed as text.

## Train
Upload CppRepair.ipynb to Google Colab and select Runtime → Run all. CPU works. Download repair.pt from the final cell and replace the checkpoint in this folder to use your run.

## Windows / VS Code
Install Python 3.12 x64 and Node.js 22. Extract the ZIP, open the folder containing Dockerfile, and run in PowerShell:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
cd frontend
npm install
npm run build
cd ..
.\.venv\Scripts\python -m uvicorn app:app --port 7860
```
Open http://localhost:7860. Try cout<a[j]<endl or if(a[j]<limit). Rebuild the frontend after editing React.

## GitHub
Create an empty repository called cpp-syntax-repair, replace YOUR_NAME below and run these commands in the project root.
```bash
git init
git add .
git commit -m "Add C++ syntax repair model and web app"
git branch -M main
git remote add origin https://github.com/YOUR_NAME/cpp-syntax-repair.git
git push -u origin main
```

## Free deployment
Open https://huggingface.co/new-space and create a public Docker Space with the blank template and free CPU Basic hardware. Upload this project's contents to the Space repository. Keep Dockerfile, README.md (including its YAML header), app.py, model.py, requirements.txt and repair.pt at the root. Preserve the frontend subdirectory. Commit and wait for Running. Test the App tab from a signed-out browser. Link the Space and GitHub repo on your resume. Free Spaces may sleep. See https://huggingface.co/docs/hub/spaces-sdks-docker .

## Results and scope
144 synthetic training lines; 36 test lines with a new array name but shared sentence patterns and normalized identifiers. Exact match 36/36; copy-input baseline 4/36. All 36 passed g++ syntax checks in a prepared wrapper. This checks syntax only. The supported patterns are array output statements and array-versus-limit comparisons. Evaluate independently on real failed submissions before claiming performance on general C++.
