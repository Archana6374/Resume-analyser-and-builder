import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Resume


class SaveResumeTests(TestCase):
    def test_save_resume_persists_payload_to_database(self):
        user = User.objects.create_user(username='tester', password='secret123')
        self.client.force_login(user)

        payload = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone': '1234567890',
            'linkedin': 'https://linkedin.com/in/janedoe',
            'github': 'https://github.com/janedoe',
            'portfolio': 'https://janedoe.dev',
            'summary': 'Backend developer with strong Django and API experience.',
            'tech_skills': ['Python', 'Django'],
            'soft_skills': ['Communication', 'Leadership'],
            'activities': 'Volunteer mentor',
            'certifications': 'AWS Cloud Practitioner',
            'projects': 'Resume platform',
            'template': 'classic',
            'experience': [{'title': 'Developer', 'org': 'Acme', 'period': '2024', 'loc': 'Remote', 'details': 'Built APIs'}],
            'education': [{'title': 'B.Tech', 'org': 'Example University', 'period': '2023', 'loc': 'Chennai', 'details': 'Computer Science'}],
        }

        response = self.client.post(
            reverse('save_resume'),
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Resume.objects.count(), 1)
        resume = Resume.objects.get()
        self.assertEqual(resume.user, user)
        self.assertEqual(resume.name, payload['name'])
        self.assertEqual(resume.skills, 'Python,Django,Communication,Leadership')
        self.assertEqual(resume.experience[0]['title'], 'Developer')

    def test_save_resume_accepts_comma_separated_skill_strings(self):
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '9876543210',
            'summary': 'Full stack developer with product delivery experience.',
            'tech_skills': 'Python, Django, SQL',
            'soft_skills': 'Communication, Teamwork',
            'experience': [{'title': 'Engineer', 'org': 'Acme', 'details': 'Delivered features'}],
            'education': [{'title': 'B.Sc', 'org': 'College', 'details': 'CS'}],
        }

        response = self.client.post(
            reverse('save_resume'),
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Resume.objects.get().skills, 'Python,Django,SQL,Communication,Teamwork')


class AuthRedirectTests(TestCase):
    def test_login_page_exposes_google_sso_url(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['google_login_url'], reverse('google_login') + '?next=/profile/')

    def test_register_page_exposes_google_sso_url_with_next(self):
        response = self.client.get(reverse('register') + '?next=/builder/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['google_login_url'], reverse('google_login') + '?next=/builder/')

    def test_login_redirects_to_profile_by_default(self):
        User.objects.create_user(username='tester', password='secret123')

        response = self.client.post(
            reverse('login'),
            data={
                'username': 'tester',
                'password': 'secret123',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

    def test_logout_redirects_to_landing_page(self):
        user = User.objects.create_user(username='tester2', password='secret123')
        self.client.force_login(user)

        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))
