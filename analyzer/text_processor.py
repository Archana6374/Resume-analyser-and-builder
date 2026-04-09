"""
Resume Text Processing Utilities
Advanced text extraction, preprocessing, and analysis functions
"""

import re
import string
from collections import Counter
from typing import List, Dict, Tuple, Optional
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from PyPDF2 import PdfReader
from docx import Document

def _has_nltk_resource(path: str) -> bool:
    try:
        nltk.data.find(path)
        return True
    except LookupError:
        return False


def _safe_word_tokenize(text: str) -> List[str]:
    try:
        return word_tokenize(text)
    except LookupError:
        return re.findall(r"\b[\w+#.-]+\b", text)


def _safe_sent_tokenize(text: str) -> List[str]:
    try:
        return sent_tokenize(text)
    except LookupError:
        return [part.strip() for part in re.split(r'[.!?\n]+', text) if part.strip()]

class ResumeTextProcessor:
    """Advanced text processing for resumes"""

    def __init__(self):
        self.stop_words = set(stopwords.words('english')) if _has_nltk_resource('corpora/stopwords') else set()
        self.lemmatizer = WordNetLemmatizer() if _has_nltk_resource('corpora/wordnet') else None

        # Common resume sections
        self.section_patterns = {
            'contact': r'(?i)(contact|phone|email|address|linkedin|github)',
            'summary': r'(?i)(summary|objective|profile|about)',
            'experience': r'(?i)(experience|work|employment|professional)',
            'education': r'(?i)(education|degree|university|college|school)',
            'skills': r'(?i)(skills|technologies|competencies|expertise)',
            'projects': r'(?i)(projects|portfolio|achievements)',
            'certifications': r'(?i)(certifications|licenses|awards)',
        }

        # Technical skills keywords - expanded for better ATS matching
        self.technical_skills = {
            'programming': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'golang', 'rust', 'swift', 'kotlin',
                'scala', 'perl', 'bash', 'shell scripting', 'powershell', 'r', 'matlab', 'sas', 'stata', 'julia'
            ],
            'web': [
                'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'react', 'react.js', 'angular', 'angularjs', 'vue', 'vue.js',
                'node.js', 'nodejs', 'express', 'express.js', 'django', 'flask', 'fastapi', 'spring', 'spring boot', 'asp.net',
                'laravel', 'symfony', 'ruby on rails', 'rails', 'jquery', 'bootstrap', 'tailwind', 'material ui', 'webpack',
                'babel', 'gulp', 'grunt', 'next.js', 'nuxt.js', 'svelte', 'ember.js', 'backbone.js'
            ],
            'database': [
                'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'mongo', 'redis', 'oracle', 'sqlite', 'cassandra',
                'couchdb', 'dynamodb', 'firebase', 'elasticsearch', 'solr', 'neo4j', 'graph database', 'data warehouse',
                'etl', 'data modeling', 'database design', 'query optimization', 'stored procedures', 'triggers'
            ],
            'cloud': [
                'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud platform', 'heroku', 'digitalocean',
                'linode', 'docker', 'kubernetes', 'k8s', 'containerization', 'microservices', 'serverless', 'lambda',
                'terraform', 'ansible', 'puppet', 'chef', 'jenkins', 'ci/cd', 'continuous integration', 'continuous deployment',
                'devops', 'infrastructure as code', 'cloudformation', 'arm templates'
            ],
            'tools': [
                'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial', 'jenkins', 'travis ci', 'circleci', 'github actions',
                'jira', 'confluence', 'trello', 'asana', 'slack', 'postman', 'insomnia', 'swagger', 'vscode', 'visual studio',
                'intellij', 'eclipse', 'pycharm', 'sublime text', 'vim', 'emacs', 'atom'
            ],
            'data': [
                'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'scikit-learn', 'sklearn', 'tensorflow', 'keras',
                'pytorch', 'torch', 'opencv', 'computer vision', 'nlp', 'natural language processing', 'nltk', 'spacy',
                'transformers', 'hugging face', 'tableau', 'power bi', 'powerbi', 'qlik', 'looker', 'apache spark', 'hadoop',
                'hive', 'pig', 'kafka', 'airflow', 'data pipeline', 'machine learning', 'deep learning', 'ai', 'artificial intelligence',
                'data science', 'data analysis', 'data visualization', 'statistics', 'probability', 'a/b testing', 'hypothesis testing'
            ],
            'mobile': [
                'android', 'ios', 'swift', 'kotlin', 'react native', 'flutter', 'dart', 'xamarin', 'ionic', 'cordova',
                'phonegap', 'mobile development', 'app development'
            ],
            'testing': [
                'unit testing', 'integration testing', 'selenium', 'cypress', 'jest', 'mocha', 'chai', 'pytest', 'junit',
                'testng', 'cucumber', 'bdd', 'tdd', 'test automation', 'qa', 'quality assurance', 'manual testing'
            ],
            'security': [
                'cybersecurity', 'information security', 'penetration testing', 'ethical hacking', 'owasp', 'ssl', 'tls',
                'encryption', 'authentication', 'authorization', 'oauth', 'jwt', 'firewall', 'intrusion detection'
            ],
            'other': [
                'agile', 'scrum', 'kanban', 'waterfall', 'lean', 'six sigma', 'itil', 'project management', 'product management',
                'business analysis', 'requirements gathering', 'stakeholder management', 'risk management', 'change management'
            ]
        }

        # Soft skills - expanded list
        self.soft_skills = [
            'communication', 'verbal communication', 'written communication', 'presentation skills', 'public speaking',
            'leadership', 'team leadership', 'management', 'teamwork', 'collaboration', 'problem solving', 'critical thinking',
            'analytical thinking', 'analytical skills', 'decision making', 'time management', 'organization', 'prioritization',
            'adaptability', 'flexibility', 'creativity', 'innovation', 'attention to detail', 'accuracy', 'quality focus',
            'project management', 'customer service', 'client relations', 'relationship building', 'negotiation',
            'conflict resolution', 'emotional intelligence', 'empathy', 'cultural awareness', 'diversity', 'inclusion',
            'mentoring', 'coaching', 'training', 'teaching', 'learning agility', 'continuous learning', 'self-motivation',
            'initiative', 'proactivity', 'accountability', 'responsibility', 'reliability', 'work ethic', 'professionalism',
            'interpersonal skills', 'networking', 'stakeholder management', 'change management', 'crisis management'
        ]

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)\@]', '', text)

        return text

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract different sections from resume text"""
        sections = {}
        lines = text.split('\n')

        current_section = 'general'
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line matches any section pattern
            section_found = False
            for section_name, pattern in self.section_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                        current_content = []

                    current_section = section_name
                    section_found = True
                    break

            if not section_found:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from text"""
        contact_info = {}

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]

        # Phone pattern (various formats)
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = '-'.join(phones[0][1:])  # Format as XXX-XXX-XXXX

        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()

        return contact_info

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills"""
        text_lower = text.lower()
        found_technical = []
        found_soft = []

        # Check technical skills
        for category, skills in self.technical_skills.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_technical.append(skill)

        # Check soft skills
        for skill in self.soft_skills:
            if skill.lower() in text_lower:
                found_soft.append(skill)

        return {
            'technical': list(set(found_technical)),
            'soft': list(set(found_soft))
        }

    def calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics"""
        sentences = _safe_sent_tokenize(text)
        words = _safe_word_tokenize(text)

        if not sentences or not words:
            return {'flesch_score': 0, 'grade_level': 0}

        # Average sentence length
        avg_sentence_length = len(words) / len(sentences)

        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Flesch Reading Ease Score
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)

        # Grade level (approximation)
        grade_level = 0.39 * avg_sentence_length + 11.8 * avg_word_length - 15.59

        return {
            'flesch_score': max(0, min(100, flesch_score)),
            'grade_level': max(0, grade_level)
        }

    def extract_keywords(self, text: str, top_n: int = 100) -> List[Tuple[str, float]]:
        """
        Extract comprehensive keywords using advanced techniques for better ATS matching
        Returns keywords with relevance scores
        """
        if not text:
            return []

        # Clean and tokenize text
        text = text.lower()
        words = _safe_word_tokenize(text)

        # Remove punctuation and filter
        words = [word for word in words if word.isalpha() and len(word) > 2]

        # Create n-grams (1-3 words)
        unigrams = words
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]

        all_phrases = unigrams + bigrams + trigrams

        # Count frequencies
        phrase_freq = Counter(all_phrases)

        # Calculate relevance scores
        keyword_scores = {}

        for phrase, freq in phrase_freq.items():
            score = freq

            # Boost score for technical skills
            for category, skills in self.technical_skills.items():
                for skill in skills:
                    if skill.lower() in phrase:
                        score *= 2.0  # Double weight for technical skills
                        break

            # Boost score for soft skills
            for skill in self.soft_skills:
                if skill.lower() in phrase:
                    score *= 1.5  # 50% boost for soft skills
                    break

            # Boost score for industry terms and certifications
            industry_terms = [
                'certified', 'certification', 'license', 'licensed', 'phd', 'masters', 'bachelors',
                'degree', 'diploma', 'experience', 'years', 'senior', 'junior', 'lead', 'principal',
                'architect', 'engineer', 'developer', 'analyst', 'manager', 'director', 'vp', 'cfo',
                'cto', 'ceo', 'scrum master', 'product owner', 'agile', 'scrum', 'kanban'
            ]
            for term in industry_terms:
                if term in phrase:
                    score *= 1.3  # 30% boost for industry terms
                    break

            # Penalize common stop words and short phrases
            if len(phrase.split()) == 1 and len(phrase) < 4:
                score *= 0.5

            keyword_scores[phrase] = score

        # Sort by score and return top keywords
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)

        # Filter out phrases that are too long or contain only stop words
        filtered_keywords = []
        for phrase, score in sorted_keywords:
            words_in_phrase = phrase.split()
            if len(words_in_phrase) <= 3:  # Max 3 words
                # Check if phrase contains meaningful words
                meaningful_words = [w for w in words_in_phrase if w not in self.stop_words and len(w) > 2]
                if meaningful_words:
                    filtered_keywords.append((phrase, score))

        return filtered_keywords[:top_n]

    def expand_keywords_with_synonyms(self, keywords: List[str]) -> List[str]:
        """
        Expand keyword list with synonyms and related terms for better ATS matching
        """
        expanded = set(keywords)

        # Synonym mappings for common tech terms
        synonyms = {
            'python': ['python programming', 'python development'],
            'java': ['java programming', 'java development', 'jvm'],
            'javascript': ['js', 'ecmascript', 'node', 'nodejs'],
            'react': ['react.js', 'reactjs'],
            'angular': ['angularjs', 'angular.js'],
            'node.js': ['nodejs', 'node'],
            'django': ['django framework'],
            'flask': ['flask framework'],
            'sql': ['structured query language', 'database queries'],
            'mysql': ['my sql'],
            'postgresql': ['postgres'],
            'mongodb': ['mongo', 'nosql'],
            'aws': ['amazon web services'],
            'azure': ['microsoft azure'],
            'gcp': ['google cloud', 'google cloud platform'],
            'docker': ['containerization', 'containers'],
            'kubernetes': ['k8s', 'container orchestration'],
            'git': ['version control', 'source control'],
            'ci/cd': ['continuous integration', 'continuous deployment'],
            'machine learning': ['ml', 'artificial intelligence', 'ai'],
            'data science': ['data analysis', 'analytics'],
            'agile': ['scrum', 'kanban', 'iterative development'],
            'devops': ['site reliability', 'infrastructure automation'],
            'api': ['rest api', 'web services', 'microservices'],
            'testing': ['qa', 'quality assurance', 'test automation'],
            'leadership': ['management', 'team leadership'],
            'communication': ['presentation', 'public speaking'],
            'problem solving': ['critical thinking', 'analytical skills']
        }

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in synonyms:
                expanded.update(synonyms[keyword_lower])

        return list(expanded)

    def analyze_ats_compatibility(self, text: str) -> Dict[str, any]:
        """Analyze ATS compatibility with AI-like weighted prediction"""
        issues = []
        score = 20

        cleaned_text = self.clean_text(text).lower()
        keywords = ['experience', 'skills', 'education', 'projects', 'certifications', 'leadership', 'management', 'communications', 'teamwork']

        # Section and header coverage
        headers = ['experience', 'skills', 'education', 'summary', 'certifications']
        header_matches = sum(1 for header in headers if header in cleaned_text)
        score += (header_matches / len(headers)) * 20
        if header_matches < 3:
            issues.append('Missing standard ATS-friendly section headers')

        # Contact information and structure
        if re.search(r'[\w\.-]+@[\w\.-]+\.[a-z]{2,}', cleaned_text):
            score += 8
        else:
            issues.append('Missing email address')

        if re.search(r'\b\d{3}[\s\-.]?\d{3}[\s\-.]?\d{4}\b', cleaned_text):
            score += 8
        else:
            issues.append('Missing phone number')

        # Quantifiable content
        if re.search(r'\b\d+%|\b\d+\s+(years?|months?)\b|\b\d+\s+(clients|users|projects|customers)\b', cleaned_text):
            score += 10
        else:
            issues.append('Missing measurable achievements or numeric results')

        # Keyword coverage
        keyword_hits = sum(1 for keyword in keywords if keyword in cleaned_text)
        score += (keyword_hits / len(keywords)) * 20
        if keyword_hits < 4:
            issues.append('Resume does not include enough common ATS keywords')

        # Readability adjustment
        readability = self.calculate_readability(text)['flesch_score']
        if readability >= 40 and readability <= 70:
            score += 10
        elif readability > 70:
            score += 5
        else:
            issues.append('Resume language may be too dense for standard ATS parsing')

        # Formatting penalties
        if re.search(r'<table|<td|<tr|\t', text, re.IGNORECASE):
            issues.append('Contains complex formatting or table-like structures')
            score -= 15

        if re.search(r'®|©|™|•|●|►', text):
            score -= 10
            issues.append('Contains symbols that can confuse ATS parsing')

        if len(text.split()) < 250:
            score -= 10
            issues.append('Resume is brief and may not contain enough ATS-friendly content')

        # Ensure more varied output with moderate normalization
        score = max(0, min(100, round(score)))

        # AI-powered prediction wording
        if score >= 90:
            prediction = 'AI-powered ATS prediction: Your resume is exceptionally optimized and should perform extremely well in automated screening.'
        elif score >= 80:
            prediction = 'AI-powered ATS prediction: Your resume is strong and likely to pass most ATS filters with only minor improvements needed.'
        elif score >= 70:
            prediction = 'AI-powered ATS prediction: Your resume is reasonably ATS-friendly but could benefit from targeted keyword and formatting updates.'
        elif score >= 60:
            prediction = 'AI-powered ATS prediction: Your resume is somewhat ATS-friendly but may struggle with stricter automated screening systems.'
        else:
            prediction = 'AI-powered ATS prediction: Your resume likely needs focused optimization to be parsed successfully by modern ATS platforms.'

        return {
            'score': score,
            'issues': issues,
            'prediction': prediction,
            'recommendations': [
                'Use standard section headers (Experience, Skills, Education)',
                'Include measurable achievements and metrics',
                'Avoid complex formatting, tables, and unusual symbols',
                'Mirror job description keywords with natural phrasing'
            ]
        }

    def preprocess_for_analysis(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Clean text
        text = self.clean_text(text)

        # Convert to lowercase
        text = text.lower()

        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

# Global processor instance
processor = ResumeTextProcessor()

def extract_text_from_pdf(file_path: str) -> str:
    """Enhanced PDF text extraction"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return processor.clean_text(text)
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file_path: str) -> str:
    """Enhanced DOCX text extraction"""
    try:
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        return processor.clean_text(text)
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def analyze_resume_text(text: str) -> Dict[str, any]:
    """Complete resume analysis"""
    if not text or text.startswith("Error"):
        return {
            'error': 'Invalid or empty resume text',
            'sections': {},
            'contact_info': {},
            'skills': {'technical': [], 'soft': []},
            'readability': {'flesch_score': 0, 'grade_level': 0},
            'keywords': [],
            'total_words': 0,
            'unique_words': 0,
            'ats_analysis': {'score': 0, 'issues': ['Invalid resume'], 'recommendations': []}
        }

    # Initialize processor
    processor = ResumeTextProcessor()

    # Calculate basic metrics
    words = text.split()
    total_words = len(words)
    unique_words = len(set(word.lower() for word in words))

    analysis_result = {
        'sections': processor.extract_sections(text),
        'contact_info': processor.extract_contact_info(text),
        'skills': processor.extract_skills(text),
        'readability': processor.calculate_readability(text),
        'keywords': processor.extract_keywords(text),
        'ats_analysis': processor.analyze_ats_compatibility(text),
        'preprocessed_text': processor.preprocess_for_analysis(text),
        'total_words': total_words,
        'unique_words': unique_words
    }

    return analysis_result


def analyze_job_match(resume_text: str, job_description: str) -> Dict[str, any]:
    """
    Analyze how well a resume matches a job description using comprehensive keyword analysis
    Returns detailed matching information including scores and keyword analysis
    """
    processor = ResumeTextProcessor()

    try:
        # Extract keywords from both texts with higher coverage
        resume_keywords = processor.extract_keywords(resume_text, top_n=100)
        job_keywords = processor.extract_keywords(job_description, top_n=100)

        # Expand with synonyms for better matching
        resume_kw_expanded = processor.expand_keywords_with_synonyms([kw[0] for kw in resume_keywords])
        job_kw_expanded = processor.expand_keywords_with_synonyms([kw[0] for kw in job_keywords])

        # Extract skills
        resume_skills = processor.extract_skills(resume_text)
        job_skills = processor.extract_skills(job_description)

        # Create comprehensive keyword sets
        resume_kw_set = set([kw.lower() for kw in resume_kw_expanded])
        job_kw_set = set([kw.lower() for kw in job_kw_expanded])

        # Find matching and missing keywords
        matched_keywords = sorted(list(resume_kw_set & job_kw_set))
        missing_keywords = sorted(list(job_kw_set - resume_kw_set))

        # Calculate keyword match score with weighted scoring
        if job_kw_set:
            # Weight matches by their relevance scores
            total_job_weight = sum([kw[1] for kw in job_keywords if kw[0].lower() in job_kw_set])
            matched_weight = sum([kw[1] for kw in job_keywords if kw[0].lower() in matched_keywords])
            keyword_score = (matched_weight / total_job_weight) * 100 if total_job_weight > 0 else 0
        else:
            keyword_score = 0

        # Calculate skills match score
        resume_tech_skills = set(resume_skills['technical'])
        job_tech_skills = set(job_skills['technical'])
        resume_soft_skills = set(resume_skills['soft'])
        job_soft_skills = set(job_skills['soft'])

        tech_match = len(resume_tech_skills & job_tech_skills)
        soft_match = len(resume_soft_skills & job_soft_skills)

        tech_score = (tech_match / max(1, len(job_tech_skills))) * 100 if job_tech_skills else 100
        soft_score = (soft_match / max(1, len(job_soft_skills))) * 100 if job_soft_skills else 100

        # Overall match score with adjusted weights for better ATS relevance
        overall_score = (keyword_score * 0.5) + (tech_score * 0.35) + (soft_score * 0.15)

        # Return comprehensive results
        return {
            'overall_score': round(min(100, overall_score), 1),
            'keyword_score': round(min(100, keyword_score), 1),
            'technical_score': round(min(100, tech_score), 1),
            'soft_skills_score': round(min(100, soft_score), 1),
            'matched_keywords': matched_keywords[:20],  # Top 20 matches
            'missing_keywords': missing_keywords[:20],  # Top 20 missing
            'resume_keywords': [kw[0] for kw in resume_keywords[:25]],
            'job_keywords': [kw[0] for kw in job_keywords[:25]],
            'matched_tech_skills': list(resume_tech_skills & job_tech_skills),
            'missing_tech_skills': list(job_tech_skills - resume_tech_skills),
            'matched_soft_skills': list(resume_soft_skills & job_soft_skills),
            'missing_soft_skills': list(job_soft_skills - resume_soft_skills),
            'keyword_coverage': len(matched_keywords) / max(1, len(job_kw_set)) * 100,
            'total_resume_keywords': len(resume_kw_expanded),
            'total_job_keywords': len(job_kw_expanded)
        }

    except Exception as e:
        # Return basic analysis if processing fails
        return {
            'overall_score': 0,
            'keyword_score': 0,
            'technical_score': 0,
            'soft_skills_score': 0,
            'matched_keywords': [],
            'missing_keywords': [],
            'resume_keywords': [],
            'job_keywords': [],
            'matched_tech_skills': [],
            'missing_tech_skills': [],
            'matched_soft_skills': [],
            'missing_soft_skills': [],
            'keyword_coverage': 0,
            'total_resume_keywords': 0,
            'total_job_keywords': 0,
            'error': str(e)
        }


def analyze_job_title(job_title: str) -> Dict[str, any]:
    """
    Analyze a job title and generate relevant keywords, skills, and description
    """
    job_title_lower = job_title.lower().strip()

    # Job title mappings with keywords and skills
    job_mappings = {
        # Software Development
        'software engineer': {
            'keywords': ['software', 'development', 'programming', 'coding', 'engineering', 'computer science', 'algorithms', 'data structures', 'debugging', 'testing'],
            'technical_skills': ['python', 'java', 'javascript', 'c++', 'git', 'sql', 'api', 'rest', 'agile', 'scrum'],
            'soft_skills': ['problem solving', 'communication', 'teamwork', 'analytical thinking'],
            'description': 'Software Engineer role requiring programming skills, problem-solving abilities, and software development experience.'
        },
        'python developer': {
            'keywords': ['python', 'django', 'flask', 'programming', 'web development', 'backend', 'api', 'database'],
            'technical_skills': ['python', 'django', 'flask', 'postgresql', 'mysql', 'mongodb', 'rest api', 'git'],
            'soft_skills': ['problem solving', 'communication', 'teamwork'],
            'description': 'Python Developer position focusing on backend development, web applications, and API development using Python frameworks.'
        },
        'frontend developer': {
            'keywords': ['javascript', 'react', 'html', 'css', 'frontend', 'web development', 'ui', 'ux'],
            'technical_skills': ['javascript', 'react', 'vue', 'angular', 'html', 'css', 'sass', 'webpack'],
            'soft_skills': ['creativity', 'attention to detail', 'communication'],
            'description': 'Frontend Developer role creating user interfaces and web applications with modern JavaScript frameworks.'
        },
        'backend developer': {
            'keywords': ['backend', 'server', 'api', 'database', 'programming', 'architecture'],
            'technical_skills': ['python', 'java', 'node.js', 'sql', 'mongodb', 'redis', 'docker', 'kubernetes'],
            'soft_skills': ['problem solving', 'analytical thinking', 'communication'],
            'description': 'Backend Developer position building server-side applications, APIs, and database systems.'
        },
        'full stack developer': {
            'keywords': ['full stack', 'frontend', 'backend', 'web development', 'javascript', 'programming'],
            'technical_skills': ['javascript', 'react', 'node.js', 'python', 'sql', 'html', 'css', 'git'],
            'soft_skills': ['versatility', 'problem solving', 'communication', 'teamwork'],
            'description': 'Full Stack Developer role handling both frontend and backend development for complete web applications.'
        },

        # Data Science & Analytics
        'data scientist': {
            'keywords': ['data science', 'machine learning', 'statistics', 'python', 'analysis', 'modeling'],
            'technical_skills': ['python', 'r', 'sql', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'jupyter'],
            'soft_skills': ['analytical thinking', 'problem solving', 'communication', 'presentation'],
            'description': 'Data Scientist role analyzing data, building predictive models, and deriving insights from complex datasets.'
        },
        'data analyst': {
            'keywords': ['data analysis', 'sql', 'excel', 'reporting', 'visualization', 'business intelligence'],
            'technical_skills': ['sql', 'excel', 'tableau', 'power bi', 'python', 'r', 'statistics'],
            'soft_skills': ['analytical thinking', 'attention to detail', 'communication', 'problem solving'],
            'description': 'Data Analyst position creating reports, analyzing business data, and providing actionable insights.'
        },
        'machine learning engineer': {
            'keywords': ['machine learning', 'ai', 'deep learning', 'neural networks', 'algorithms', 'modeling'],
            'technical_skills': ['python', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'aws', 'docker'],
            'soft_skills': ['analytical thinking', 'problem solving', 'research', 'innovation'],
            'description': 'Machine Learning Engineer role developing and deploying ML models and AI systems.'
        },

        # Business & Management
        'project manager': {
            'keywords': ['project management', 'agile', 'scrum', 'planning', 'coordination', 'leadership'],
            'technical_skills': ['jira', 'trello', 'ms project', 'excel', 'powerpoint', 'agile', 'scrum'],
            'soft_skills': ['leadership', 'communication', 'organization', 'problem solving', 'teamwork'],
            'description': 'Project Manager role overseeing project execution, team coordination, and delivery management.'
        },
        'business analyst': {
            'keywords': ['business analysis', 'requirements', 'process improvement', 'stakeholder management'],
            'technical_skills': ['sql', 'excel', 'visio', 'jira', 'requirements gathering', 'uml'],
            'soft_skills': ['communication', 'analytical thinking', 'problem solving', 'stakeholder management'],
            'description': 'Business Analyst role gathering requirements and improving business processes.'
        },
        'product manager': {
            'keywords': ['product management', 'roadmap', 'strategy', 'user experience', 'market research'],
            'technical_skills': ['jira', 'figma', 'analytics', 'sql', 'agile', 'scrum'],
            'soft_skills': ['leadership', 'communication', 'strategic thinking', 'user focus'],
            'description': 'Product Manager role defining product strategy and managing product development lifecycle.'
        },

        # Marketing & Sales
        'marketing manager': {
            'keywords': ['marketing', 'campaign', 'brand', 'digital marketing', 'strategy', 'analytics'],
            'technical_skills': ['google analytics', 'seo', 'sem', 'social media', 'content marketing', 'crm'],
            'soft_skills': ['creativity', 'communication', 'strategic thinking', 'leadership'],
            'description': 'Marketing Manager role developing and executing marketing strategies and campaigns.'
        },
        'sales representative': {
            'keywords': ['sales', 'customer service', 'relationship building', 'negotiation', 'closing deals'],
            'technical_skills': ['crm', 'salesforce', 'excel', 'powerpoint', 'presentation tools'],
            'soft_skills': ['communication', 'persuasion', 'relationship building', 'resilience'],
            'description': 'Sales Representative role generating leads and closing sales with customers.'
        },
        'digital marketing specialist': {
            'keywords': ['digital marketing', 'social media', 'seo', 'content marketing', 'analytics'],
            'technical_skills': ['google ads', 'facebook ads', 'seo tools', 'analytics', 'content management'],
            'soft_skills': ['creativity', 'analytical thinking', 'communication', 'adaptability'],
            'description': 'Digital Marketing Specialist role managing online marketing campaigns and digital presence.'
        },

        # Design & Creative
        'ux designer': {
            'keywords': ['user experience', 'ux design', 'usability', 'wireframing', 'prototyping'],
            'technical_skills': ['figma', 'sketch', 'adobe xd', 'user research', 'usability testing'],
            'soft_skills': ['creativity', 'empathy', 'communication', 'problem solving'],
            'description': 'UX Designer role creating intuitive user experiences and conducting user research.'
        },
        'graphic designer': {
            'keywords': ['graphic design', 'visual design', 'branding', 'typography', 'layout'],
            'technical_skills': ['photoshop', 'illustrator', 'indesign', 'figma', 'after effects'],
            'soft_skills': ['creativity', 'attention to detail', 'communication', 'artistic vision'],
            'description': 'Graphic Designer role creating visual content and brand materials.'
        },

        # Default fallback
        'default': {
            'keywords': ['professional', 'experience', 'skills', 'communication', 'teamwork'],
            'technical_skills': ['microsoft office', 'communication tools', 'basic computer skills'],
            'soft_skills': ['communication', 'teamwork', 'problem solving', 'adaptability'],
            'description': f'Professional role as {job_title} requiring relevant experience and skills.'
        }
    }

    # Find matching job title
    for job_key, job_data in job_mappings.items():
        if job_key in job_title_lower or any(word in job_title_lower for word in job_key.split()):
            return {
                'title': job_title,
                'keywords': job_data['keywords'],
                'technical_skills': job_data['technical_skills'],
                'soft_skills': job_data['soft_skills'],
                'description': job_data['description']
            }

    # Return default if no match found
    return {
        'title': job_title,
        'keywords': job_mappings['default']['keywords'],
        'technical_skills': job_mappings['default']['technical_skills'],
        'soft_skills': job_mappings['default']['soft_skills'],
        'description': job_mappings['default']['description']
    }


def generate_improvement_suggestions(resume_text: str, job_text: str, match_scores: Dict) -> List[str]:
    """
    Generate intelligent improvement suggestions based on resume-job analysis
    Server-side function that analyzes text deeply to provide personalized recommendations
    """
    processor = ResumeTextProcessor()
    suggestions = []

    try:
        # Analyze resume and job with full processing
        resume_analysis = analyze_resume_text(resume_text)
        job_analysis = analyze_resume_text(job_text)

        overall_score = match_scores.get('overall_score', 0)
        keyword_score = match_scores.get('keyword_score', 0)
        tech_score = match_scores.get('tech_score', 0)

        # Content length analysis
        resume_word_count = len(resume_text.split())
        if resume_word_count < 200:
            suggestions.append("Expand your resume content - aim for 300-500 words to provide more detail about your experience")
        elif resume_word_count > 600:
            suggestions.append("Consider condensing your resume - focus on the most relevant 1-2 years of experience")

        # Intelligent keyword optimization
        if keyword_score < 70:
            job_keywords = [kw[0] for kw in job_analysis['keywords'][:8]]
            resume_keywords = [kw[0] for kw in resume_analysis['keywords'][:10]]

            missing_keywords = [kw for kw in job_keywords if kw not in resume_keywords][:5]
            if missing_keywords:
                suggestions.append(f"Add these job-specific keywords naturally: {', '.join(missing_keywords)}")

        # Technical skills gap analysis
        if tech_score < 70:
            resume_tech = set(resume_analysis['skills']['technical'])
            job_tech = set(job_analysis['skills']['technical'])
            missing_tech = job_tech - resume_tech

            if missing_tech:
                missing_list = list(missing_tech)[:3]
                suggestions.append(f"Highlight experience with these technologies: {', '.join(missing_list)}")
                suggestions.append("Add specific examples of projects or work where you used these technologies")

        # Soft skills enhancement
        resume_soft = set(resume_analysis['skills']['soft'])
        job_soft = set(job_analysis['skills']['soft'])
        missing_soft = job_soft - resume_soft

        if missing_soft and len(suggestions) < 6:
            soft_list = list(missing_soft)[:2]
            suggestions.append(f"Emphasize these soft skills with concrete examples: {', '.join(soft_list)}")

        # Readability improvements based on server analysis
        flesch_score = resume_analysis['readability']['flesch_score']
        if flesch_score < 40:
            suggestions.append("Improve readability by using shorter sentences and simpler language")
        elif flesch_score > 70:
            suggestions.append("Consider adding more industry-specific terminology to strengthen your professional voice")

        # ATS optimization from server analysis
        ats_issues = resume_analysis['ats_analysis']['issues']
        if ats_issues:
            suggestions.append("Fix ATS compatibility issues: " + "; ".join(ats_issues[:2]))

        # Score-based general advice with intelligent prioritization
        if overall_score < 50:
            suggestions.extend([
                "Quantify your achievements with specific metrics (e.g., 'Increased sales by 30%' instead of 'Improved sales')",
                "Tailor your resume specifically for this job by mirroring the job description's language",
                "Use standard section headers (Experience, Education, Skills) that ATS systems can recognize",
                "Ensure consistent formatting and remove complex graphics or tables"
            ])
        elif overall_score < 70:
            suggestions.extend([
                "Add more recent and relevant work experience",
                "Include specific accomplishments and results from your roles",
                "Strengthen your skills section with industry-standard terminology"
            ])
        else:
            suggestions.extend([
                "Your resume is well-matched! Consider adding recent certifications or achievements",
                "Proofread carefully for any typos or grammatical errors",
                "Consider having peers in your industry review your resume"
            ])

        # Remove duplicates and limit to top 8 suggestions
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen and len(unique_suggestions) < 8:
                unique_suggestions.append(suggestion)
                seen.add(suggestion)

        return unique_suggestions

    except Exception as e:
        # Fallback suggestions if analysis fails
        return [
            "Review the job description and incorporate relevant keywords",
            "Quantify your achievements with specific numbers and percentages",
            "Ensure your resume uses standard section headers",
            "Proofread carefully for spelling and grammar",
            "Keep your resume to 1-2 pages with clear formatting"
        ]
