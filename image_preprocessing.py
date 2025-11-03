"""
Préprocessing d'image amélioré pour améliorer la précision OCR
"""

from PIL import Image
import numpy as np
from typing import Optional
import io

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def preprocess_image(
    image: Image.Image,
    enhance_contrast: bool = True,
    denoise: bool = True,
    deskew: bool = True,
    upscale: bool = False,
    target_dpi: int = 300
) -> Image.Image:
    """
    Améliore la qualité d'une image avant OCR
    
    Args:
        image: Image PIL à traiter
        enhance_contrast: Améliorer le contraste
        denoise: Réduire le bruit
        deskew: Corriger l'inclinaison
        upscale: Augmenter la résolution si nécessaire
        target_dpi: DPI cible (défaut: 300)
    
    Returns:
        Image PIL améliorée
    """
    if CV2_AVAILABLE:
        # Convertir PIL vers OpenCV
        img_array = np.array(image.convert('RGB'))
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Conversion en niveaux de gris
        if len(img_cv.shape) == 3:
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_cv
        
        # 1. Désinclinaison (deskew)
        if deskew:
            gray = auto_deskew(gray)
        
        # 2. Réduction du bruit
        if denoise:
            gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # 3. Amélioration du contraste
        if enhance_contrast:
            gray = enhance_contrast_clahe(gray)
        
        # 4. Binarisation adaptative
        gray = adaptive_threshold(gray)
        
        # 5. Upscaling si nécessaire
        if upscale:
            current_dpi = image.info.get('dpi', (72, 72))[0]
            if current_dpi < target_dpi:
                scale_factor = target_dpi / current_dpi
                new_width = int(gray.shape[1] * scale_factor)
                new_height = int(gray.shape[0] * scale_factor)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Convertir back vers PIL
        return Image.fromarray(gray)
    else:
        # Fallback sans OpenCV : améliorations basiques avec PIL
        # Conversion en niveaux de gris
        if image.mode != 'L':
            image = image.convert('L')
        
        # Amélioration du contraste (histogram stretching)
        if enhance_contrast:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
        
        return image


def auto_deskew(image: np.ndarray) -> np.ndarray:
    """
    Corrige automatiquement l'inclinaison d'une image
    """
    if not CV2_AVAILABLE:
        return image
    
    # Détecter les contours
    coords = np.column_stack(np.where(image > 0))
    
    if len(coords) == 0:
        return image
    
    # Calculer l'angle d'inclinaison
    angle = cv2.minAreaRect(coords)[-1]
    
    # Ajuster l'angle
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    # Si l'angle est négligeable, ne pas faire de rotation
    if abs(angle) < 0.5:
        return image
    
    # Rotation
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return rotated


def enhance_contrast_clahe(image: np.ndarray) -> np.ndarray:
    """
    Améliore le contraste avec CLAHE (Contrast Limited Adaptive Histogram Equalization)
    """
    if not CV2_AVAILABLE:
        return image
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)


def adaptive_threshold(image: np.ndarray) -> np.ndarray:
    """
    Binarisation adaptative pour améliorer la lisibilité
    """
    if not CV2_AVAILABLE:
        return image
    
    # Binarisation adaptative
    binary = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    return binary


def should_preprocess(image: Image.Image, min_dpi: int = 200) -> bool:
    """
    Détermine si le préprocessing est nécessaire
    
    Args:
        image: Image à analyser
        min_dpi: DPI minimum requis
    
    Returns:
        True si préprocessing recommandé
    """
    # Vérifier la résolution
    dpi = image.info.get('dpi', (72, 72))[0]
    if dpi < min_dpi:
        return True
    
    # Vérifier la taille (images très petites peuvent bénéficier du preprocessing)
    width, height = image.size
    if width < 800 or height < 600:
        return True
    
    return False





