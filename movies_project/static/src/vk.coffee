#VK.init(function() {});
init_vk = ->
    VK.callMethod('resizeWindow', 807, $('body').height() + 80);
setInterval('init_vk()', 200);