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
