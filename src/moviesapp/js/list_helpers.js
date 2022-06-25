'use strict';
import axios from 'axios';


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
