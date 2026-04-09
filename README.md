# Resume Builder and Analyzer - Backend

A comprehensive Django-based resume processing and analysis system with advanced text processing capabilities.

## Features

### Resume Upload & Processing
- **Multi-format Support**: PDF and DOCX file uploads
- **Advanced Text Extraction**: Robust parsing with error handling
- **File Validation**: Type and size validation
- **Secure Storage**: Django's FileSystemStorage with organized file management

### Text Preprocessing Module
- **Text Cleaning**: Remove extra whitespace, special characters, normalization
- **Tokenization**: Word and sentence level processing
- **Stop Word Removal**: NLTK-based filtering
- **Lemmatization**: Word form normalization
- **Case Normalization**: Consistent lowercase processing

### Resume Analysis Module
- **Section Detection**: Automatic identification of resume sections (Contact, Summary, Experience, Education, Skills)
- **Contact Information Extraction**: Email, phone, LinkedIn parsing
- **Skills Analysis**: Technical and soft skills identification
- **Keyword Extraction**: TF-IDF based important term identification
- **Readability Metrics**: Flesch score and grade level calculation
- **ATS Compatibility Analysis**: Formatting and keyword optimization checks

### Scoring System
- **Comprehensive Scoring**: Multi-factor resume quality assessment
- **Content Completeness**: Section presence evaluation
- **Skills Quality**: Technical and soft skills assessment
- **Readability Analysis**: Language complexity evaluation
- **ATS Compatibility**: Applicant tracking system optimization
- **Length Optimization**: Word count appropriateness

### Job Matching
- **Resume-Job Comparison**: Side-by-side analysis
- **Skills Matching**: Technical and soft skills alignment
- **Keyword Matching**: Job description keyword overlap
- **Match Scoring**: Overall compatibility percentage
- **Improvement Recommendations**: Specific suggestions for better matching

## API Endpoints

### POST /analyzer/api/analyze/
Analyze resume text and return comprehensive insights.

**Request Body:**
```json
{
  "text": "Full resume text content..."
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "sections": {...},
    "contact_info": {...},
    "skills": {...},
    "readability": {...},
    "keywords": [...],
    "ats_analysis": {...}
  }
}
```

### POST /analyzer/api/match/
Match resume against job description.

**Request Body:**
```json
{
  "resume_text": "Resume content...",
  "job_text": "Job description..."
}
```

**Response:**
```json
{
  "success": true,
  "match_score": 75.5,
  "keyword_score": 80.0,
  "tech_score": 70.0,
  "matched_keywords": [...],
  "missing_keywords": [...]
}
```

## Database Models

### Resume
- File metadata and storage
- Extracted and processed text
- Basic statistics (word count, scores)

### ResumeAnalysis
- Detailed analysis results
- Skills and keyword data
- Readability metrics
- ATS compatibility scores

### JobDescription
- Job posting storage
- Extracted requirements and skills

### ResumeJobMatch
- Matching results between resumes and jobs
- Detailed comparison data

## Text Processing Features

### Advanced Text Extraction
- PDF text extraction with page handling
- DOCX document parsing with formatting preservation
- Error handling for corrupted files
- Multi-language support preparation

### Preprocessing Pipeline
1. **Cleaning**: Whitespace normalization, special character removal
2. **Tokenization**: Word and sentence boundary detection
3. **Normalization**: Case conversion, encoding standardization
4. **Filtering**: Stop word removal, punctuation elimination
5. **Lemmatization**: Base word form reduction

### Skills Recognition
- **Technical Skills**: Programming languages, frameworks, tools, databases, cloud platforms
- **Soft Skills**: Communication, leadership, problem-solving, etc.
- **Custom Dictionaries**: Extensible skill categorization
- **Context Awareness**: Position and industry-specific skill detection

### ATS Optimization
- **Formatting Analysis**: Table, column, and complex formatting detection
- **Keyword Optimization**: Job-specific terminology matching
- **Structure Validation**: Standard section header verification
- **Quantification Checks**: Measurable achievement detection

## Installation & Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### MySQL Setup

If you want to run the project on MySQL instead of SQLite:

1. Create a `.env` file in the project root based on `.env.example`.
2. Set these values:
   ```bash
   DB_ENGINE=django.db.backends.mysql
   MYSQL_DATABASE=resume_db
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   ```
3. Create the database in MySQL:
   ```sql
   CREATE DATABASE resume_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```

If `DB_ENGINE` is not set to MySQL, the project continues using `db.sqlite3`.

3. **Download NLTK Data:**
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   nltk.download('wordnet')
   ```

4. **Start Server:**
   ```bash
   python manage.py runserver
   ```

## Quick Deploy on Render

1. Push this project to GitHub.
2. Sign in to Render and create a new `Web Service`.
3. Connect your GitHub repository.
4. Use the repo root `resume builder and analyser/resume builder and analyser` as the service root if Render asks for it.
5. Render can use:
   ```bash
   Build Command: ./build.sh
   Start Command: gunicorn resume_builder.wsgi:application
   ```
6. Set these environment variables in Render:
   ```bash
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=<your-render-domain>
   DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-render-domain>
   DJANGO_SECRET_KEY=<generate-a-secret>
   ```
7. After deploy, your public website link will look like:
   ```text
   https://your-service-name.onrender.com
   ```

You can use that public Render URL in Razorpay when it asks for your website link.

## Usage Examples

### Basic Resume Upload
```python
from analyzer.text_processor import analyze_resume_text

# Analyze resume text
result = analyze_resume_text(resume_content)
print(f"Skills found: {result['skills']}")
print(f"Readability score: {result['readability']['flesch_score']}")
```

### Job Matching
```python
from analyzer.views import api_match_job
import json

# Match resume to job
match_data = {
    'resume_text': resume_content,
    'job_text': job_description
}
# Process through API endpoint
```

## Future Enhancements

- **Machine Learning Integration**: ML-based skill extraction and job matching
- **Multi-language Support**: International resume processing
- **Advanced NLP**: Named entity recognition, sentiment analysis
- **Integration APIs**: LinkedIn, Indeed, Glassdoor job data
- **Real-time Analysis**: Live editing feedback
- **Collaborative Features**: Team resume review workflows

## Dependencies

- **Django**: Web framework
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX file processing
- **NLTK**: Natural language processing
- **scikit-learn**: Machine learning utilities
- **spaCy**: Advanced NLP (future use)
- **pandas**: Data manipulation
- **numpy**: Numerical computing
