// function initVk() {
//   return VK.callMethod('resizeWindow', 807, $('body').height() + 80);
// };

// setInterval('initVk()', 200);

function inIframe() {
  try {
    return window.self !== window.top;
  } catch (e) {
    return true;
  }
}

const isVkApp = inIframe();
  if (!isVkApp) {
    $('.vk-app').hide();
  }

$(function(){
  if (isVkApp) {
    $('.vk-app').show();
  }
})