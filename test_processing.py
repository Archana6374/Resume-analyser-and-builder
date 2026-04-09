#!/usr/bin/env python
"""
Test script for resume text processing functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.text_processor import ResumeTextProcessor, analyze_resume_text

def test_text_processing():
    """Test the text processing functionality"""

    # Sample resume text
    sample_resume = """
    JOHN DOE
    Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years in Python, Django, and React development.
    Passionate about creating scalable web applications and mentoring junior developers.

    SKILLS
    Python, Django, React, JavaScript, PostgreSQL, AWS, Docker, Git

    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2020-Present
    - Developed and maintained Django-based web applications serving 10k+ users
    - Led a team of 3 developers on microservices architecture migration
    - Improved application performance by 40% through code optimization

    Software Engineer | Startup Inc | 2018-2020
    - Built responsive React interfaces for e-commerce platform
    - Implemented REST APIs using Django REST framework
    - Collaborated with design team to improve user experience

    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology | 2014-2018
    GPA: 3.8/4.0
    """

    print("Testing Resume Text Processing...")
    print("=" * 50)

    # Test basic analysis
    result = analyze_resume_text(sample_resume)

    print(f"Contact Info Found: {bool(result['contact_info'])}")
    print(f"Email: {result['contact_info'].get('email', 'Not found')}")
    print(f"Phone: {result['contact_info'].get('phone', 'Not found')}")

    print(f"\nSkills Detected:")
    print(f"Technical: {result['skills']['technical']}")
    print(f"Soft: {result['skills']['soft']}")

    print(f"\nReadability Score: {result['readability']['flesch_score']:.1f}")
    print(f"Grade Level: {result['readability']['grade_level']:.1f}")

    print(f"\nTop Keywords: {result['keywords'][:5]}")

    print(f"\nATS Score: {result['ats_analysis']['score']}%")
    print(f"ATS Issues: {result['ats_analysis']['issues']}")

    print("\n✅ Text processing test completed successfully!")

if __name__ == "__main__":
    test_text_processing()