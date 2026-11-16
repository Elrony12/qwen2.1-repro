# -*- coding: utf-8 -*-
"""Frame-by-frame face swap of a video onto a source face using insightface inswapper.
usage: python faceswap.py <video> <src_image> <outdir>
"""
import os, sys, glob, shutil
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model

VIDEO = sys.argv[1]
SRC = sys.argv[2]
OUT = sys.argv[3]

ROOT = "/root/autodl-tmp/ComfyUI/models/insightface"
SWAPPER = "/root/ComfyUI/models/insightface/inswapper_128.onnx"

os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, "*.png")):
    os.remove(f)

app = FaceAnalysis(name="buffalo_l", root=ROOT, providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
app.prepare(ctx_id=0, det_size=(640, 640))
swapper = get_model(SWAPPER, providers=["CUDAExecutionProvider", "CPUExecutionProvider"])

src_img = cv2.imread(SRC)
if src_img is None:
    raise SystemExit("cannot read source image: " + SRC)
src_faces = app.get(src_img)
if not src_faces:
    raise SystemExit("no face in source")
src_face = max(src_faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
print("source face bbox", src_face.bbox.tolist(), "det_score", float(src_face.det_score), flush=True)

cap = cv2.VideoCapture(VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
n = 0
missed = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    faces = app.get(frame)
    if faces:
        # swap the largest face only (single-person shots)
        face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        frame = swapper.get(frame, face, src_face, paste_back=True)
    else:
        missed += 1
    cv2.imwrite(os.path.join(OUT, "f_%04d.png" % n), frame)
    n += 1

cap.release()
print("frames", n, "missed", missed, "fps", fps, flush=True)
