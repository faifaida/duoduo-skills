(function(){
  function txt(s){var e=document.querySelector(s);return e?e.innerText.trim():null;}
  // 风控/安全验证页检测：命中则标记无效，不写脏笔记
  var _body = document.body ? document.body.innerText : '';
  var _t = document.title || '';
  var _all = _t + ' ' + _body;
  // 限流：抓太猛触发，页面回 Too many requests / Try again later，标题常为「安全限制」
  if(/too many requests|try again later|请求过于频繁|访问频繁|稍后(再|重)试|安全限制|rate limit/i.test(_all)){
    return JSON.stringify({title:null, desc:'', author:'', time:null, blocked:true, throttled:true});
  }
  if(/Security Verification|安全验证|滑动验证|人机验证|please slide|verify you are human|验证码|系统检测/i.test(_all)){
    return JSON.stringify({title:null, desc:'', author:'', time:null, blocked:true});
  }
  var raw = txt('#detail-title') || txt('.title') || document.title || '(无标题)';
  raw = raw.replace(/\s*[-–—·]\s*小红书.*$/,'').trim();
  var desc = txt('#detail-desc') || txt('.note-content') || txt('.desc') || '';
  desc = desc.replace(/\s*猜你想搜[\s\S]*$/,'').replace(/\s*编辑于[\s\S]*$/,'').trim();
  var author = txt('.author-wrapper .name') || txt('.author .name') || txt('.username') || '';
  var date = null;
  var dEl = txt('.date') || txt('.publish-date');
  if(dEl){
    var f = dEl.match(/(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})/);
    if(f){ date = f[1]+'-'+('0'+f[2]).slice(-2)+'-'+('0'+f[3]).slice(-2); }
    else {
      var rel = dEl.match(/(今天|昨天|刚刚|前天)/);
      if(rel){
        var d=new Date();
        if(rel[1]==='昨天'){ d.setDate(d.getDate()-1); }
        else if(rel[1]==='前天'){ d.setDate(d.getDate()-2); }
        date = d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);
      } else {
        var m2 = dEl.match(/(\d{1,2})[-/.](\d{1,2})/);
        if(m2){ var y=new Date().getFullYear(); date = y+'-'+('0'+m2[1]).slice(-2)+'-'+('0'+m2[2]).slice(-2); }
      }
    }
  }
  if(!date){
    var body=document.body?document.body.innerText:'';
    var dm=body.match(/(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})/);
    if(dm){ date=dm[1]+'-'+('0'+dm[2]).slice(-2)+'-'+('0'+dm[3]).slice(-2); }
  }
  return JSON.stringify({title:raw, desc:desc, author:author, time:date});
})()
