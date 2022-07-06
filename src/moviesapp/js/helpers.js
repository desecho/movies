'use strict';

import {loadProgressBar} from 'axios-progress-bar';
import axios from 'axios';

export function param(params) {
  const paramsOutput = new URLSearchParams();
  for (const key in params) {
    if (Object.prototype.hasOwnProperty.call(params, key)) {
      paramsOutput.append(key, params[key]);
    }
  }
  return paramsOutput;
}

export function removeItemOnce(arr, value) {
  const index = arr.indexOf(value);
  if (index > -1) {
    arr.splice(index, 1);
  }
  return arr;
}

export function getSrcSet(img1x, img2x) {
  return `${img1x} 1x, ${img2x} 2x`;
}

export function initAxios(vm) {
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
