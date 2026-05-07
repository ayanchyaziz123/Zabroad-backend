# Zabroad Backend

REST API for **Zabroad** — a community platform for immigrants to find jobs, housing, legal help, healthcare, events, and connect with people from their home country.

Built with Django 5 + Django REST Framework. Deployable to Railway (primary) or Render.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5, Django REST Framework |
| Auth | SimpleJWT (access + refresh tokens, blacklist) |
| Database | PostgreSQL (production), SQLite (local dev) |
| AI | Anthropic Claude (Haiku) via `anthropic` SDK |
| Media Storage | Cloudflare R2 / AWS S3 via django-storages |
| Static Files | WhiteNoise (compressed + cached) |
| Server | Gunicorn |
| Deployment | Railway (nixpacks) |

---

## Project Structure

```
zabroad_backend/
├── accounts/          # Auth, OTP, user profiles
├── posts/             # Community feed, likes, comments, saves
├── jobs/              # Job listings + Stripe payments
├── housing/           # Housing listings + Stripe payments
├── marketplace/       # Buy/sell marketplace
├── healthcare/        # Doctor directory
├── attorneys/         # Immigration attorney directory + Stripe payments
├── events/            # Community events + RSVP
├── chat/              # Direct messaging
├── notifications/     # In-app notifications
├── ai/                # Claude AI immigration assistant
│   ├── views.py       # /api/ai/chat/ endpoint
│   └── urls.py
└── zabroad_backend/   # Settings, URLs, shared utilities
    ├── settings.py
    ├── urls.py
    ├── geo.py          # Shared GPS/city location sorting
    ├── permissions.py  # IsOwnerOrReadOnly, IsOwner
    └── exceptions.py   # Custom error handler
```

---

## API Endpoints

### Auth — `/api/auth/`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `health/` | None | Health check |
| POST | `otp/send/` | None | Send 6-digit OTP to email |
| POST | `otp/verify/` | None | Verify OTP code |
| POST | `register/` | None | Create account (requires verified OTP) |
| POST | `login/` | None | Email + password → JWT tokens |
| POST | `logout/` | None | Blacklist refresh token |
| POST | `token/refresh/` | None | Rotate refresh token |
| GET/PATCH | `me/` | Required | Get or update current user profile |
| POST | `change-password/` | Required | Change password |
| POST | `password/forgot/` | None | Send password-reset OTP |
| POST | `password/reset/` | None | Verify OTP + set new password |
| GET | `profile/<user_id>/` | Required | Get any user's public profile + posts |

### AI Assistant — `/api/ai/`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `chat/` | Required | Send message history → get Claude AI reply |

**Request body:**
```json
{
  "messages": [
    { "role": "user", "content": "Can I work on OPT while applying for H-1B?" },
    { "role": "assistant", "content": "Yes, here's how cap-gap works..." },
    { "role": "user", "content": "What documents do I need?" }
  ]
}
```

**Response:**
```json
{ "reply": "Here are the documents you need for H-1B..." }
```

The AI automatically receives the user's visa status, home country, and current city as system context so responses are personalized.

### Posts — `/api/posts/`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Optional | Feed (filterable by scope, topic, country, location, search) |
| POST | `/` | Required | Create post |
| GET | `<id>/` | Optional | Post detail |
| PATCH/DELETE | `<id>/` | Owner | Edit or delete post |
| POST | `<id>/like/` | Required | Toggle like |
| POST | `<id>/save/` | Required | Toggle save |
| GET | `<id>/comments/` | Optional | List comments |
| POST | `<id>/comments/` | Required | Add comment |
| GET | `saved/` | Required | Current user's saved posts |

**Feed query params:** `scope` (local/country/global), `topic`, `country`, `location`, `author`, `search`, `near_city`, `lat`, `lng`

### Jobs — `/api/jobs/`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Optional | List jobs (filterable) |
| POST | `/` | Required | Post a job |
| GET/PATCH/DELETE | `<id>/` | Owner | Job detail |
| POST | `payment-intent/` | Required | Stripe payment intent for plan upgrade |

### Housing — `/api/housing/`

Same pattern as Jobs. Filter by `category`, `home_country`, `near_city`, `lat`/`lng`.

### Marketplace — `/api/marketplace/`

Same pattern. Filter by `category`, `home_country`, `near_city`, `lat`/`lng`.

### Healthcare — `/api/doctors/`

Doctor directory. Filter by `specialty`, `language`, `accepts_medicaid`, `near_city`, `lat`/`lng`. Sorted by plan tier then proximity.

### Attorneys — `/api/attorneys/`

Attorney directory. Filter by `specialty`, `language`, `home_country`, `near_city`, `lat`/`lng`.

### Events — `/api/events/`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Optional | List upcoming events |
| POST | `/` | Required | Create event |
| GET/PATCH/DELETE | `<id>/` | Owner | Event detail |
| POST | `<id>/rsvp/` | Required | Toggle RSVP |

### Chat — `/api/chat/`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `conversations/` | Required | List user's conversations |
| POST | `conversations/` | Required | Start a conversation |
| GET | `conversations/<id>/messages/` | Required | Message history |
| POST | `conversations/<id>/messages/` | Required | Send a message |

### Notifications — `/api/notifications/`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Required | List notifications |
| POST | `<id>/read/` | Required | Mark as read |
| POST | `read-all/` | Required | Mark all as read |

---

## Data Models

### Profile (extends Django User)
```
handle, avatar_emoji, avatar, cover
home_country, country_flag, lives_in
visa_status (OPT/CPT/H1B/H4/L1/O1/GC/CITIZEN/F1/ASYLUM/OTHER)
bio
```

### Post
```
body (500 chars), scope (local/country/global), is_anonymous
image, location, latitude, longitude, country
topics (M2M via PostTopic)
```

### Listings (Jobs, Housing, Marketplace)
```
title, description, price, location, category
plan (free/standard/premium)
home_country, country_flag, latitude, longitude, image
is_active, is_hot / is_featured
```

---

## Authentication Flow

```
1. POST /api/auth/otp/send/      → OTP emailed (6-digit, 10-min expiry, max 5 attempts)
2. POST /api/auth/otp/verify/    → Mark OTP as verified
3. POST /api/auth/register/      → Create account (OTP must be verified within 15 min)
4. POST /api/auth/login/         → Returns { access, refresh, user }

Access token: 30 minutes
Refresh token: 7 days (rotated on use, blacklisted after rotation)
```

**Password reset:**
```
1. POST /api/auth/password/forgot/  → OTP emailed (if account exists)
2. POST /api/auth/password/reset/   → Verify OTP + set new password
```

---

## AI Assistant

The `/api/ai/chat/` endpoint proxies messages to Anthropic's Claude Haiku model.

**How it works:**
1. Frontend sends the full conversation history (array of `{role, content}` objects)
2. Backend injects a system prompt that defines Zabroad AI's persona and expertise
3. The authenticated user's profile (visa status, home country, city) is appended to the system prompt automatically — responses are personalized
4. Claude Haiku returns a reply which is forwarded to the app

**System prompt covers:**
- All US visa types (OPT, STEM OPT, H-1B, H-4, L-1, O-1, F-1, Green Card, Asylum, DACA)
- USCIS processes, form numbers, timelines, deadlines
- Job search for immigrants (E-Verify, cap-gap, OPT-friendly employers)
- Renting without US credit history or SSN
- Healthcare options (FQHCs, OPT insurance, telehealth, GoodRx)
- Banking, credit building, ITIN, taxes
- Finding immigration attorneys and legal aid

**Error handling:**
- `503` — API key not configured
- `429` — Claude rate limit hit, retry later

---

## Rate Limits

| Scope | Limit |
|-------|-------|
| Anonymous requests | 100 / hour |
| Authenticated requests | 1000 / hour |
| Login attempts | 5 / minute |
| OTP send | 3 / hour |
| OTP resend cooldown | 2 minutes between sends |

---

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
cd zabroad_backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY and ANTHROPIC_API_KEY at minimum

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start dev server
python manage.py runserver
```

The API will be available at `http://localhost:8000`.
Admin panel: `http://localhost:8000/admin/`
Browsable API: enabled in DEBUG mode.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DJANGO_SECRET_KEY` | Yes | Django secret key |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude AI — get at console.anthropic.com |
| `DEBUG` | No | `True` for dev, `False` for prod (default: False) |
| `DATABASE_URL` | No | Auto-injected by Railway/Render. Falls back to SQLite. |
| `ALLOWED_HOSTS` | No | Comma-separated hosts. Auto-detected on Railway/Render. |
| `CORS_ALLOWED_ORIGINS` | No | Comma-separated origins. Defaults to allow-all (dev only). |
| `EMAIL_BACKEND` | No | Django email backend class |
| `EMAIL_HOST` | No | SMTP host (default: smtp.gmail.com) |
| `EMAIL_PORT` | No | SMTP port (default: 587) |
| `EMAIL_USE_TLS` | No | (default: True) |
| `EMAIL_HOST_USER` | No | Gmail address for sending OTP emails |
| `EMAIL_HOST_PASSWORD` | No | Gmail app password (16-char, generated in Google Account settings) |
| `USE_S3` | No | Set `True` to enable R2/S3 media storage |
| `AWS_ACCESS_KEY_ID` | If USE_S3 | R2 or S3 access key |
| `AWS_SECRET_ACCESS_KEY` | If USE_S3 | R2 or S3 secret key |
| `AWS_STORAGE_BUCKET_NAME` | If USE_S3 | Bucket name |
| `AWS_S3_ENDPOINT_URL` | If R2 | `https://<account-id>.r2.cloudflarestorage.com` |
| `AWS_S3_CUSTOM_DOMAIN` | No | CDN domain for media URLs |
| `STRIPE_SECRET_KEY` | No | Stripe secret key (for plan upgrades) |
| `STRIPE_PUBLISHABLE_KEY` | No | Stripe publishable key |

---

## Deploying to Railway

1. Push the `zabroad_backend` folder to a GitHub repository.
2. Create a new Railway project → **Deploy from GitHub repo**.
3. Set **Root Directory** to `zabroad_backend`.
4. Add a **Postgres** plugin — Railway injects `DATABASE_URL` automatically.
5. Set environment variables in Railway dashboard (minimum: `DJANGO_SECRET_KEY`, `DEBUG=False`, `ANTHROPIC_API_KEY`, email config).
6. Railway uses `railway.toml` (already configured) — build and deploy happens automatically.

`RAILWAY_PUBLIC_DOMAIN` is auto-injected and added to `ALLOWED_HOSTS`.

Health check endpoint: `GET /api/auth/health/`

---

## Security

- OTP codes use `secrets.randbelow` (cryptographically secure)
- OTP comparison uses `hmac.compare_digest` (timing-attack safe)
- JWT refresh tokens are blacklisted after rotation
- Password reset uses the same OTP system — email enumeration protected (identical response whether account exists or not)
- AI endpoint requires authentication — no anonymous AI access
- Production security headers: HSTS, XSS filter, content-type nosniff, X-Frame-Options DENY
- TLS termination handled at Railway/Render load balancer via `SECURE_PROXY_SSL_HEADER`
- Per-endpoint throttling on login and OTP send

---

## License

Private — all rights reserved.
