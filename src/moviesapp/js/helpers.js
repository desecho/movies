/* global retinajs:false */

'use strict';

import {loadProgressBar} from 'axios-progress-bar';
import axios from 'axios';

export function retina(event) {
  const el = $(event.target);
  if (el.data('rjs-processed-2')) {
    return;
  }
  el.removeAttr('data-rjs-processed');
  // We need to remove height because retinajs apparently adds height attribute and it can't fix the
  // image after that
  el.removeAttr('height');
  el.attr('data-rjs-processed-2', true);
  retinajs();
}

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

export function saveRecordsOrder() {
  function getSortData() {
    const data = [];
    vm.records.forEach((record, index) => {
      const sortData = {'id': record.id, 'order': index + 1};
      data.push(sortData);
    });
    return data;
  }

  function success() {
    vm.recordsOriginal = vm.records;
  }

  function fail() {
    vm.records = vm.recordsOriginal;
    vm.$toast.error(gettext('Error saving movie order'));
  }

  const vm = this; // eslint-disable-line no-invalid-this
  axios.put(vm.urls.saveRecordsOrder, {'records': getSortData()}).then(success).catch(fail);
}

export function openUrl(url) {
  location.href = url;
}
