## MovieMunch Features

A concise guide to everything the site does and how to use it. This document focuses on user-facing functionality with light notes about how each feature works under the hood.

### Core Concepts

- **Two personal lists**: `Watched` and `To‑Watch` for every user
- **Search and discovery**: Search, Trending, and AI Recommendations
- **Organization tools**: Sorting, filtering, view modes, pagination, and custom drag‑and‑drop order
- **Social**: Public profile pages and a user directory (with privacy controls)
- **Streaming availability**: See where a movie is available to stream (by country)

---

## Authentication and Accounts

- **Sign up / Login / Logout**
  - Pages: `/register`, `/login`, `/logout`
  - Backend: JWT auth (`/token/`, `/token/refresh/`), registration/password flows via `rest_registration` under `/user/`
  - Frontend auto‑refreshes access tokens when they near expiration

- **Email availability check**
  - Used during registration to validate email availability
  - API: `POST /user/check-email-availability/` → boolean

- **Password flows**
  - Verify user: `/verify-user` (links sent via email)
  - Reset password: `/reset-password-request`, `/reset-password`
  - Change password: `/change-password` (logged‑in only)

- **User preferences**
  - Page: `/preferences` (logged‑in only)
  - Fields: `hidden` (privacy), `country` (for streaming availability)
  - API: `GET/PUT /user/preferences/`

- **Avatar**
  - Upload/remove your profile avatar (drag‑and‑drop upload, preview)
  - API: `GET/POST/DELETE /user/avatar/`

---

## Search and Discovery

- **Search**
  - Page: `/search`
  - Search by: movie title, actor, director
  - Options: sort by date, popular‑only filter
  - Logged‑in users won’t see movies they already have in their lists
  - API: `GET /search/?query=...&type=movie|actor|director&options={...}` (capped at 50 results)

- **Trending**
  - Page: `/trending`
  - Curated by TMDB; logged‑in users won’t see movies already on their lists
  - API: `GET /trending/`

- **AI Recommendations**
  - Page: `/recommendations` (logged‑in only)
  - Personalizes suggestions from your `Watched` ratings and optional filters:
    - `preferredGenre`, `yearStart`–`yearEnd`, `minRating` (0–5), `recommendationsNumber`
  - API: `GET /recommendations/` (uses OpenAI + TMDB to return movie cards)

---

## Personal Lists (Watched / To‑Watch)

- **Pages**
  - Your lists: `/list/watched`, `/list/to-watch`
  - Another user’s lists: `/users/:username/list/watched`, `/users/:username/list/to-watch`

- **Add and remove**
  - From search results: add directly to a list
  - If a movie isn’t in the database yet, it is fetched from TMDB and added automatically
  - Remove any record from your lists
  - APIs:
    - `POST /add-to-list/<movie_id>/` (movie already in DB)
    - `POST /add-to-list-from-db/` with `tmdbId` (auto‑add to DB if needed)
    - `DELETE /remove-record/<record_id>/`

- **Rating and comments**
  - Rate 0–5 stars for `Watched`
  - Add and edit a short comment
  - APIs: `PUT /change-rating/<record_id>/`, `PUT /save-comment/<record_id>/`

- **Viewing options (per movie)**
  - Mark options such as: Original cut, Extended, In theatre, HD / Full HD / 4K, Ignore rewatch
  - API: `PUT /record/<record_id>/options/`

- **Sorting and custom order**
  - Sort by: Addition date, Release date, Rating, or Custom
  - In Custom mode, drag cards to reorder; save persists your custom order
  - API: `PUT /save-records-order/`

- **Filtering and searching within a list**
  - Text search across title/director/actors
  - Filters:
    - To‑watch: Hide unreleased, Only recent releases (last 6 months)
    - Watched: To rewatch
      - Shows 5‑star movies that are good candidates to re‑experience under better/different conditions
      - Applied only on the `Watched` list
      - Inclusion logic (all client‑side):
        - Must have user rating = 5
        - Must NOT be marked "Ignore rewatch"
        - And one of the following is true:
          - Watched not in Ultra HD and not in Theatre; or
          - Watched not in the Original version
      - Based on per‑movie Viewing options: Original, Extended, In theatre, HD/Full HD/Ultra HD, Ignore rewatch
      - Toggling these options or changing rating updates whether the movie appears in this filter

- **View modes**
  - Full, Minimal, Compact, Gallery (poster grid)
  - Preferences (mode/sort/query/filters) are persisted locally; page resets on changes

- **Pagination**
  - 50 items per page, both in table and gallery

- **Streaming availability**
  - Shows where a movie can be streamed in your selected country (if supported and movie is released)
  - Providers include logos and link out to TMDB’s “Where to Watch” page
  - Countries supported: US, CA, RU

---

## Users and Profiles

- **User directory**
  - Page: `/users`
  - Browsable list of public users with avatars
  - API: `GET /users/`

- **Profile pages**
  - Public list pages under `/users/:username/...`
  - If a user sets `hidden = true`, they won’t appear in the directory and their lists aren’t accessible

---

## Stats and Insights

- **Page**: `/stats` (logged‑in only)
- **Metrics**
  - Totals: Watched, To‑watch
  - Time watched (sum of runtimes)
  - Ratings: Average rating and count of rated movies
  - Preferences: Counts for Theatre, HD, Full HD, 4K, Extended, Original
  - Top 5: Genres, Directors, Actors
  - Trends: Monthly watch counts (last 12 months) and rating distribution
- **API**: `GET /stats/`

---

## Theme and UX

- **Dark mode**
  - One‑click toggle in the sidebar/top bar; integrated with Vuetify and custom CSS variables
- **Responsive layout**
  - Mobile‑first UI using Vue 3 + Vuetify 3

---

## Data Sources and Freshness

- **TMDB**: Posters, trending, search results, titles, release dates, trailers
- **OMDb**: IMDb rating refresh via scheduled commands
- **OpenAI**: AI Recommendations (returns IMDb IDs which are resolved to TMDB data)
- **Freshness**
  - When a movie is added and already released, background jobs fetch streaming availability
  - Admin/cron commands keep watch providers and IMDb ratings up to date

---

## Key API Endpoints (reference)

```
/token/                      – Obtain JWT (POST)
/token/refresh/              – Refresh JWT (POST)

/user/                       – Auth & account endpoints (rest_registration)
/user/preferences/           – Load/Save user preferences (GET/PUT)
/user/avatar/                – Get/Upload/Delete avatar (GET/POST/DELETE)
/user/check-email-availability/ – Check if email is available (POST)

/users/                      – List public users (GET)
/users/<username>/avatar/    – Get a user’s avatar (GET)

/search/                     – Search movies (GET)
/trending/                   – Trending movies (GET)
/recommendations/            – AI recommendations (GET, auth required)
/stats/                      – User stats (GET, auth required)

/records/                    – Current user’s records (GET)
/users/<username>/records/   – Another user’s records (GET)
/add-to-list/<movie_id>/     – Add existing DB movie to list (POST)
/add-to-list-from-db/        – Add by TMDB ID (POST)
/remove-record/<record_id>/  – Remove from list (DELETE)
/record/<record_id>/options/ – Save per‑movie options (PUT)
/change-rating/<record_id>/  – Set rating (PUT)
/save-comment/<record_id>/   – Save comment (PUT)
/save-records-order/         – Save custom order for list (PUT)
```

---

## Notes and Limits

- Max search results per request: 50
- Token auto‑refresh occurs when <30 minutes remain before expiry
- Streaming availability shown only for supported countries (US, CA, RU) and released movies

---

## Getting Started (quick user path)

1) Create an account and log in
2) Set your country and upload an avatar in `/preferences`
3) Use `/search` and `/trending` to add movies to `To‑Watch` or `Watched`
4) Rate and comment on `Watched` items; toggle viewing options as needed
5) Organize via filters, sorting, view modes, and drag‑and‑drop custom order
6) Explore `/recommendations` and `/stats`
7) Share your profile lists if your account isn’t hidden: `/users/<your-username>/list/to-watch`
