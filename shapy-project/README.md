# SHAPY deployment package for VS Code + WSL + Docker

Target design:

- Host editor: VS Code connected to WSL Ubuntu 20.04.
- Runtime: Docker container with Ubuntu 18.04, CUDA 10.2, Python 3.8, PyTorch 1.7.1/cu102.
- Main project file: `notebooks/shapy_deployment.ipynb`.

## 1. Prepare the workspace

```bash
cd shapy_docker_vscode_package
bash scripts/00_prepare_workspace.sh
```

## 2. Build the Docker image

```bash
bash scripts/01_build_image.sh
```

## 3. Start Jupyter

```bash
bash scripts/02_run_jupyter.sh
```

Open in VS Code:

```text
http://127.0.0.1:8888/lab?token=shapy
```

In VS Code, open `notebooks/shapy_deployment.ipynb` and select the remote Jupyter server above.

## 4. First notebook execution

Run the notebook cells in order. Cell 3 installs SHAPY dependencies inside the running container.

## 5. Required manual data

Because of licensing, this package does not include SHAPY data, SMPL, or SMPL-X files.

Place the files under:

```text
workspace/shapy/data/body_models/smplx/
workspace/shapy/data/body_models/smpl/
workspace/shapy/data/
```

Expected minimum for the SHAPY regressor:

```text
workspace/shapy/data/body_models/smplx/SMPLX_NEUTRAL.npz
workspace/shapy/data/body_models/smplx/SMPLX_FEMALE.npz
workspace/shapy/data/body_models/smplx/SMPLX_MALE.npz
workspace/shapy/data/trained_models/shapy/SHAPY_A/
workspace/shapy/data/expose_release/
workspace/shapy/data/utility_files/
```

You can obtain SHAPY model data using `workspace/shapy/data/download_data.sh` after registering on the SHAPY website, or by manually downloading `shapy_data.zip` and extracting it into `workspace/shapy/data/`.

## 6. Test Docker GPU visibility

```bash
bash scripts/04_test_gpu.sh
```
