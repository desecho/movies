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

$(function(){
  if (isVkApp) {
    $('.vk-app-show').show();
  } else {
    $('.vk-app-hide').show();
  }
})