'use strict';

import {newApp} from './app';
import {retina, getSrcSet} from './helpers';
import {sortRecords} from './list_helpers';

window.vm = newApp({
  data() {
    return {
      records: vars.records,
      recordsOriginal: vars.records,
      listWatchedId: vars.listWatchedId,
      listToWatchId: vars.listToWatchId,
      listId: vars.listId,
      urls: urls,
      isAnothersAccount: vars.isAnothersAccount,
    };
  },
  computed: {
    isDraggable() {
      const vm = this;
      return vm.listId == vm.listToWatchId && !vm.isAnothersAccount;
    },
  },
  methods: {
    openUrl(url) {
      location.href = url;
    },
    sortRecords: sortRecords,
    getSrcSet: getSrcSet,
    retinajs: retina,
  },
});

window.vm.mount('#app');
