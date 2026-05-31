import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os


class MRIPredictor:
    def __init__(self, model_path='models/best_model.pth'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = self._resolve_model_path(model_path)
        self.model = self._load_model()
        self.transform = self._get_transforms()
        self.classes = ['normal', 'sick']

    def _resolve_model_path(self, model_path):
        """Handle relative/absolute paths"""
        if os.path.exists(model_path):
            return model_path

        # Try relative to current file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(base_dir, '..', model_path)

        if os.path.exists(alt_path):
            return alt_path

        raise FileNotFoundError(
            f"Model file not found at {model_path} or {alt_path}\n"
            f"Current directory: {os.getcwd()}"
        )

    def _load_model(self):
        """Load model with proper error handling"""
        try:
            # Create model architecture
            model = models.efficientnet_b0(pretrained=False)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, 2)

            # Load weights
            state_dict = torch.load(self.model_path, map_location=self.device)

            # Handle potential mismatch in state dict keys
            if all(k.startswith('module.') for k in state_dict.keys()):
                state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}

            model.load_state_dict(state_dict)
            model.eval()
            return model.to(self.device)

        except Exception as e:
            raise RuntimeError(
                f"Failed to load model from {self.model_path}\n"
                f"Error: {str(e)}\n"
                "Possible causes:\n"
                "1. Model file is corrupted\n"
                "2. Architecture mismatch\n"
                "3. PyTorch version mismatch"
            )

    def _get_transforms(self):
        return transforms.Compose([
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, image_path):
        """Predict with error handling"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")

            image = Image.open(image_path).convert('RGB')
            image = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(image)
                _, predicted = torch.max(outputs, 1)
                prob = torch.nn.functional.softmax(outputs, dim=1)[0] * 100

            return self.classes[predicted.item()], prob[predicted.item()].item()

        except Exception as e:
            raise RuntimeError(f"Prediction failed for {image_path}: {str(e)}")

    def get_precautions(self, prediction):
        if prediction == 'sick':
            return [
                "1. Consult a cardiologist immediately",
                "2. Reduce salt intake",
                "3. Monitor blood pressure regularly",
                "4. Avoid strenuous activities",
                "5. Follow a heart-healthy diet"
            ]
        return ["No specific precautions needed. Maintain regular checkups."]