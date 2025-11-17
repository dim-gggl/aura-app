# Patch: upgrade security-sensitive OS packages during build (Debian/Ubuntu based image)
FROM python:3.11-slim AS base

WORKDIR /app

# Security upgrades for urgent vulnerabilities (libxml2, libxslt, xz, pip)
RUN apt-get update && \
    # upgrade only the packages we care about to minimize layer changes
    apt-get install -y --only-upgrade \
      libxml2 \
      libxslt1.1 \
      xz-utils \
      python3-pip \
      libssl3 || true && \
    # if you prefer to upgrade everything, use: apt-get upgrade -y
    rm -rf /var/lib/apt/lists/*

    # Ensure pip is updated to the fixed version that addresses CVE-2025-8869
RUN python3 -m pip install --upgrade pip==25.3
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    gettext \
    curl \
    ca-certificates \
    libexpat1 \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && adduser --disabled-password --gecos '' appuser \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

COPY --chown=appuser:appuser . .
RUN chmod +x /app/entrypoint.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s \
    CMD curl -f http://localhost:${PORT:-8000}/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 aura_app.wsgi:application"]
