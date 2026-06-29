import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


NEWS_API_BASE = "https://newsapi.org/v2"


class NewsView(APIView):
    """Fetch top headlines. Free tier gets headlines only; Pro/Premium get full articles."""

    def get(self, request):
        category = request.query_params.get("category", "general")
        country = request.query_params.get("country", "ke")  # Kenya by default
        query = request.query_params.get("q", "")

        params = {
            "apiKey": settings.NEWS_API_KEY,
            "pageSize": 10,
        }

        if query:
            params["q"] = query
            params["sortBy"] = "publishedAt"
            url = f"{NEWS_API_BASE}/everything"
        else:
            params["country"] = country
            params["category"] = category
            url = f"{NEWS_API_BASE}/top-headlines"

        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=502)

        # Free tier: strip article content
        user = request.user
        if user.tier == user.TIER_FREE:
            articles = [
                {
                    "title": a["title"],
                    "source": a["source"],
                    "publishedAt": a["publishedAt"],
                    "urlToImage": a["urlToImage"],
                    "url": a["url"],
                    "description": a["description"],
                    "content": None,  # paywalled
                }
                for a in articles
            ]

        return Response({"articles": articles})
