!function(w, d){
  var 
    endpoint = '/event/add',
    interval = 10 * 1000,
    processing = false,
    events = ['click', 'mouseover', 'mouseout'],
    counters = [],
    token = d.querySelector('script[data-counter-token]');
  
  if (!token) return;
  token = token.dataset.counterToken;
    
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
    if (!counters.length || processing) return;
    
    processing = true;
    
    var payload = {
      'event_list': counters
    };

    var xhr = new XMLHttpRequest();

    xhr.open('post', endpoint, true);
    xhr.setRequestHeader("X-CSRFToken", token);

    xhr.onload = function() {
      if (xhr.status >= 200 && xhr.status < 400) {
        counters = [];
        w.localStorage && w.localStorage.removeItem('counters');
        console.log(payload);
      } else {
        console.log('error sending playload.');
      }
      processing = false;
    };

    xhr.send(payload);
    

  };
  
  setTimeout(_push, 1000);
  
  var _closest=function(e,t){var ms='MatchesSelector',c;['matches','webkit'+ms,'moz'+ms,'ms'+ms,'o'+ms].some(function(e){return'function'==typeof document.body[e]&&(c=e,!0)});var r=e;try{for(;e;){if(r&&r[c](t))return r;e=r=e.parentElement}}catch(e){}return null};
  
  setInterval(_push, interval)
    
}(window, document.documentElement);