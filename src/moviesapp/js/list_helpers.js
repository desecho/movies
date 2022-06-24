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

  const vm = this; // eslint-disable-line no-invalid-this
  axios.put(urls.saveRecordsOrder, {'records': getSortData()}).then(function() {
    vm.recordsOriginal = vm.records;
  }).catch(
      function() {
        vm.records = vm.recordsOriginal;
        vm.$toast.error(gettext('Error saving movie order'));
      });
}
