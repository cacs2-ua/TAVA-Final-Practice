# VIBE VS Code / WSL / Docker deployment bundle

Open `VIBE_Docker_Deployment.ipynb` in VS Code from WSL Ubuntu 20.04.

The notebook creates:
- a Dockerfile for VIBE Ubuntu 18.04 runtime,
- helper tools for inspecting VIBE outputs,
- metric utilities for MPJPE, PA-MPJPE, PVE, beta error, PCK, and acceleration error.

The notebook itself controls Docker from WSL; VIBE runs inside Docker.
