import warnings
from flask_frozen import MimetypeMismatchWarning
from app import app, freezer  # Import your Flask app and Freezer instance

# Suppress MimetypeMismatchWarning warnings
warnings.filterwarnings("ignore", category=MimetypeMismatchWarning)

if __name__ == '__main__':
    freezer.freeze()
