VK.init(function() {});
function init_vk() {
  VK.callMethod('resizeWindow', 807, $('body').height() + 80);
  VK.callMethod('scrollWindow', 0);
}
setInterval('init_vk()', 200);