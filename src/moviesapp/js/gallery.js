'use strict';

import {newApp} from './app';
import {retina, getSrcSet} from './helpers';
import {saveRecordsOrder} from './list_helpers';
import {listWatchedId, listToWatchId} from './constants';

window.vm = newApp({
  data() {
    return {
      records: vars.records,
      recordsOriginal: vars.records,
      listWatchedId: listWatchedId,
      listToWatchId: listToWatchId,
      listId: vars.listId,
      urls: urls,
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
    openUrl(url) {
      location.href = url;
    },
    saveRecordsOrder: saveRecordsOrder,
    getSrcSet: getSrcSet,
    retinajs: retina,
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
});

window.vm.mount('#app');
