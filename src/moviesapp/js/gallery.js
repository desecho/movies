'use strict';

import {newApp} from './app';
import {getSrcSet, saveRecordsOrder, openUrl, initAxios} from './helpers';
import {listWatchedId, listToWatchId} from './constants';

newApp({
  data() {
    const vars = window.vars;
    return {
      records: vars.records,
      recordsOriginal: vars.records,
      listWatchedId: listWatchedId,
      listToWatchId: listToWatchId,
      listId: vars.listId,
      urls: window.urls,
      isAnothersAccount: vars.isAnothersAccount,
    };
  },
  computed: {
    isSortable() {
      const vm = this;

      return vm.listId == vm.listToWatchId && !vm.isAnothersAccount;
    },
  },
  methods: {
    openUrl: openUrl,
    saveRecordsOrder: saveRecordsOrder,
    getSrcSet: getSrcSet,
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
    initAxios(this);
  },
}).mount('#app');
