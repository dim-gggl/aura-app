from django.core.cache import cache
from django.template.loader import render_to_string
from weasyprint import HTML

CACHE_TTL = 60 * 60  # 1h


class PDFService:
    @staticmethod
    def render_to_pdf(template_name: str, context: dict, cache_key: str) -> bytes:
        cached = cache.get(cache_key)
        if cached:
            return cached
        html = render_to_string(template_name, context)
        pdf_bytes = HTML(string=html).write_pdf()
        cache.set(cache_key, pdf_bytes, CACHE_TTL)
        return pdf_bytes
