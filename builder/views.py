from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse, JsonResponse
from .models import Resume
from analyzer.models import Resume as AnalyzedResume
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
import json
import os
import requests
import hmac
import hashlib
import base64


#login imports 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.decorators import login_required

FEATURE_PAGES = {
    'resume-builder': {
        'title': 'Resume Builder',
        'summary': 'Build a polished resume with guided templates, section prompts, and clear formatting.',
        'details': 'Our builder helps you create professional resumes with easy editing, structured sections, and ATS-friendly output.',
        'login_next': '/builder/'
    },
    'resume-analyzer': {
        'title': 'Resume Analyzer',
        'summary': 'Upload your resume and get detailed AI-driven feedback on skills, formatting, and ATS compatibility.',
        'details': 'Analyze your resume to identify strengths, missing keywords, and formatting issues before applying to jobs.',
        'login_next': '/analyzer/upload/'
    },
    'ats-score': {
        'title': 'ATS Score & Suggestions',
        'summary': 'See how your resume performs against applicant tracking systems and improve it with actionable suggestions.',
        'details': 'Get a clear ATS compatibility score, formatting recommendations, and keyword optimization tips.',
        'login_next': '/analyzer/score/'
    }
}

PREMIUM_TEMPLATE_PRICING = {
    'executive': {'amount': 19900, 'name': 'Executive', 'description': 'Executive ATS premium template'},
    'studio': {'amount': 24900, 'name': 'Studio', 'description': 'Studio Portfolio premium template'},
    'prestige': {'amount': 29900, 'name': 'Prestige', 'description': 'Prestige Editorial premium template'},
    'signature': {'amount': 34900, 'name': 'Signature', 'description': 'Signature Luxe premium template'},
}


def is_manual_payment_testing_enabled():
    raw = os.getenv('MANUAL_PAYMENT_TESTING', '')
    if raw:
        return raw.strip().lower() in {'1', 'true', 'yes', 'on'}
    return bool(getattr(settings, 'DEBUG', False))


def _coerce_skill_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(',') if item.strip()]
    return []

@csrf_exempt
def chat_bot(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Use POST to chat with the resume assistant."}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"reply": "Invalid request payload."}, status=400)

    user_message = payload.get('message')
    chat_history = payload.get('chat_history', [])
    resume_text = payload.get('resume_text', "")

    if not user_message:
        return JsonResponse({"reply": "Please ask a question so I can help."}, status=400)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        fallback = _local_reply(user_message, resume_text)
        print("[ChatBot] GEMINI_API_KEY not configured, using local fallback.")
        return JsonResponse({"reply": fallback})

    history_text = "\n".join([f"{h['role']}: {h['content']}" for h in chat_history])
    prompt = f"""
You are a resume assistant AI.
Previous conversation: {history_text}
User's resume content: {resume_text}
Respond helpfully to the user input: {user_message}
"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    body = {
        "prompt": prompt,
        "max_tokens": 250
    }

    try:
        ai_response = requests.post(
            "https://api.gemini.ai/v1/chat",
            headers=headers,
            json=body,
            timeout=15
        )
        ai_response.raise_for_status()
        ai_json = ai_response.json()
        reply = ai_json.get("text") or ai_json.get("reply") or ai_json.get("message") or "Sorry, cannot process right now."
    except Exception as exc:
        print(f"[ChatBot] External API request failed: {exc!r}")
        reply = _local_reply(user_message, resume_text)

    return JsonResponse({"reply": reply})


def _local_reply(user_message, resume_text):
    lower = user_message.lower()
    if "skill" in lower or "strength" in lower:
        return "Focus on resume skills that match the job. Put the strongest technical and transferable skills at the top."
    if "experience" in lower or "job" in lower:
        return "List your most recent and relevant work experience first, with achievements and metrics when possible."
    if "write summary" in lower or "summary" in lower or "objective" in lower:
        role = "software developer" if "software developer" in lower else "your desired role"
        return (f"Experienced {role} with a strong foundation in developing scalable applications, "
                "collaborating with cross-functional teams, and delivering high-quality software solutions. "
                "Known for strong problem-solving skills, clean code, and a focus on driving business outcomes.")
    if "format" in lower or "layout" in lower:
        return "Use clear section headings, bullet points, and a simple font. Keep your resume easy to scan for both humans and ATS."
    if "education" in lower:
        return "Include your highest degree, institution, graduation year, and any relevant coursework or certifications."
    if resume_text:
        return "Based on your resume content, try to emphasize your top achievements and the skills that match your target role."
    return "Ask me about resume format, skills, experience, or how to make your resume stronger."
def landing(request):
    google_login_url = get_google_login_url()

    return render(request, 'landing.html', {
        'google_login_url': google_login_url,
    })

def feature_detail(request, feature_slug):
    feature = FEATURE_PAGES.get(feature_slug)
    if not feature:
        return redirect('landing')

    next_url = request.GET.get('next', feature['login_next'])
    login_url = reverse('login') + f'?next={next_url}'
    register_url = reverse('register') + f'?next={next_url}'
    google_login_url = get_google_login_url(next_url)

    if request.user.is_authenticated:
        return redirect(next_url)

    return render(request, 'feature_detail.html', {
        'feature': feature,
        'login_url': login_url,
        'register_url': register_url,
        'google_login_url': google_login_url,
        'next': next_url,
    })

@login_required(login_url='login')
def builder(request):
    razorpay_configured = bool(
        os.getenv('RAZORPAY_KEY_ID', '').strip() and os.getenv('RAZORPAY_KEY_SECRET', '').strip()
    )
    return render(request, 'builder.html', {
        'manual_payment_testing': is_manual_payment_testing_enabled(),
        'razorpay_configured': razorpay_configured,
    })

def get_google_login_url(next_url=None):
    try:
        google_login_url = reverse('google_login')
        if next_url:
            google_login_url = f"{google_login_url}?next={next_url}"
        return google_login_url
    except NoReverseMatch:
        return None


@csrf_exempt
def save_resume(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "error": "Invalid JSON in request body"
            }, status=400)

        # Combine tech_skills and soft_skills
        tech_skills = _coerce_skill_list(data.get("tech_skills", []))
        soft_skills = _coerce_skill_list(data.get("soft_skills", []))
        all_skills = tech_skills + soft_skills

        try:
            user = request.user if request.user.is_authenticated else None
            resume = Resume.objects.create(
                user=user,
                name=data.get("name"),
                email=data.get("email"),
                phone=data.get("phone"),
                linkedin=data.get("linkedin", ""),
                github=data.get("github", ""),
                portfolio=data.get("portfolio", ""),
                summary=data.get("summary", ""),
                skills=",".join(all_skills),
                activities=data.get("activities", ""),
                certifications=data.get("certifications", ""),
                projects=data.get("projects", ""),
                template=data.get("template", "classic"),
                experience=data.get("experience", []),
                education=data.get("education", [])
            )
        except Exception as exc:
            print("SAVE_RESUME_ERROR:", repr(exc))
            return JsonResponse({
                "error": "Resume save failed",
                "details": str(exc),
                "type": type(exc).__name__
            }, status=500)

        return JsonResponse({
            "message": "Resume saved successfully!",
            "id": resume.id
        })
    
    return JsonResponse({
        "error": "Method not allowed"
    }, status=405)
# login modules

def login_view(request):
    next_url = request.GET.get('next', '/profile/')
    google_login_url = get_google_login_url(next_url)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', next_url)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect(next_url)

        messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {
        'next': next_url,
        'google_login_url': google_login_url
    })
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('landing')

#register view
def register_view(request):
    next_url = request.GET.get('next', '/profile/')
    google_login_url = get_google_login_url(next_url)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        next_url = request.POST.get('next', next_url)

        errors = []

        if not username:
            errors.append('Username is required.')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already exists.')

        if not email:
            errors.append('Email is required.')
        elif User.objects.filter(email=email).exists():
            errors.append('Email already registered.')

        if password != password_confirm:
            errors.append('Passwords do not match.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'register.html', {'next': next_url, 'google_login_url': google_login_url})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        authenticated_user = authenticate(request, username=username, password=password)
        if authenticated_user is not None:
            login(request, authenticated_user)
            messages.success(request, 'Account created successfully.')
            return redirect(next_url)

        messages.error(request, 'Registration succeeded, but automatic login failed. Please log in manually.')
        return redirect('login')

    return render(request, 'register.html', {'next': next_url, 'google_login_url': google_login_url})

#dashboard view
@login_required(login_url='login')

def dashboard(request):
    try:
        resumes = AnalyzedResume.objects.filter(user=request.user).order_by('-uploaded_at')[:10]

        total_resumes = resumes.count()

        ats_scores = resumes.values_list('ats_score', flat=True)
        avg_ats_score = round(sum(ats_scores) / len(ats_scores)) if ats_scores else 0
        best_ats_score = max(ats_scores) if ats_scores else 0

        context = {
            'resumes': resumes,
            'total_resumes': total_resumes,
            'avg_ats_score': avg_ats_score,
            'best_ats_score': best_ats_score,
        }

        return render(request, 'dashboard.html', context)

    except Exception:
        return render(request, 'dashboard.html', {
            'resumes': [],
            'total_resumes': 0,
            'avg_ats_score': 0,
            'best_ats_score': 0,
        })


@csrf_exempt
def create_razorpay_order(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    template_key = str(payload.get('template') or '').strip().lower()
    pricing = PREMIUM_TEMPLATE_PRICING.get(template_key)
    if not pricing:
        return JsonResponse({'error': 'Invalid premium template selected'}, status=400)

    if is_manual_payment_testing_enabled():
        return JsonResponse({
            'key': 'manual_test_key',
            'order_id': f'manual_{template_key}_{os.urandom(6).hex()}',
            'amount': pricing['amount'],
            'currency': 'INR',
            'template': template_key,
            'template_name': pricing['name'],
            'description': pricing['description'],
            'manual_testing': True,
            'message': 'Manual payment testing is enabled. No real payment will be charged.'
        })

    razorpay_key_id = os.getenv('RAZORPAY_KEY_ID', '').strip()
    razorpay_key_secret = os.getenv('RAZORPAY_KEY_SECRET', '').strip()
    if not razorpay_key_id or not razorpay_key_secret:
        return JsonResponse({
            'error': 'Razorpay is not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.'
        }, status=500)

    auth_token = base64.b64encode(f'{razorpay_key_id}:{razorpay_key_secret}'.encode('utf-8')).decode('ascii')
    receipt = f'{template_key}-{request.user.id if request.user.is_authenticated else "guest"}-{os.urandom(4).hex()}'
    order_payload = {
        'amount': pricing['amount'],
        'currency': 'INR',
        'receipt': receipt[:40],
        'notes': {
            'template': template_key,
            'user': str(request.user.id if request.user.is_authenticated else 'guest'),
        }
    }

    try:
        response = requests.post(
            'https://api.razorpay.com/v1/orders',
            headers={
                'Authorization': f'Basic {auth_token}',
                'Content-Type': 'application/json',
            },
            json=order_payload,
            timeout=20,
        )
        response.raise_for_status()
        order = response.json()
    except requests.RequestException as exc:
        details = ''
        if exc.response is not None:
            details = exc.response.text
        return JsonResponse({
            'error': 'Unable to create Razorpay order',
            'details': details or str(exc),
        }, status=502)

    return JsonResponse({
        'key': razorpay_key_id,
        'order_id': order.get('id'),
        'amount': order.get('amount'),
        'currency': order.get('currency', 'INR'),
        'template': template_key,
        'template_name': pricing['name'],
        'description': pricing['description'],
    })


@csrf_exempt
def verify_razorpay_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    template_key = str(payload.get('template') or '').strip().lower()
    if is_manual_payment_testing_enabled():
        if template_key not in PREMIUM_TEMPLATE_PRICING:
            return JsonResponse({'error': 'Invalid premium template selected'}, status=400)
        manual_reference = str(payload.get('manual_reference') or payload.get('payment_id') or '').strip()
        if not manual_reference:
            return JsonResponse({'error': 'Missing manual payment reference'}, status=400)
        return JsonResponse({
            'verified': True,
            'manual_testing': True,
            'template': template_key,
            'reference': manual_reference,
        })

    razorpay_key_secret = os.getenv('RAZORPAY_KEY_SECRET', '').strip()
    if not razorpay_key_secret:
        return JsonResponse({
            'error': 'Razorpay is not configured. Set RAZORPAY_KEY_SECRET.'
        }, status=500)

    order_id = str(payload.get('order_id') or '').strip()
    payment_id = str(payload.get('payment_id') or '').strip()
    signature = str(payload.get('signature') or '').strip()
    if not order_id or not payment_id or not signature:
        return JsonResponse({'error': 'Missing payment verification fields'}, status=400)

    generated_signature = hmac.new(
        razorpay_key_secret.encode('utf-8'),
        f'{order_id}|{payment_id}'.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()

    is_valid = hmac.compare_digest(generated_signature, signature)
    if not is_valid:
        return JsonResponse({'error': 'Payment signature verification failed'}, status=400)

    return JsonResponse({'verified': True, 'template': template_key or None})
