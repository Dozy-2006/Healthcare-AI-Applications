import os
import sys
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QVBoxLayout, QWidget, QFileDialog, QListWidget,
                             QMessageBox, QHBoxLayout, QProgressDialog)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from utils.model_utils import MRIPredictor


class HeartDiseaseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heart Disease MRI Classifier")
        self.setWindowIcon(QIcon("assets/icon.png"))  # Add a heart icon if available

        try:
            # Initialize model
            self.predictor = MRIPredictor('models/best_model.pth')
            self.init_ui()
            self.statusBar().showMessage("Ready")
        except Exception as e:
            self.show_error("Initialization Error",
                            f"Failed to load model:\n{str(e)}\n\n{traceback.format_exc()}")
            sys.exit(1)

    def init_ui(self):
        """Initialize the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()

        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setStyleSheet("""
            border: 2px dashed #aaa;
            background: #f9f9f9;
            qproperty-alignment: AlignCenter;
        """)
        layout.addWidget(self.image_label)

        # Results list
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                font: 12px;
                min-height: 100px;
            }
            QListWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(self.results_list)

        # Button layout
        button_layout = QHBoxLayout()

        # Load button
        self.load_button = QPushButton("Load MRI Scans")
        self.load_button.setIcon(QIcon("assets/folder.png"))
        self.load_button.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font: bold 12px;
            }
        """)
        self.load_button.clicked.connect(self.load_images)
        button_layout.addWidget(self.load_button)

        # Predict button
        self.predict_button = QPushButton("Analyze")
        self.predict_button.setIcon(QIcon("assets/analyze.png"))
        self.predict_button.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font: bold 12px;
                background: #4CAF50;
                color: white;
            }
            QPushButton:disabled {
                background: #cccccc;
            }
        """)
        self.predict_button.clicked.connect(self.predict_images)
        self.predict_button.setEnabled(False)
        button_layout.addWidget(self.predict_button)

        layout.addLayout(button_layout)
        central_widget.setLayout(layout)

        # Store loaded images
        self.image_paths = []

        # Set minimum window size
        self.setMinimumSize(600, 700)

    def load_images(self):
        """Load MRI scan images"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select MRI Scans",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp);;All Files (*)"
        )

        if files:
            self.image_paths = files
            self.predict_button.setEnabled(True)
            self.results_list.clear()
            self.results_list.addItems([f"✔ {os.path.basename(f)}" for f in files])

            # Display first image
            self.display_image(files[0])
            self.statusBar().showMessage(f"Loaded {len(files)} images")

    def display_image(self, path):
        """Display selected image"""
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                self.image_label.width() - 20,
                self.image_label.height() - 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)

    def predict_images(self):
        """Analyze all loaded images"""
        if not self.image_paths:
            return

        # Create progress dialog
        progress = QProgressDialog("Analyzing images...", "Cancel", 0, len(self.image_paths), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setWindowTitle("Processing")
        progress.setAutoClose(True)

        self.results_list.clear()
        precautions_shown = False

        for i, img_path in enumerate(self.image_paths):
            progress.setValue(i)
            QApplication.processEvents()  # Keep UI responsive

            if progress.wasCanceled():
                break

            try:
                # Make prediction
                prediction, confidence = self.predictor.predict(img_path)
                result_text = f"{os.path.basename(img_path)}: {prediction} ({confidence:.1f}% confidence)"

                # Add to results list
                item = QListWidgetItem(result_text)
                if prediction == "sick":
                    item.setForeground(Qt.red)
                    if not precautions_shown:
                        self.show_precautions()
                        precautions_shown = True
                else:
                    item.setForeground(Qt.darkGreen)
                self.results_list.addItem(item)

                # Display current image
                self.display_image(img_path)

            except Exception as e:
                self.results_list.addItem(f"❌ Error analyzing {os.path.basename(img_path)}")
                print(f"Error processing {img_path}: {traceback.format_exc()}")

        progress.setValue(len(self.image_paths))
        self.statusBar().showMessage("Analysis complete")

    def show_precautions(self):
        """Show heart disease precautions"""
        precautions = self.predictor.get_precautions("sick")
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Important Precautions")
        msg.setText("<b>Heart Disease Detected - Please Note:</b>")
        msg.setInformativeText("\n".join(precautions))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_error(self, title, message):
        """Show error message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


if __name__ == '__main__':
    # Set working directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look

    # Create and show main window
    try:
        window = HeartDiseaseApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Fatal error: {traceback.format_exc()}")
        sys.exit(1)