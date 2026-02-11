# Deploying `Heatmap/` on Hugging Face (Custom Docker)

This folder contains a FastAPI-based backend (`Heatmap/backend_api.py`) used by the SafeSphere project. To deploy this on Hugging Face using a custom Docker container, the repository contains a `Dockerfile` and a small `start.sh` entrypoint.

Quick instructions (locally build and run):

```bash
# from repository root
docker build -t safesphere-heatmap -f Heatmap/Dockerfile .
docker run -e PORT=8000 -p 8000:8000 safesphere-heatmap
```

Notes for Hugging Face:
- HF will build your Dockerfile automatically when you push this repository as a Space using "Custom Dockerfile".
- Ensure you set `SUPABASE_URL` and `SUPABASE_KEY` as repo Secrets in the Space settings (do NOT commit them to the repo).
- The container exposes the port defined by the `PORT` environment variable (defaults to `7860`).

Optional tweaks:
- Reduce worker count or pin versions in `requirements_hf.txt` for stability.
- If you don't need audio/vision ML packages on HF, trim heavy deps (Whisper, torch) to speed builds.
