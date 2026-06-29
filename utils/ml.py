"""
Model: jdelgado2002/diabetic_retinopathy_detection
Hugging Face da fastai .pkl formatida saqlangan ResNet-50 model.
"""

import io
from pathlib import Path
from typing import Tuple
from data.config import HF_TOKEN

_learner = None
MODEL_PATH = Path("model.pkl")
HF_MODEL_REPO = "jdelgado2002/diabetic_retinopathy_detection"
HF_MODEL_FILE = "model.pkl"


def load_model():
    global _learner
    if _learner is not None:
        return

    try:
        from fastai.vision.all import load_learner
    except ImportError:
        raise RuntimeError("fastai o'rnatilmagan. 'pip install fastai' buyrug'ini bajaring.")

    if not MODEL_PATH.exists():
        print(f"Model yuklab olinmoqda: {HF_MODEL_REPO}/{HF_MODEL_FILE} ...")
        try:
            from huggingface_hub import hf_hub_download
            downloaded = hf_hub_download(
                repo_id=HF_MODEL_REPO,
                filename=HF_MODEL_FILE,
                local_dir=".",
                token=HF_TOKEN,
            )
            print(f"Model saqlandi: {downloaded}")
        except Exception as e:
            raise RuntimeError(f"Modelni yuklab bo'lmadi: {e}")

    # model.pkl custom funksiyalarni __main__ dan izlaydi.
    # DummyModule har qanday nomni so'raganda placeholder qaytaradi.
    import sys, types

    class _DummyModule(types.ModuleType):
        def __getattr__(self, _):
            def _placeholder(*args): return args[0] if args else None
            return _placeholder

    _real_main = sys.modules["__main__"]
    sys.modules["__main__"] = _DummyModule("__main__")
    try:
        _learner = load_learner(MODEL_PATH, cpu=True)
    finally:
        sys.modules["__main__"] = _real_main
    print("Model muvaffaqiyatli yuklandi.")


def predict_image(image_bytes: bytes) -> Tuple[int, float, list]:
    from fastai.vision.all import PILImage

    if _learner is None:
        load_model()

    img = PILImage.create(io.BytesIO(image_bytes))
    pred_class, pred_idx, probs = _learner.predict(img)

    diagnosis = int(pred_idx)
    probabilities = probs.tolist()
    confidence = float(probs[pred_idx])

    return diagnosis, confidence, probabilities
