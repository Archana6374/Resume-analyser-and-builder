#!/usr/bin/env python
"""
Script to download NLTK data required for text processing
"""

import nltk
import sys

def download_nltk_data():
    """Download required NLTK data"""
    try:
        print("Downloading NLTK punkt tokenizer...")
        nltk.download('punkt', quiet=True)

        print("Downloading NLTK stopwords...")
        nltk.download('stopwords', quiet=True)

        print("Downloading NLTK wordnet...")
        nltk.download('wordnet', quiet=True)

        print("✅ All NLTK data downloaded successfully!")
        return True

    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        return False

if __name__ == "__main__":
    success = download_nltk_data()
    sys.exit(0 if success else 1)