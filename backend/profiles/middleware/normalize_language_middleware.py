"""
Normalize non-canonical language tags in headers/cookies/querystrings
to Django's expected form (e.g., 'en_US' -> 'en-us', 'us-US' -> 'en-us').
"""


from django.utils.deprecation import MiddlewareMixin


class NormalizeLanguageMiddleware(MiddlewareMixin):
    """
    Normalize non-canonical language tags in headers/cookies/querystrings
    to Django's expected form (e.g., 'en_US' -> 'en-us', 'us-US' -> 'en-us').
    """
    def process_request(self, request):
        """
        Processing the request with propper language
        """
        def canon(tag: str) -> str:
            if not tag:
                return tag
            tag = tag.replace("_", "-")
            parts = tag.split("-", 1)
            lang = parts[0].lower()
            region = parts[1].lower() if len(parts) > 1 else ""
            # Map odd variants like 'us-US' to 'en-us'
            if lang in ("us", "en"):
                lang = "en"
                region = "us" if region in ("us", "usa") or not region else region
            if lang == "et" and region in ("ee", ""):
                region = ""  # prefer canonical 'et'
            return f"{lang}-{region}" if region else lang

        # Accept-Language header
        al = request.META.get("HTTP_ACCEPT_LANGUAGE")
        if al:
            # very light-weight normalization; leave q-values as-is
            normalized = ",".join(
                [canon(chunk.split(";")[0].strip()) + (";" + ";".join(chunk.split(";")[1:]) if ";" in chunk else "")
                 for chunk in al.split(",")]
            )
            request.META["HTTP_ACCEPT_LANGUAGE"] = normalized

        # ?lang= and language cookie normalizations (optional)
        if "lang" in request.GET:
            req = request.GET.copy()
            req["lang"] = canon(req.get("lang"))
            request.GET = req

        cookie_name = "django_language"
        if cookie_name in request.COOKIES:
            request.COOKIES[cookie_name] = canon(request.COOKIES[cookie_name])
