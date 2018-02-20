/* global retinajs:false */

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
