"""Prétraitement d'image avant OCR.

Améliore la lisibilité des documents scannés : niveaux de gris, débruitage,
redressement (deskew) et binarisation (Otsu). Un scan tordu / bruité / pâle donne
un OCR médiocre — ces étapes augmentent le taux d'extraction.
"""
from __future__ import annotations
import cv2
import numpy as np
from PIL import Image


def to_gray(img: np.ndarray) -> np.ndarray:
    if img.ndim == 3:
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return img


def denoise(gray: np.ndarray) -> np.ndarray:
    return cv2.medianBlur(gray, 3)


def deskew(gray: np.ndarray) -> np.ndarray:
    """Redresse une image légèrement tournée (angle estimé sur le texte)."""
    inv = cv2.bitwise_not(gray)
    thr = cv2.threshold(inv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thr > 0))
    if len(coords) < 50:
        return gray
    angle = cv2.minAreaRect(coords)[-1]
    if angle > 45:
        angle -= 90
    if abs(angle) < 0.5 or abs(angle) > 15:   # ne pas sur-corriger
        return gray
    h, w = gray.shape
    m = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(gray, m, (w, h), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)


def binarize(gray: np.ndarray) -> np.ndarray:
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def preprocess(img: np.ndarray, do_deskew: bool = True, do_binarize: bool = True) -> np.ndarray:
    g = to_gray(img)
    g = denoise(g)
    if do_deskew:
        g = deskew(g)
    if do_binarize:
        g = binarize(g)
    return g


def preprocess_pil(pil_img: Image.Image, **kw) -> Image.Image:
    """Version pratique : entrée/sortie en image PIL."""
    out = preprocess(np.array(pil_img.convert("RGB")), **kw)
    return Image.fromarray(out)
