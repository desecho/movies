<template>
  <v-container>
    <v-row>
      <v-col cols="9">
        <p>Create movie lists "Watched" and "To Watch", rate movies, and add comments.</p>
        <br />
        <h3>Features</h3>
        <ul>
          <li>Search for movies by title, actor, or director</li>
          <li>Get a list of currently trending movies</li>
          <li>AI-powered recommendations</li>
          <li>Stats</li>
          <li>Add custom order for the "To Watch" list</li>
          <li>Share your lists online</li>
          <li>See where you can stream a movie</li>
          <li>Privacy settings.</li>
          <li>Dark mode</li>
          <li>
            Add additional information such as if you watched a movie in the original version, in a theatre, an
            extended version, in 4K, etc.
          </li>
        </ul>
        <br />
        <h3>Tips</h3>
        <ul>
          <li>You can see the original title when you hover over the movie title</li>
          <li>You can only add custom order in the minimal mode and on the gallery page</li>
          <li>
            The best user experience to reorder movies is available on the gallery page for the "To Watch" list. On the
            gallery page, additional functionality is available to move a movie to the top or bottom of the list.
          </li>
          <li>To be able to see where you can stream a movie, you need to set your country in preferences</li>
        </ul>
        <br />
        <h3>Streaming data</h3>
        <p>
          Streaming data is currently only available in Canada, the United States are supported. You can
          <a href="mailto:{{ ADMIN_EMAIL }}">email me</a> to request support for your country.
        </p>
        <br />
        <h3>Rating system</h3>
        <ul>
          <li>1 — Awful</li>
          <li>2 — Bad</li>
          <li>3 — Ok</li>
          <li>4 — Good</li>
          <li>5 — Excellent</li>
        </ul>
        <br />
        <h3>APIs used</h3>
        <ul>
          <li>
            <a href="https://www.themoviedb.org/" target="_blank">TMDB</a>
          </li>
          <li>
            <a href="https://www.omdbapi.com/" target="_blank">OMDb</a>
          </li>
        </ul>
        <br />
        <h3>Import/Export data</h3>
        <p>
          If you would like to import or export data, please
          <a :href="`mailto:${email}`">email me</a>.
        </p>
        <br />
        <h3>Source code</h3>
        <p>
          The source code is available
          <a href="https://github.com/desecho/movies" target="_blank">on GitHub</a>.
        </p>
        <br />
        <h3>Contact info</h3>
        <p>
          If you have problems with account activation or other issues, questions or feedback please
          <a :href="`mailto:${email}`">email me</a>.
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import { ADMIN_EMAIL } from "../const";

const email = ADMIN_EMAIL;
</script>
