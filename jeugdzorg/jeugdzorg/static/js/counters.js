!function(w, d){
  var 
    endpoint = '/counter/',
    interval = 10 * 1000,
    id = false,
    token = false,
    s = document.getElementById('counter'),
    events = ['click', 'mouseover', 'mouseout'],
    counters = [];
    
  if (s) {
    id = s.dataset.id;
  }
  if (id) {
    id = document.location.hostname + '_' + id;
    token = s.dataset.token;
  } else return;
  
  if (w.localStorage) {
    var cachedCounters = w.localStorage.getItem('counters');
    if (cachedCounters) {
      cachedCounters = JSON.parse(cachedCounters);
      if (cachedCounters && typeof cachedCounters == 'object') counters = cachedCounters;
    }
  }
  
  var _set = function(obj) {
    if (!obj.url) obj.url = w.location.href;
    if (!obj.name || !obj.value || !obj.url || obj.url.indexOf(w.location.origin) !== 0) return;
    obj.timestamp = (new Date()).getTime();
    obj.id = id;
    counters.push(obj);
    
    w.localStorage && w.localStorage.setItem('counters', JSON.stringify(counters));
    
  };

  for (var i = 0; i < events.length; i++) {
    
    d.addEventListener(events[i], function(t){
      var k, e, a = t && t.target;
      if (a = _closest(a, '[data-counter*="' + t.type + '."]')) {
        var r = a.getAttribute('data-counter').split(/\s+/);
        for (e = 0; e < r.length; e++){
          !r[e].indexOf(t.type) && _set({
            name: t.type,
            value: r[e].split(t.type + '.')[1]
          });
        }
      }
    });
  }
    
  _set({
    name: 'load.page',
    value: document.title
  });
    
    
  var _push = function(){
    if (!counters.length) return;
    
    var payload = JSON.stringify(counters);
    counters = [];
    w.localStorage && w.localStorage.removeItem('counters');
    
    // var xhr = new XMLHttpRequest();
    //
    // xhr.open('POST', endpoint, true);
    // xhr.setRequestHeader("X-CSRFToken", token);
    //
    // xhr.onload = function() {
    //   console.log(xhr);
    //   if (xhr.status >= 200 && xhr.status < 400) {
    //   }
    // };
    //
    // xhr.send(payload);
    
    console.log(payload);
  };
  
  setTimeout(_push, 1000);
  
  var _closest=function(e,t){var ms='MatchesSelector',c;['matches','webkit'+ms,'moz'+ms,'ms'+ms,'o'+ms].some(function(e){return'function'==typeof document.body[e]&&(c=e,!0)});var r=e;try{for(;e;){if(r&&r[c](t))return r;e=r=e.parentElement}}catch(e){}return null};
  
  setInterval(_push, interval)
    
}(window, document.documentElement);