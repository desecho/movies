<template>
  <v-footer class="full-width-footer">
    <div class="footer-content">
      <div class="footer-left">
        <div class="powered-by">
          Powered by
          <a href="https://www.themoviedb.org" target="_blank">
            <span class="powered-by-tmdb"></span>
          </a>
        </div>
      </div>
      <div class="footer-right">
        <div class="footer-links">
          <router-link to="/about">About Movies</router-link>
        </div>
        <div class="footer-copyright">© 2013 - {{ new Date().getFullYear() }} {{ email }}. All rights reserved.</div>
      </div>
    </div>
  </v-footer>
</template>

<script lang="ts" setup>
import { ADMIN_EMAIL } from "../const";

const email = ADMIN_EMAIL;
</script>

<style scoped>
.full-width-footer {
  background: var(--background-secondary, #f8f9fa) !important;
  color: var(--text-secondary, #6b7280) !important;
  border-top: 1px solid var(--border-color, rgba(0, 0, 0, 0.05));
  transition: all 0.3s ease;
  width: 100% !important;
  position: relative;
  bottom: 0;
  left: 0;
  right: 0;
  margin: 0 !important;
  padding: 24px 0 !important;
  margin-top: auto !important;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 0 80px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  flex-wrap: wrap;
  gap: 16px;
}

.footer-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.footer-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  text-align: right;
}

.powered-by {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}

.footer-links {
  margin-bottom: 4px;
}

.footer-copyright {
  font-size: 0.85rem;
  opacity: 0.8;
}

.footer-content a {
  color: var(--text-primary, #1f2937) !important;
  text-decoration: none;
  transition: color 0.3s ease;
  font-weight: 500;
}

.footer-content a:hover {
  color: #667eea !important;
}

.powered-by-tmdb {
  background: url("/img/tmdb.svg");
  background-repeat: no-repeat;
  width: 70px;
  height: 40px;
  display: inline-block;
  background-size: contain;
  filter: var(--tmdb-filter, none);
  transition: filter 0.3s ease;
}

/* Dark mode specific styles */
:global(.dark-theme) .full-width-footer {
  background: var(--background-secondary) !important;
  color: var(--text-secondary) !important;
  border-top-color: var(--border-color) !important;
}

:global(.dark-theme) .footer-content a {
  color: var(--text-primary) !important;
}

:global(.dark-theme) .powered-by-tmdb {
  filter: brightness(0.8) contrast(1.2);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    text-align: center;
    gap: 12px;
    padding: 0 16px;
  }

  .footer-left,
  .footer-right {
    width: 100%;
    justify-content: center;
    align-items: center;
    text-align: center;
  }

  .footer-right {
    align-items: center;
  }

  .powered-by {
    justify-content: center;
  }

  .powered-by-tmdb {
    width: 60px;
    height: 35px;
  }
}

@media (max-width: 480px) {
  .full-width-footer {
    padding: 20px 0 !important;
  }

  .footer-content {
    padding: 0 12px;
  }

  .powered-by {
    font-size: 0.8rem;
  }

  .footer-copyright {
    font-size: 0.8rem;
  }

  .powered-by-tmdb {
    width: 55px;
    height: 30px;
  }
}
</style>
