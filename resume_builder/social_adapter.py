from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class NoProxySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_requests_session(self):
        session = super().get_requests_session()
        session.trust_env = False
        return session
