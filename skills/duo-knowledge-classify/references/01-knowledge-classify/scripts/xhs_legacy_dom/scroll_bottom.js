(function(){
  var el=document.scrollingElement||document.documentElement;
  el.scrollTop=el.scrollHeight;
  window.scrollTo(0, document.body.scrollHeight);
  return el.scrollTop;
})()
