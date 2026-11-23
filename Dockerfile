FROM node:22-alpine AS ui
WORKDIR /ui
COPY frontend/package.json .
RUN npm install
COPY frontend/ .
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py model.py repair.pt ./
COPY --from=ui /ui/dist ./frontend/dist
USER 1000
EXPOSE 7860
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","7860"]
