# Utilisation d'une image Python 3.12 slim Bookworm à jour (corrige vuln. zlib, sqlite, etc.)
FROM python:3.12-slim-bookworm AS base

WORKDIR /app

# Mise à jour des paquets système critiques (libxml2, libxslt, xz, OpenSSL)
# + Mise à jour de zlib, SQLite, PAM, OpenLDAP, Perl, ncurses, toolchain (libstdc++/libgomp)
#   pour corriger les CVE signalés par Trivy.
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
      libxml2 \
      libxslt1.1 \
      xz-utils \
      libssl3 \
      zlib1g \
      libsqlite3-0 \
      libpam0g \
      libpam-runtime \
      libpam-modules \
      libpam-modules-bin \
      libldap-2.5-0 \
      perl \
      perl-base \
      perl-modules-5.36 \
      libperl5.36 \
      ncurses-base \
      ncurses-bin \
      libtinfo6 \
      libncursesw6 \
      libstdc++6 \
      libgomp1 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Mise à jour de pip et outils build
# (Python 3.12 gère nativement la sécurité des archives via PEP 706)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Installation des dépendances Python (on ignore les warnings de version Python si besoin)
RUN pip install --no-cache-dir -r requirements.txt --ignore-requires-python

# Image exécution
FROM python:3.12-slim-bookworm

# Variables d'env Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances système requises à l'exécution
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    gettext \
    curl \
    ca-certificates \
    libexpat1 \
    && apt-get install -y --only-upgrade \
    zlib1g \
    libsqlite3-0 \
    libpam0g \
    libpam-runtime \
    libpam-modules \
    libpam-modules-bin \
    libldap-2.5-0 \
    libpq5 \
    perl \
    perl-base \
    perl-modules-5.36 \
    libperl5.36 \
    ncurses-base \
    ncurses-bin \
    libtinfo6 \
    libncursesw6 \
    libssl3 \
    libstdc++6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos '' appuser \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

# Copie des packages Python installés depuis l'étape de build
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copie du code de l’application (propriétaire appuser)
COPY --chown=appuser:appuser . .
RUN chmod +x /app/entrypoint.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s \
  CMD curl -f http://localhost:${PORT:-8000}/health/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 aura_app.wsgi:application"]