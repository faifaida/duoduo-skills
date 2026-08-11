(function(){
  if(!window.__xhsArr) window.__xhsArr=[];
  var seen={}; window.__xhsArr.forEach(function(x){seen[x]=1;});
  var cards=document.querySelectorAll('section.note-item');
  for(var i=0;i<cards.length;i++){
    var c=cards[i];
    if(c.offsetParent===null) continue;
    var a=c.querySelector('a.cover');
    if(!a) continue;
    var href=a.getAttribute('href');
    if(!href) continue;
    var url=href.indexOf('http')===0?href:('https://www.xiaohongshu.com'+href);
    if(!seen[url]){ window.__xhsArr.push(url); seen[url]=1; }
  }
  return window.__xhsArr.length;
})()
