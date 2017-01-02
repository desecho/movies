function initVk() {
  return VK.callMethod('resizeWindow', 807, $('body').height() + 80);
};

setInterval('initVk()', 200);
