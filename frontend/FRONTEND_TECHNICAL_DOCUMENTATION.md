## Frontend Technical Documentation

This document describes the architecture, tooling, and conventions used in the frontend application.

### Stack
- **Framework**: Vue 3 (Composition API, Single File Components)
- **Build tool**: Vite 6
- **Language**: TypeScript 5
- **UI**: Vuetify 3
- **State**: Pinia 3 (+ `pinia-plugin-persist`)
- **Routing**: vue-router 4
- **HTTP**: axios (+ global interceptors, progress bar)
- **Analytics**: vue-gtag (Google Analytics 4)
- **Notifications**: vue-toast-notification
- **Utilities**: lodash, jwt-decode, v-lazy-image, vuedraggable, vue3-pagination

### Directory structure
- `src/main.ts`: App bootstrap (Pinia, Router, Vuetify, GA, fonts, axios progress bar)
- `src/App.vue`: Root layout, global error boundary, theme init
- `src/router.ts`: Route table and navigation guards
- `src/axios.ts`: Axios defaults and interceptors (auth refresh, logging, network/timeouts)
- `src/plugins/`: Vuetify and WebFontLoader setup
- `src/stores/`: Pinia stores (`auth`, `theme`, `records`, `listView`, `feed`)
- `src/composables/`: Reusable logic (filtering, sorting, pagination, async ops, request dedup, etc.)
- `src/services/`: Service layer (`listViewService`, `shareService`)
- `src/utils/`: Cross-cutting utils (`errorHandling`, `movieUtils`)
- `src/views/` and `src/components/`: Pages and UI components
- `src/styles/`: Global SCSS
- `src/types*/`: Type declarations

### Application lifecycle
1. `main.ts`
   - Loads web fonts via `webfontloader`
   - Enables `x-axios-progress-bar`
   - Creates Pinia (installs `pinia-plugin-persist`)
   - Configures GA via `vue-gtag` with router-based page tracking
   - Mounts Vue app with Vuetify, Router, Pinia
   - Calls `initAxios()` after app creation so auth store is available
2. `App.vue`
   - Sets up `MenuComponent`, `FooterComponent`, and wraps `RouterView` with `ErrorBoundary`
   - On mount: initializes theme (`themeStore.initVuetifyTheme()` + `initTheme()`) and, if logged in, initializes axios and loads avatar

### Routing (`src/router.ts`)
- History: `createWebHistory()`; active class: `active`
- Routes include: `/`, `/search`, `/about`, `/feed`, `/trending`, `/recommendations`, `/stats`, `/network`, lists (`/list/watched`, `/list/to-watch`), user lists (`/users/:username/...`), auth flows, and settings
- Private pages: `['/preferences','/change-password','/stats','/network']`
- Guard behavior:
  - Redirects guests on private pages to `/login`
  - Validates/refreshes JWT on navigation when logged in (refresh if expiring within 30 minutes)
  - If token invalid during a "logged in" state, redirects to `/login`
- Query-to-props helpers (e.g., `authProps`) parse numeric/string query values safely

### State management (Pinia)
- `stores/auth.ts`
  - Persists under localStorage key `user`
  - Actions: `login`, `refreshToken`, `uploadAvatar`, `deleteAvatar`, `loadAvatar`, `logout`
  - On successful auth or refresh, calls `initAxios()` to update headers/interceptors
- `stores/theme.ts`
  - Syncs a dark/light theme both via document class (`dark-theme`/`light-theme`) and Vuetify theme (`useTheme()`)
  - Persists preference in localStorage; respects system preference if none saved
- `stores/records.ts`
  - Loads records for current user or a given `username`; manages loading flags and context switching
  - Normalizes IMDb rating to 0–5 half-star scale and stores original rating
- `stores/listView.ts`
  - Holds view mode, sort, search query, filters, and page
  - Provides TTL caches (5 min) for filtered/sorted arrays and manual localStorage persistence (excluding page)
- `stores/feed.ts`
  - Loads activity feed with pagination; caches follow status per user; exposes follow/unfollow/toggle

### Service layer
- `services/listViewService.ts`
  - DI-based service that composes composables for filtering, sorting, and pagination
  - Exposes derived record lists, counts, pagination info, navigation guards; supports config (itemsPerPage, caching flags)
- `services/shareService.ts`
  - `generateShareUrl(recordId, platform)` makes `POST /share/{id}/` and returns `share_url`
  - `openShareWindow(url)` opens a popup sized for social sharing

### Composables
- `useListViewFiltering(records, currentListId, searchQuery, filters)`
  - Validates records, applies: list filter, text search, rewatch (watched only), unreleased hide, recent releases (to-watch only)
- `useListViewSorting(filteredRecords, sortType, currentListId)`
  - Sorts by addition date (default), release date, rating (user vs IMDb), or custom order
- `useListViewPagination(sortedRecords, currentPage, itemsPerPage=50)`
  - Memoized paginated slice, total pages, and navigation flags; cache invalidation helper
- `useRecordsData()`
  - Loads records/my records/user avatar with request deduplication; parallel `loadAllData`
- `useRecordFilters(records, currentListId)`
  - Debounced search and pure filtering utilities with counts for watched/to-watch
- `useRequestDeduplication()`
  - Prevents concurrent duplicate requests with a per-key Promise cache
- `useAsyncOperation()` (+ `useApiCall`, `useNetworkRequest`, `useAuthenticatedRequest`, `useSilentRequest`)
  - Standardized async flow: loading flags, retries, error handling via `utils/errorHandling`
- `mobile.ts`
  - Vuetify breakpoint helpers for `isPhone`, `isTablet`, `isMobile`

### HTTP and axios (`src/axios.ts`)
- Defaults: JSON headers; adds `Authorization: Bearer <accessToken>` if present and valid
- Request interceptor: logs (DEV), attaches metadata for timing
- Response interceptor:
  - Logs (DEV) with duration
  - 401 handling: detects token errors, queues requests while refresh is in progress, refreshes via `auth.refreshToken()`, retries original request; on refresh failure logs out and redirects to `/login`
  - Network/timeout errors routed through `utils/errorHandling`
- Interceptors are ejected/re-registered on `initAxios()` to avoid leaks/stale closures

### Error handling (`src/utils/errorHandling.ts`)
- Defines `AppError`, `ErrorType`, `ErrorSeverity` and helpers to classify errors
- Central `handleError()` shows toasts (severity-based), logs, and optionally reports
- Specialized handlers (`authentication`, `network`, `api`, `validation`, `silent`) and `handleCriticalError()` for ErrorBoundaries
- Toasts are powered by `vue-toast-notification` with default position bottom-right

### Theming and styles
- Vuetify themes defined in `plugins/vuetify.ts` (custom color palettes for light/dark)
- Global CSS variables and dark overrides in `App.vue`
- Additional SCSS utilities in `styles/`
- Theme preference is applied both to document classes and Vuetify theme

### Environment and configuration
- Env variables (read at build time via `import.meta.env`):
  - `VITE_BACKEND_URL`: API base URL (used by `helpers.getUrl()`)
  - `VITE_GOOGLE_ANALYTICS_ID`: GA4 tag ID for `vue-gtag`
  - `VITE_ADMIN_EMAIL`: Displayed in the UI where relevant
- Docker build passes these via `ARG` and runs `yarn build`

### Build, run, and deploy
- Package scripts:
  - `yarn dev`: Vite dev server
  - `yarn build`: Production build to `dist/`
  - `yarn preview` / `yarn serve`: Preview built app
- Docker:
  - Multi-stage: Node builder → Nginx static server
  - Nginx serves `dist/` with SPA fallback (`try_files ... /index.html`)

### Conventions and linting
- ESLint Flat config with Vue + TypeScript plugins, Prettier integration
- Strict TypeScript rules and import ordering
- Prefer Composition API with explicit function return types on exported API
- Avoid deep nesting; use early returns and composables/services for separation of concerns

### Adding features (guidelines)
- New page/view: create under `src/views/`, add route in `src/router.ts`
- API access: prefer centralizing cross-cutting behavior in axios interceptors; use `useAsyncOperation` for retries/errors
- Complex UI logic: extract to composables and/or a service class for testability
- State: use Pinia stores for shared state; persist only what is necessary
- Performance: use request deduplication, TTL caches, and memoized computations from composables

### Key constants and types
- List IDs: `listWatchedId = 1`, `listToWatchId = 2` (`src/const.ts`)
- Shared types such as `RecordType`, `Movie`, etc. in `src/types.ts`
- ListView types (`ViewMode`, `SortType`, filters) in `src/types/listView.ts`

### Troubleshooting
- If authenticated but redirected to `/login`: access token invalid/expired and refresh failed; check network and `VITE_BACKEND_URL`
- CORS or network issues: confirm backend URL and Nginx config; see axios network error handling
- Theme not switching: ensure `themeStore.initVuetifyTheme()` is called early (see `App.vue`) and `localStorage['theme']` state
