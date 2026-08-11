(function(){
  var links = [].slice.call(document.querySelectorAll('a[href*="/board/"]'));
  var seen = {};
  var out = [];
  links.forEach(function(a){
    var m = a.href.match(/\/board\/([a-f0-9]{24})/);
    if(!m) return;
    var id = m[1];
    if(seen[id]) return;
    seen[id]=1;
    var card = a.closest('section') || a.closest('div[class]') || a.parentElement || a;
    var title = (card.innerText||a.innerText||'').replace(/\s+/g,' ').trim().slice(0,80);
    out.push({id:id, title:title});
  });
  return JSON.stringify(out);
})()
