'use strict';

import {loadProgressBar} from 'axios-progress-bar';
import axios from 'axios';

function setAxiosSettings() {
  loadProgressBar();
  const headers = {
    'X-CSRFToken': vm.$cookies.get('csrftoken'),
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
  };
  axios.defaults.headers.common = headers;
  axios.interceptors.response.use(null, function(error) {
    if (error.response.status === 403) {
      vm.$toast.info(
          gettext('You need to login to add a movie to your list'));
      return new Promise(() => {});
    }
    return Promise.reject(error);
  });
}

if (window.vm) {
  setAxiosSettings();
}
