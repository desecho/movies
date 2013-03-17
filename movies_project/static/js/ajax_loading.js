$("#loading").ajaxStart(function(){
    $(this).show();
});

$("#loading").ajaxStop(function(){
    $(this).hide();
});