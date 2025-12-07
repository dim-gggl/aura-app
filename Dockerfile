# On passe à 3.12-slim pour une base système plus récente et sécurisée
FROM python:3.12-slim-bookworm AS base

WORKDIR /app

# Mise à jour des paquets système critiques
# Debian Bookworm (base de 3.12) a déjà des versions plus récentes, 
# mais on garde l'upgrade de sécurité par prudence.
RUN apt-get update && \
    apt-get install -y --only-upgrade \
      libxml2 \
      libxslt1.1 \
      xz-utils \
      libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Pip est mis à jour, mais Python 3.12 gère nativement la sécurité des archives (PEP 706)
# On installe aussi setuptools/wheel pour éviter les erreurs liées à la suppression de distutils
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --ignore-requires-python

# Runtime
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    gettext \
    curl \
    ca-certificates \
    libexpat1 \
    # On nettoie immédiatement pour garder l'image légère
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos '' appuser \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

# Copie des packages depuis le builder
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

COPY --chown=appuser:appuser . .
RUN chmod +x /app/entrypoint.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s \
    CMD curl -f http://localhost:${PORT:-8000}/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 aura_app.wsgi:application"]