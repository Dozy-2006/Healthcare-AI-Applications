import streamlit as st
from utils.model_utils import MRIPredictor
import os

# App config
st.set_page_config(
    page_title="Heart Disease MRI Classifier",
    page_icon="❤️",
    layout="wide"
)

USER_CREDENTIALS = {"username": "user", "password": "password123"}


@st.cache_resource
def load_predictor():
    try:
        return MRIPredictor('models/best_model.pth')
    except Exception as e:
        st.error(f"Failed to load model: {str(e)}")
        st.stop()


def authenticate_user():
    """Authenticate user using username and password."""
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USER_CREDENTIALS["username"] and password == USER_CREDENTIALS["password"]:
            st.session_state.authenticated = True
            st.success("Login successful! Redirecting to the main page...")
            st.session_state.page = "main"
        else:
            st.error("Invalid username or password. Please try again.")


def entry_page():
    """Display the start page."""
    st.title("Welcome to the Heart Disease MRI Classifier! ❤️")
    st.markdown("""
    This application allows you to upload MRI scans to detect heart disease. 
    The AI model will analyze the images and provide predictions along with recommendations.
    """)

    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        authenticate_user()  # Show login page if not authenticated

    elif st.button("Start Detection"):
        st.session_state.page = "main"


def main_page():
    """Main page where users can upload MRI images for prediction."""
    st.title("❤️ Heart Disease MRI Classifier")
    st.markdown("Upload MRI scans to detect heart disease")

    # Load model (cached)
    predictor = load_predictor()

    # File upload
    uploaded_files = st.file_uploader(
        "Choose MRI images (JPG/PNG)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_files:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):
            try:
                # Save temp file
                with open("temp_img", "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Update UI
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Processing {i + 1}/{len(uploaded_files)}: {uploaded_file.name}")

                # Predict
                prediction, confidence = predictor.predict("temp_img")
                results.append({
                    "name": uploaded_file.name,
                    "prediction": prediction,
                    "confidence": confidence,
                    "precautions": predictor.get_precautions(prediction)
                })

                # Clean up
                os.remove("temp_img")

            except Exception as e:
                results.append({
                    "name": uploaded_file.name,
                    "error": str(e)
                })

        # Display results
        st.success("Analysis complete!")
        progress_bar.empty()
        status_text.empty()

        for result in results:
            with st.expander(f"Result: {result['name']}", expanded=True):
                if 'error' in result:
                    st.error(f"Error: {result['error']}")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(uploaded_file, use_column_width=True)
                    with col2:
                        if result['prediction'] == 'sick':
                            st.error(f"🚨 Result: {result['prediction']} ({result['confidence']:.1f}% confidence)")
                            st.warning("**Precautions:**")
                            for precaution in result['precautions']:
                                st.write(f"- {precaution}")
                        else:
                            st.success(f"✅ Result: {result['prediction']} ({result['confidence']:.1f}% confidence)")
                            st.info(result['precautions'][0])


def main():
    """Check for which page to display."""
    if "page" not in st.session_state:
        st.session_state.page = "entry"

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False  # Default is not authenticated

    if st.session_state.page == "entry":
        entry_page()
    elif st.session_state.page == "main" and st.session_state.authenticated:
        main_page()
    else:
        st.error("You are not authenticated. Please log in.")


if __name__ == '__main__':
    main()
