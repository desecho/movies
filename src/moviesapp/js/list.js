'use strict';

import axios from 'axios';
import {getSrcSet, initAxios} from './helpers';
import {newApp} from './app';
import {listWatchedId, listToWatchId} from './constants';

const starSizeNormal = 35;
const starSizeMinimal = 15;

newApp({
  data() {
    const vars = window.vars;
    return {
      urls: window.urls,
      records: vars.records,
      recordsOriginal: vars.records,
      mode: vars.mode,
      sort: vars.sort,
      listId: vars.listId,
      listName: vars.listName,
      isAnothersAccount: vars.isAnothersAccount,
      recommendations: vars.recommendations,
      listWatchedId: listWatchedId,
      listToWatchId: listToWatchId,
      sortByDate: false,
    };
  },
  computed: {
    isSortable() {
      const vm = this;

      return (vm.listId == vm.listToWatchId &&
        !vm.isAnothersAccount &&
        vm.sort == 'custom' &&
        (vm.mode == 'minimal' || vm.mode == 'gallery'));
    },
    starSize() {
      const vm = this;

      if (vm.mode == 'minimal') {
        return starSizeMinimal;
      } else {
        return starSizeNormal;
      }
    },
  },
  methods: {
    isRatingVisible(rating) {
      const vm = this;
      if (vm.isAnothersAccount && rating === 0) {
        return false;
      }

      return true;
    },
    applySettings(settings, reload = true) {
      const vm = this;
      const data = {
        settings: settings,
      };

      axios.put(vm.urls.saveSettings, data).then(function() {
        if (reload) {
          location.reload();
        }
      }).catch(function() {
        vm.$toast.error(gettext('Error applying the settings'));
      });
    },
    saveRecordsOrder() {
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
    },
    openUrl(url) {
      location.href = url;
    },
    getSrcSet: getSrcSet,
    changeRating(record, rating) {
      function success() {
        record.ratingOriginal = record.rating;
      }

      function fail() {
        record.rating = record.ratingOriginal;
        vm.$toast.error(gettext('Error saving the rating'));
      }

      const vm = this;
      const url = vm.urls.changeRating + record.id + '/';
      axios.put(url, {rating: rating}).then(success).catch(fail);
    },
    saveOptions(record, field) {
      function fail() {
        record.options[field] = !record.options[field];
        vm.$toast.error(gettext('Error saving options'));
      }

      const vm = this;
      const data = {
        options: record.options,
      };

      axios.put(vm.urls.record + record.id + '/options/', data).then(function() {}).catch(fail);
    },
    switchMode(newMode) {
      const vm = this;

      if (newMode == vm.mode) {
        return;
      }
      vm.applySettings({
        mode: newMode,
      }, false);
      vm.mode = newMode;
    },
    toggleRecommendation() {
      const vm = this;
      const newRecommendationSetting = !vm.recommendations;
      vm.recommendations = newRecommendationSetting;
      const settings = {
        recommendations: newRecommendationSetting,
      };
      if (newRecommendationSetting) {
        vm.sort = 'rating';
        const sortSettings = {};
        sortSettings[vm.listName] = 'rating';
        settings.sort = sortSettings;
      }
      this.applySettings(settings);
    },
    switchSort(newSort) {
      const vm = this;
      if (vm.sort == newSort) {
        return;
      }
      vm.sort = newSort;
      const sortSettings = {};
      sortSettings[vm.listName] = newSort;
      const settings = {
        sort: sortSettings,
      };
      if (newSort !== 'rating') {
        // disable recommendations if sorting by rating is manually disabled
        settings.recommendations = false;
        vm.recommendations = false;
      }
      vm.applySettings(settings);
    },
    removeRecord(record, index) {
      function success() {
        vm.records.splice(index, 1);
      }

      function fail() {
        vm.$toast.error(gettext('Error removing the movie'));
      }

      const vm = this;
      const url = vm.urls.removeRecord + record.id + '/';
      axios.delete(url).then(success).catch(fail);
    },
    addToList(movieId, listId, record) {
      const vm = this;
      const url = vm.urls.addToList + movieId + '/';
      axios.post(url, {
        listId: listId,
      }).then(function() {
        record.listId = listId;
      }).catch(function() {
        vm.$toast.error(gettext('Error adding the movie to the list'));
      });
    },
    showCommentArea(record) {
      record.commentArea = true;
    },
    saveComment(record) {
      const vm = this;
      const data = {
        comment: record.comment,
      };
      axios.put(vm.urls.saveComment + record.id + '/', data).then(function() {
        if (record.comment == '') {
          record.commentArea = false;
        }
      }).catch(function() {
        vm.$toast.error(gettext('Error saving a comment'));
      });
    },
    moveToTop(record, index) {
      const vm = this;
      vm.records.splice(index, 1);
      vm.records.unshift(record);
      vm.saveRecordsOrder();
    },
    moveToBottom(record, index) {
      const vm = this;
      vm.records.splice(index, 1);
      vm.records.push(record);
      vm.saveRecordsOrder();
    },
  },
  mounted() {
    this.records.forEach((record) => {
      record.ratingOriginal = record.rating;
    });
    initAxios(this);
  },
}).mount('#app');
