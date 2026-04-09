from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from allauth.socialaccount.models import SocialApp

from django.core.files.storage import FileSystemStorage

from django.contrib import messages

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from django.utils import timezone

import json

import os

import logging

from .models import Resume, ResumeAnalysis, JobDescription, ResumeJobMatch, Feedback

# Set up logging
logger = logging.getLogger(__name__)


def _text_processor():
    from . import text_processor
    return text_processor


def generate_improvement_suggestions(*args, **kwargs):
    return _text_processor().generate_improvement_suggestions(*args, **kwargs)


def extract_text_from_pdf(*args, **kwargs):
    return _text_processor().extract_text_from_pdf(*args, **kwargs)


def extract_text_from_docx(*args, **kwargs):
    return _text_processor().extract_text_from_docx(*args, **kwargs)


def analyze_resume_text(*args, **kwargs):
    return _text_processor().analyze_resume_text(*args, **kwargs)


def analyze_job_match(*args, **kwargs):
    return _text_processor().analyze_job_match(*args, **kwargs)


def analyze_job_title(*args, **kwargs):
    return _text_processor().analyze_job_title(*args, **kwargs)





def generate_ats_prediction(score):
    """Generate worded ATS prediction based on score"""
    if score >= 90:
        return "AI-powered ATS prediction: Your resume is exceptionally optimized and should perform extremely well in automated screening."
    elif score >= 80:
        return "AI-powered ATS prediction: Your resume is strong and likely to pass most ATS filters with only minor improvements needed."
    elif score >= 70:
        return "AI-powered ATS prediction: Your resume is reasonably ATS-friendly but could benefit from targeted keyword and formatting updates."
    elif score >= 60:
        return "AI-powered ATS prediction: Your resume is somewhat ATS-friendly but may struggle with stricter automated screening systems."
    else:
        return "AI-powered ATS prediction: Your resume likely needs focused optimization to be parsed successfully by modern ATS platforms."


def home(request):
    google_login_url = None
    try:
        if SocialApp.objects.filter(provider='google', sites__id=settings.SITE_ID).exists():
            google_login_url = reverse('socialaccount_login', args=['google'])
    except Exception:
        google_login_url = None

    return render(request, 'home.html', {
        'google_login_url': google_login_url,
    })





@login_required(login_url='login')
def upload_resume(request):

    """Enhanced resume upload with comprehensive processing"""

    if request.method == 'POST':

        if 'resumeFile' not in request.FILES:

            messages.error(request, 'No file selected.')

            return render(request, 'upload_resume.html')



        resume_file = request.FILES['resumeFile']

        filename = resume_file.name



        # Validate file type

        ext = os.path.splitext(filename)[1].lower()

        if ext not in ['.pdf', '.docx']:

            messages.error(request, 'Please upload a PDF or DOCX file only.')

            return render(request, 'upload_resume.html')



        try:

            # Save file temporarily

            fs = FileSystemStorage()

            saved_filename = fs.save(filename, resume_file)

            file_path = fs.path(saved_filename)



            # Extract text based on file type

            if ext == '.pdf':

                raw_text = extract_text_from_pdf(file_path)

                file_type = 'pdf'

            elif ext == '.docx':

                raw_text = extract_text_from_docx(file_path)

                file_type = 'docx'



            if raw_text.startswith("Error"):

                messages.error(request, f'Failed to extract text: {raw_text}')

                fs.delete(saved_filename)  # Clean up failed upload

                return render(request, 'upload_resume.html')



            # Create Resume model instance

            resume = Resume.objects.create(

                original_filename=filename,

                file_path=saved_filename,

                file_type=file_type,

                raw_text=raw_text,

                word_count=len(raw_text.split()),

                character_count=len(raw_text),

            )



            # Perform comprehensive analysis

            analysis_result = analyze_resume_text(raw_text)



            # Create or update analysis record
            analysis, created = ResumeAnalysis.objects.get_or_create(
                resume=resume,
                defaults={
                    'total_words': len(raw_text.split()),
                    'unique_words': len(set(raw_text.lower().split())),
                    'avg_word_length': sum(len(word) for word in raw_text.split()) / max(1, len(raw_text.split())),
                    'has_contact_info': bool(analysis_result['contact_info']),
                    'has_summary': bool(analysis_result['sections'].get('summary')),
                    'has_experience': bool(analysis_result['sections'].get('experience')),
                    'has_education': bool(analysis_result['sections'].get('education')),
                    'has_skills': bool(analysis_result['sections'].get('skills')),
                    'top_keywords': analysis_result['keywords'],
                    'skill_keywords': analysis_result['skills']['technical'],
                    'soft_skills': analysis_result['skills']['soft'],
                    'flesch_score': analysis_result['readability']['flesch_score'],
                    'grade_level': analysis_result['readability']['grade_level'],
                    'ats_friendly_score': analysis_result['ats_analysis']['score'],
                    'formatting_issues': analysis_result['ats_analysis']['issues']
                }
            )
            
            # If analysis already existed, update it
            if not created:
                analysis.total_words = len(raw_text.split())
                analysis.unique_words = len(set(raw_text.lower().split()))
                analysis.avg_word_length = sum(len(word) for word in raw_text.split()) / max(1, len(raw_text.split()))
                analysis.has_contact_info = bool(analysis_result['contact_info'])
                analysis.has_summary = bool(analysis_result['sections'].get('summary'))
                analysis.has_experience = bool(analysis_result['sections'].get('experience'))
                analysis.has_education = bool(analysis_result['sections'].get('education'))
                analysis.has_skills = bool(analysis_result['sections'].get('skills'))
                analysis.top_keywords = analysis_result['keywords']
                analysis.skill_keywords = analysis_result['skills']['technical']
                analysis.soft_skills = analysis_result['skills']['soft']
                analysis.flesch_score = analysis_result['readability']['flesch_score']
                analysis.grade_level = analysis_result['readability']['grade_level']
                analysis.ats_friendly_score = analysis_result['ats_analysis']['score']
                analysis.formatting_issues = analysis_result['ats_analysis']['issues']
                analysis.save()



            # Update resume with cleaned text and scores

            resume.cleaned_text = analysis_result['preprocessed_text']

            resume.ats_score = analysis_result['ats_analysis']['score']

            resume.readability_score = int(analysis_result['readability']['flesch_score'])

            resume.save()



            # Store in session for backward compatibility

            logger.info(f"Setting resume_id={resume.id} in session (key={request.session.session_key})")

            request.session['resume_id'] = resume.id

            request.session['extracted_text'] = raw_text

            request.session['cleaned_text'] = analysis_result['preprocessed_text']

            request.session.modified = True
            
            request.session.save()  # Explicitly save session to database
            
            logger.info(f"Session saved. Resumeid in session: {request.session.get('resume_id')}")



            messages.success(request, f'Successfully uploaded and analyzed {filename}')

            return redirect('score')



        except Exception as e:

            messages.error(request, f'Upload failed: {str(e)}')

            return render(request, 'upload_resume.html')



    return render(request, 'upload_resume.html')

    



@login_required(login_url='login')
def parsed_resume(request):

    """Enhanced parsed resume view with detailed analysis"""

    resume_id = request.session.get('resume_id')

    if not resume_id:

        messages.warning(request, 'No resume found. Please upload a resume first.')

        return redirect('upload_resume')



    try:

        resume = Resume.objects.get(id=resume_id)

        analysis = ResumeAnalysis.objects.filter(resume=resume).first()



        context = {

            'resume': resume,

            'analysis': analysis,

            'extracted_text': resume.raw_text,

            'cleaned_text': resume.cleaned_text,

            'word_count': resume.word_count,

            'character_count': resume.character_count,

        }

        return render(request, 'parsed_resume.html', context)



    except Resume.DoesNotExist:

        messages.error(request, 'Resume not found. Please upload again.')

        return redirect('upload_resume')





@login_required(login_url='login')
def preprocessed_resume(request):

    """Display preprocessed resume text"""

    resume_id = request.session.get('resume_id')

    if not resume_id:

        messages.warning(request, 'No resume found. Please upload a resume first.')

        return redirect('upload_resume')



    try:

        resume = Resume.objects.get(id=resume_id)

        context = {

            'resume': resume,

            'preprocessed_text': resume.cleaned_text,

        }

        return render(request, 'preprocessed_resume.html', context)



    except Resume.DoesNotExist:

        messages.error(request, 'Resume not found. Please upload again.')

        return redirect('upload_resume')





@login_required(login_url='login')
def analysis(request):

    """Display detailed resume analysis"""

    resume_id = request.session.get('resume_id')

    if not resume_id:

        messages.warning(request, 'No resume found. Please upload a resume first.')

        return redirect('upload_resume')



    try:

        resume = Resume.objects.get(id=resume_id)

        analysis = ResumeAnalysis.objects.filter(resume=resume).first()



        context = {

            'resume': resume,

            'analysis': analysis,

        }

        return render(request, 'analysis.html', context)



    except Resume.DoesNotExist:

        messages.error(request, 'Resume not found. Please upload again.')

        return redirect('upload_resume')





@login_required(login_url='login')
def score(request):

    """Display resume scores"""

    resume_id = request.session.get('resume_id')
    logger.info(f"SCORE VIEW - Session Key: {request.session.session_key}")
    logger.info(f"SCORE VIEW - Resume ID from session: {resume_id}")

    # Try to get resume from session, or get the latest one if not in session
    if not resume_id:
        # Fallback: Get the most recent resume
        latest_resume = Resume.objects.order_by('-uploaded_at').first()
        if latest_resume:
            resume_id = latest_resume.id
            logger.info(f"SCORE VIEW - Using latest resume from DB: {resume_id}")
            request.session['resume_id'] = resume_id
            request.session.modified = True
            request.session.save()  # Explicitly save session to database
        else:
            logger.error("SCORE VIEW - No resume found")
            messages.warning(request, 'No resume found. Please upload a resume first.')
            return redirect('upload_resume')

    try:

        resume = Resume.objects.get(id=resume_id)

        analysis = ResumeAnalysis.objects.filter(resume=resume).first()



        # Calculate final score as weighted average

        ats_score = resume.ats_score or 0

        readability_score = resume.readability_score or 0

        # Add other factors for final score

        content_score = 0

        if analysis:

            # Calculate content completeness score

            content_factors = [

                analysis.has_contact_info,

                analysis.has_summary,

                analysis.has_experience,

                analysis.has_education,

                analysis.has_skills

            ]

            content_score = (sum(content_factors) / len(content_factors)) * 100



        final_score = int((ats_score * 0.4) + (readability_score * 0.3) + (content_score * 0.3))



        # Determine grade

        if final_score >= 90:

            grade = 'A'

        elif final_score >= 80:

            grade = 'B'

        elif final_score >= 70:

            grade = 'C'

        elif final_score >= 60:

            grade = 'D'

        else:

            grade = 'F'



        # Prepare comprehensive ATS analysis data with worded descriptions
        ats_analysis = {
            'score': ats_score,
            'issues': analysis.formatting_issues if analysis else [],
            'recommendations': [
                "Use standard section headers (Experience, Skills, Education)",
                "Include quantifiable achievements with metrics",
                "Avoid complex formatting and tables",
                "Use common keywords from job descriptions",
                "Keep consistent formatting throughout"
            ],
            'prediction': generate_ats_prediction(ats_score),
            'status': 'excellent' if ats_score >= 90 else 'good' if ats_score >= 80 else 'fair' if ats_score >= 70 else 'needs_improvement'
        }

        context = {

            'resume': resume,

            'analysis': analysis,

            'final_score': final_score,

            'grade': grade,

            'ats_score': ats_score,

            'readability_score': readability_score,

            'content_score': content_score,

            'ats_analysis': ats_analysis,

        }

        return render(request, 'score.html', context)



    except Resume.DoesNotExist:

        messages.error(request, 'Resume not found. Please upload again.')

        return redirect('upload_resume')





@login_required(login_url='login')
def jobmatch(request):
    """
    Job matching: 
    1. Get resume from session or database
    2. If GET: Show job description input form
    3. If POST: Analyze job description against resume
    """
    
    # STEP 1: Get the resume - try session first, then latest from DB
    resume_id = request.session.get('resume_id')
    logger.info(f"JOBMATCH REQUEST - Method: {request.method}, Session resume_id: {resume_id}")
    
    resume = None
    analysis = None
    
    # Try session ID first
    if resume_id:
        try:
            resume = Resume.objects.get(id=resume_id)
            logger.info(f"Found resume {resume_id} from session")
        except Resume.DoesNotExist:
            logger.warning(f"Resume {resume_id} from session not in DB")
            if 'resume_id' in request.session:
                del request.session['resume_id']
            request.session.modified = True
    
    # Fallback: Get latest resume from database
    if not resume:
        resume = Resume.objects.order_by('-uploaded_at').first()
        if resume:
            logger.info(f"Using latest resume from DB: {resume.id}")
            request.session['resume_id'] = resume.id
            request.session.save()
        else:
            logger.error("No resume found in database at all")
    
    # Get analysis if resume exists
    if resume:
        analysis = ResumeAnalysis.objects.filter(resume=resume).first()
        logger.info(f"Resume found: {resume.id}, Analysis: {analysis is not None}")
    
    # STEP 2: Handle POST (form submission with job description)
    if request.method == 'POST':
        
        # No resume = redirect to upload
        if not resume:
            logger.error("POST request but no resume found")
            messages.error(request, 'Resume not found. Please upload a resume first.')
            return redirect('upload_resume')
        
        # Get job description from form or file
        job_description = request.POST.get('job_description', '').strip()
        job_file = request.FILES.get('job_file')
        
        logger.info(f"POST received - job_description length: {len(job_description)}, has file: {job_file is not None}")
        
        # If file uploaded, extract text
        if job_file and not job_description:
            try:
                filename = job_file.name.lower()
                if filename.endswith('.pdf'):
                    job_description = extract_text_from_pdf(job_file)
                elif filename.endswith('.docx'):
                    job_description = extract_text_from_docx(job_file)
                elif filename.endswith('.txt'):
                    job_description = job_file.read().decode('utf-8')
                    
                if job_description.startswith('Error'):
                    raise Exception(job_description)
                    
            except Exception as e:
                logger.error(f"File extraction failed: {str(e)}")
                messages.error(request, f'Could not read file: {str(e)}')
                return render(request, 'jobmatch.html', {'resume': resume, 'analysis': analysis})
        
        # Validate job description exists
        if not job_description:
            logger.warning("No job description provided")
            messages.error(request, 'Please paste job description or upload a file.')
            return render(request, 'jobmatch.html', {'resume': resume, 'analysis': analysis})
        
        # STEP 3: Run analysis
        try:
            resume_text = resume.cleaned_text or resume.raw_text
            logger.info(f"Starting analysis - resume text length: {len(resume_text)}, job desc length: {len(job_description)}")
            
            # Analyze resume vs job description
            match_result = analyze_job_match(resume_text, job_description)
            logger.info(f"Analysis complete - score: {match_result.get('overall_score', 0)}")
            
            # Generate suggestions
            suggestions = generate_improvement_suggestions(
                resume_text,
                job_description,
                match_result
            )
            logger.info(f"Suggestions generated: {len(suggestions)} items")
            
            # Save match record
            job_match = ResumeJobMatch.objects.create(
                resume=resume,
                job_description=job_description[:500],  # Store first 500 chars as preview
                match_score=match_result['overall_score'],
                matched_keywords=match_result.get('matched_keywords', []),
                missing_keywords=match_result.get('missing_keywords', []),
                suggestions=suggestions
            )
            
            # Prepare context for template with match_results
            context = {
                'resume': resume,
                'analysis': analysis,
                'job_description_text': job_description[:300] + ('...' if len(job_description) > 300 else ''),
                'match_results': {
                    'overall_score': int(match_result.get('overall_score', 0)),
                    'keyword_score': int(match_result.get('keyword_score', 0)),
                    'tech_score': int(match_result.get('technical_score', 0)),
                    'soft_skills_score': int(match_result.get('soft_skills_score', 0)),
                    'matched_keywords': match_result.get('matched_keywords', [])[:25],
                    'missing_keywords': match_result.get('missing_keywords', [])[:25],
                    'matched_tech_skills': match_result.get('matched_tech_skills', [])[:15],
                    'missing_tech_skills': match_result.get('missing_tech_skills', [])[:15],
                    'matched_soft_skills': match_result.get('matched_soft_skills', [])[:10],
                    'missing_soft_skills': match_result.get('missing_soft_skills', [])[:10],
                    'keyword_coverage': round(match_result.get('keyword_coverage', 0), 1),
                    'total_resume_keywords': match_result.get('total_resume_keywords', 0),
                    'total_job_keywords': match_result.get('total_job_keywords', 0),
                },
                'suggestions': suggestions[:5],  # Limit to 5 suggestions for display
                'job_match_id': job_match.id,
            }
            
            logger.info(f"Rendering results - match_results keys: {list(context['match_results'].keys())}")
            return render(request, 'jobmatch.html', context)
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            messages.error(request, f'Analysis failed: {str(e)}')
            return render(request, 'jobmatch.html', {'resume': resume, 'analysis': analysis})
    
    # STEP 3: GET request - show form with resume info
    context = {
        'resume': resume,
        'analysis': analysis,
    }
    logger.info(f"GET request - returning form with resume: {resume is not None}")
    return render(request, 'jobmatch.html', context)





@login_required(login_url='login')
def feedback(request):
    """Collect user feedback on analysis results"""
    
    logger.info(f"Feedback view accessed. Session key: {request.session.session_key}")
    
    if request.method == 'POST':
        # Get resume from session or latest from DB
        resume_id = request.session.get('resume_id')
        if not resume_id:
            logger.warning("No resume_id in session, trying latest resume")
            resume = Resume.objects.order_by('-uploaded_at').first()
        else:
            resume = Resume.objects.filter(id=resume_id).first()

        if not resume:
            logger.error("No resume found for feedback")
            messages.error(request, 'No resume found. Please upload a resume first.')
            return redirect('upload_resume')

        # Get feedback data from form
        rating = request.POST.get('rating')
        comments = request.POST.get('comments', '').strip()
        analysis_helpful = request.POST.get('analysis_helpful') == 'on'
        suggestions_useful = request.POST.get('suggestions_useful') == 'on'
        would_recommend = request.POST.get('would_recommend') == 'on'
        job_match_id = request.POST.get('job_match_id')
        helpful_suggestions = []
        if analysis_helpful:
            helpful_suggestions.append('analysis_helpful')
        if suggestions_useful:
            helpful_suggestions.append('suggestions_useful')
        if would_recommend:
            helpful_suggestions.append('would_recommend')

        if not rating:
            messages.error(request, 'Please select a rating.')
            return redirect('feedback')

        try:
            # Create feedback record
            feedback_obj = Feedback.objects.create(
                resume=resume,
                rating=int(rating),
                comments=comments,
                analysis_helpful=analysis_helpful,
                suggestions_useful=suggestions_useful,
                would_recommend=would_recommend
            )

            if job_match_id:
                job_match = ResumeJobMatch.objects.filter(id=job_match_id, resume=resume).first()
                if job_match:
                    job_match.helpful_suggestions = helpful_suggestions
                    job_match.feedback_text = comments
                    job_match.save()

            logger.info(f"Feedback saved: ID={feedback_obj.id}, Rating={rating}")
            messages.success(request, 'Thank you for your feedback! We appreciate your input.')
            return redirect('home')

        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            messages.error(request, 'Error saving feedback. Please try again.')
            return redirect('feedback')
    
    # GET request - display feedback form
    resume_id = request.session.get('resume_id')
    resume = None
    if resume_id:
        resume = Resume.objects.filter(id=resume_id).first()
    
    if not resume:
        resume = Resume.objects.order_by('-uploaded_at').first()
    
    # Get latest job match for the resume to display in feedback summary
    job_match = None
    match_results = None
    recommendations = []
    if resume:
        job_match = ResumeJobMatch.objects.filter(resume=resume).order_by('-created_at').first()
        if job_match:
            match_results = {
                'overall_score': int(job_match.match_score),
                'keyword_score': 0,
                'tech_score': 0,
            }
            recommendations = job_match.suggestions[:5]  # Limit to 5 suggestions
    
    context = {
        'resume': resume,
        'job_match': job_match,
        'match_results': match_results,
        'recommendations': recommendations,
        'session': request.session
    }
    return render(request, 'feedback.html', context)





@login_required(login_url='login')
def builder(request):

    """Resume builder interface"""

    return render(request, 'builder.html')





@login_required(login_url='login')
def resume_history(request):

    """Display resume analysis history"""

    resumes = Resume.objects.all().order_by('-uploaded_at')

    context = {

        'resumes': resumes,

    }

    return render(request, 'history.html', context)





# API Endpoints





@csrf_exempt

def api_analyze_resume(request):

    """API endpoint for resume analysis"""

    if request.method == 'POST':

        try:

            data = json.loads(request.body)

            resume_text = data.get('resume_text', '')



            if not resume_text:

                return JsonResponse({'error': 'No resume text provided'}, status=400)



            analysis_result = analyze_resume_text(resume_text)



            return JsonResponse({

                'success': True,

                'analysis': analysis_result

            })



        except Exception as e:

            return JsonResponse({'error': str(e)}, status=500)



    return JsonResponse({'error': 'Method not allowed'}, status=405)





@csrf_exempt

def api_match_job(request):

    """API endpoint for job matching"""

    if request.method == 'POST':

        try:

            data = json.loads(request.body)

            resume_text = data.get('resume_text', '')

            job_description = data.get('job_description', '')



            if not resume_text or not job_description:

                return JsonResponse({'error': 'Resume text and job description required'}, status=400)



            match_result = analyze_job_match(resume_text, job_description)



            return JsonResponse({

                'success': True,

                'match': match_result

            })



        except Exception as e:

            return JsonResponse({'error': str(e)}, status=500)



    return JsonResponse({'error': 'Method not allowed'}, status=405)





@csrf_exempt

def api_get_suggestions(request):

    """API endpoint for improvement suggestions"""

    if request.method == 'POST':

        try:

            data = json.loads(request.body)

            resume_text = data.get('resume_text', '')

            job_description = data.get('job_description', '')

            match_scores = data.get('match_scores', {})



            if not resume_text or not job_description:

                return JsonResponse({'error': 'Resume text and job description required'}, status=400)



            suggestions = generate_improvement_suggestions(

                resume_text,

                job_description,

                match_scores

            )



            return JsonResponse({

                'success': True,

                'suggestions': suggestions

            })



        except Exception as e:

            return JsonResponse({'error': str(e)}, status=500)



    return JsonResponse({'error': 'Method not allowed'}, status=405)
