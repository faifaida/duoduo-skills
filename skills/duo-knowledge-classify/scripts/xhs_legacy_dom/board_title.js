(function(){
  var t = (document.title||'').replace(/\s*[-\u2013\u2014]\s*小红书.*$/,'');
  var cnt = null;
  var m = (document.body?document.body.innerText:'').match(/笔记・\s*(\d+)/);
  if (m) cnt = m[1];
  var h = document.querySelector('.board-info') || document.querySelector('.header') || document.querySelector('.title');
  var htxt = h ? h.innerText.replace(/\s+/g,' ').slice(0,40) : null;
  return JSON.stringify({name:t, count:cnt, header:htxt});
})()
