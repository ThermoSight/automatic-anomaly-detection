# model_trainning 

Purpose
- Training and inference helpers for PatchCore-based anomaly detection (configs, scripts, and dataset helpers).

Required layout
- `model_trainning/configs/patchcore_transformers.yaml` — main experiment config
- `model_trainning/dataset/` with `train/normal`, `test/normal`, `test/faulty`

Quick commands
- Train (anomalib):
  `anomalib train --config model_trainning/configs/patchcore_transformers.yaml`
- Single-image inference:
  `python model_trainning/patchcore_single_image.py path\to\image.jpg`
- Folder inference:
  `python model_trainning/patchcore_inference.py`
- YAML-driven inference (recommended):
  `python model_trainning/patchcore_api_inference.py`
- Batch scoring to CSV:
  `python model_trainning/batch_patchcore_infer.py`

Outputs
- Checkpoints: `results/.../*.ckpt`
- Masks: `api_inference_pred_masks/`, `inference_masks/`
- Filtered images: `api_inference_filtered/`
- Batch CSV: `patchcore_batch_scores.csv`

Notes
- Ensure `torch` and `anomalib` versions are compatible (install correct `torch` wheel for your CUDA/CPU setup).
- Make checkpoint paths configurable (env var or small `config.py`) before production runs.
- Use `model_trainning/scripts/` for dataset preparation and augmentation helpers.
\




