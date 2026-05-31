import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, ttk
import time

# Modern color scheme
COLORS = {
    'background': '#2E3440',
    'primary': '#5E81AC',
    'secondary': '#81A1C1',
    'text': '#ECEFF4',
    'success': '#A3BE8C',
    'danger': '#BF616A',
    'warning': '#EBCB8B',
    'card': '#3B4252',
    'highlight': '#88C0D0'
}


class MRIPredictor:
    def __init__(self, model_path='models/best_model.pth'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model(model_path)
        self.transform = self._get_transforms()
        self.classes = ['normal', 'sick']

    def _load_model(self, model_path):
        """Load model with comprehensive error handling"""
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {os.path.abspath(model_path)}")

            # Updated to use weights parameter instead of pretrained
            model = models.efficientnet_b0(weights=None)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, 2)

            state_dict = torch.load(model_path, map_location=self.device)
            model.load_state_dict(state_dict)
            model.eval()
            return model.to(self.device)

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")

    def _get_transforms(self):
        return transforms.Compose([
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, image_path):
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")

            image = Image.open(image_path).convert('RGB')
            image = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(image)
                _, predicted = torch.max(outputs, 1)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)[0] * 100

            return {
                'class': self.classes[predicted.item()],
                'confidence': probabilities[predicted.item()].item(),
                'probabilities': {
                    'normal': probabilities[0].item(),
                    'sick': probabilities[1].item()
                },
                'image_path': image_path
            }

        except Exception as e:
            raise RuntimeError(f"Prediction failed for {image_path}: {str(e)}")

    def get_precautions(self, prediction):
        if prediction == 'sick':
            return [
                "➤ Consult a cardiologist immediately",
                "➤ Reduce salt intake (<1.5g/day)",
                "➤ Monitor blood pressure daily",
                "➤ Avoid strenuous exercise",
                "➤ Follow a Mediterranean diet",
                "➤ Quit smoking if applicable",
                "➤ Limit alcohol consumption"
            ]
        return [
            "➤ Maintain regular cardiovascular checkups",
            "➤ Continue healthy lifestyle habits",
            "➤ Exercise 30 minutes daily",
            "➤ Monitor cholesterol levels annually"
        ]


class ModernButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style='Modern.TButton', **kwargs)
        self.configure(padding=6)


class MRIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CardioScan AI - Heart Disease Detection")
        self.root.geometry("1100x750")
        self.root.configure(bg=COLORS['background'])

        # Configure styles
        self.configure_styles()

        # Initialize predictor
        self.predictor = MRIPredictor()

        # Create UI
        self.create_widgets()

        # Initialize variables
        self.image_paths = []
        self.current_index = 0
        self.predictions = []
        self.current_img = None
        self.img_display = None  # Reference to image label

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Background colors
        style.configure('.', background=COLORS['background'], foreground=COLORS['text'])

        # Button styles
        style.configure('Modern.TButton',
                        foreground=COLORS['text'],
                        background=COLORS['primary'],
                        bordercolor=COLORS['primary'],
                        font=('Helvetica', 11, 'bold'),
                        padding=10,
                        relief='flat')
        style.map('Modern.TButton',
                  background=[('active', COLORS['highlight']), ('pressed', COLORS['secondary'])])

        # Frame styles
        style.configure('Card.TFrame', background=COLORS['card'], relief='flat', borderwidth=0)

        # Label styles
        style.configure('Title.TLabel',
                        font=('Helvetica', 16, 'bold'),
                        foreground=COLORS['highlight'],
                        background=COLORS['background'])
        style.configure('Subtitle.TLabel',
                        font=('Helvetica', 12),
                        foreground=COLORS['text'],
                        background=COLORS['background'])
        style.configure('Result.TLabel',
                        font=('Helvetica', 14, 'bold'),
                        background=COLORS['card'])

    def create_widgets(self):
        # Header frame
        header_frame = ttk.Frame(self.root, style='Card.TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=15)

        ttk.Label(header_frame,
                  text="CardioScan AI",
                  style='Title.TLabel').pack(side=tk.LEFT, padx=10)

        ttk.Label(header_frame,
                  text="Heart Disease Detection from MRI Scans",
                  style='Subtitle.TLabel').pack(side=tk.LEFT, padx=10)

        # Control frame
        control_frame = ttk.Frame(self.root, style='Card.TFrame')
        control_frame.pack(fill=tk.X, padx=20, pady=10)

        self.browse_btn = ModernButton(
            control_frame,
            text="📁 Browse MRI Scans",
            command=self.browse_files
        )
        self.browse_btn.pack(side=tk.LEFT, padx=10, pady=5)

        self.status_label = ttk.Label(
            control_frame,
            text="Ready to analyze MRI scans",
            style='Subtitle.TLabel'
        )
        self.status_label.pack(side=tk.LEFT, padx=20)

        # Main content frame
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Image display frame
        self.image_frame = ttk.Frame(content_frame, style='Card.TFrame')
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.image_label = ttk.Label(
            self.image_frame,
            text="MRI Scan Will Appear Here",
            style='Subtitle.TLabel'
        )
        self.image_label.pack(pady=50)

        # Results frame
        result_frame = ttk.Frame(content_frame, style='Card.TFrame')
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5, ipadx=10, ipady=10)

        ttk.Label(
            result_frame,
            text="Analysis Results",
            style='Title.TLabel'
        ).pack(pady=10)

        # Prediction card
        pred_card = ttk.Frame(result_frame, style='Card.TFrame')
        pred_card.pack(fill=tk.X, pady=10, padx=10, ipady=5)

        ttk.Label(
            pred_card,
            text="Diagnosis:",
            style='Subtitle.TLabel'
        ).pack(anchor=tk.W)

        self.result_label = ttk.Label(
            pred_card,
            text="Not analyzed",
            style='Result.TLabel'
        )
        self.result_label.pack(fill=tk.X, pady=5)

        # Confidence card
        conf_card = ttk.Frame(result_frame, style='Card.TFrame')
        conf_card.pack(fill=tk.X, pady=10, padx=10, ipady=5)

        ttk.Label(
            conf_card,
            text="Confidence Level:",
            style='Subtitle.TLabel'
        ).pack(anchor=tk.W)

        self.confidence_label = ttk.Label(
            conf_card,
            text="0%",
            style='Result.TLabel'
        )
        self.confidence_label.pack(fill=tk.X, pady=5)

        # Precautions card
        prec_card = ttk.Frame(result_frame, style='Card.TFrame')
        prec_card.pack(fill=tk.BOTH, expand=True, pady=10, padx=10, ipady=5)

        ttk.Label(
            prec_card,
            text="Recommended Actions:",
            style='Subtitle.TLabel'
        ).pack(anchor=tk.W)

        self.precautions_label = ttk.Label(
            prec_card,
            text="No analysis performed yet",
            style='Subtitle.TLabel',
            wraplength=300,
            justify=tk.LEFT
        )
        self.precautions_label.pack(fill=tk.BOTH, expand=True, pady=5)

        # Navigation frame
        nav_frame = ttk.Frame(self.root, style='Card.TFrame')
        nav_frame.pack(fill=tk.X, padx=20, pady=10)

        self.prev_btn = ModernButton(
            nav_frame,
            text="◄ Previous",
            command=self.show_previous,
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=20)

        self.next_btn = ModernButton(
            nav_frame,
            text="Next ►",
            command=self.show_next,
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.RIGHT, padx=20)

        # Counter label
        self.counter_label = ttk.Label(
            nav_frame,
            text="0/0",
            style='Subtitle.TLabel'
        )
        self.counter_label.pack(side=tk.LEFT, expand=True)

    def browse_files(self):
        """Open file dialog to select multiple images"""
        filetypes = (
            ('Image files', '*.jpg *.jpeg *.png'),
            ('All files', '*.*')
        )

        paths = filedialog.askopenfilenames(
            title='Select MRI Scans',
            initialdir='/',
            filetypes=filetypes
        )

        if paths:
            self.image_paths = list(paths)
            self.current_index = 0
            self.predictions = []

            # Update status
            self.status_label.config(text=f"Processing {len(self.image_paths)} images...")
            self.root.update()

            # Process images with progress
            for i, path in enumerate(self.image_paths):
                try:
                    result = self.predictor.predict(path)
                    self.predictions.append(result)
                except Exception as e:
                    self.predictions.append({
                        'error': str(e),
                        'image_path': path
                    })

                # Update progress
                self.status_label.config(text=f"Processing {i + 1}/{len(self.image_paths)} images")
                self.root.update()

            # Update UI
            self.status_label.config(text=f"Analysis complete - {len(self.predictions)} results")
            self.update_navigation_buttons()
            self.show_current_image()

    def show_current_image(self):
        """Display current image and prediction"""
        if not self.predictions or self.current_index >= len(self.predictions):
            return

        prediction = self.predictions[self.current_index]

        # Display image
        img = Image.open(prediction['image_path'])
        img.thumbnail((600, 600))  # Larger display size

        # Clear previous image if exists
        if hasattr(self, 'img_display') and self.img_display:
            self.img_display.destroy()

        # Convert to PhotoImage
        self.current_img = ImageTk.PhotoImage(img)

        # Create new image label
        self.img_display = ttk.Label(self.image_frame, image=self.current_img)
        self.img_display.pack(pady=10)

        # Hide placeholder text
        self.image_label.pack_forget()

        # Show prediction results
        if 'error' in prediction:
            self.result_label.config(
                text=f"Error: {prediction['error']}",
                foreground=COLORS['danger']
            )
            self.confidence_label.config(text="")
            self.precautions_label.config(
                text="Unable to provide recommendations due to error",
                foreground=COLORS['text']
            )
        else:
            color = COLORS['danger'] if prediction['class'] == 'sick' else COLORS['success']
            self.result_label.config(
                text=f"{prediction['class'].upper()}",
                foreground=color
            )
            self.confidence_label.config(
                text=f"{prediction['confidence']:.1f}% confidence",
                foreground=color
            )

            precautions = "\n".join(self.predictor.get_precautions(prediction['class']))
            self.precautions_label.config(
                text=precautions,
                foreground=color
            )

        # Update counter
        self.counter_label.config(
            text=f"{self.current_index + 1}/{len(self.predictions)}"
        )

    def show_next(self):
        """Show next image in the list"""
        if self.current_index < len(self.predictions) - 1:
            self.current_index += 1
            self.show_current_image()
            self.update_navigation_buttons()

    def show_previous(self):
        """Show previous image in the list"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()
            self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Update button states based on current position"""
        # Enable/disable previous button
        self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)

        # Enable/disable next button
        self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.predictions) - 1 else tk.DISABLED)


if __name__ == '__main__':
    root = tk.Tk()

    # Set window icon
    try:
        root.iconbitmap('assets/icon.ico')  # Add a heart icon if available
    except:
        pass

    app = MRIApp(root)
    root.mainloop()