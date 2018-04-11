!function(w, d){
  
  var handlers = {

    'toggle': function(e) {
      var el = document.getElementById(this.hash.substr(1));
      if (el) {
        e.preventDefault();
        var 
          wasActive = this.hash == w.location.hash,
          addRemove = wasActive ? 'remove' : 'add';

        el.classList[addRemove]('active');
        this.classList[addRemove]('active');
        var url = document.location.href.split('#')[0];
        if (history.replaceState) {
          w.location.hash = '_';
          history.replaceState({id: url}, d.title, wasActive ? url : url + this.hash);
        }
        
      }
    },
    
    'scroll': function(e){
      var target = document.getElementById(this.hash.substr(1));
      if (!target) return;
      e.preventDefault();
      _scrollTo(target);
    },
    
    'view': function(e){
      e.preventDefault();
      d.setAttribute('data-view', this.hash.substr(1));
      w.localStorage && w.localStorage.setItem('view', d.dataset.view);
    },
    
    'modal': function(e){
      e.preventDefault();
      var 
        el = this.hash && document.getElementById(this.hash.substring(1)),
        url = this.href, 
        template = '<div class="modal-inner">[[CONTENT]]</div><a href="#" class="modal-close" data-handler="modal-close">SLUITEN</a>';
        content = false;
        
      var _render = function(content){
        var modal = document.createElement('div');
        modal.classList.add('modal');
        modal.innerHTML = template.replace('[[CONTENT]]', content);
        document.body.appendChild(modal);
        setTimeout(function(){
          modal.classList.add('active');
        }, 300);
      };
      
      if (el) {
        content = el.innerHTML;
        _render(content);
      } else if (url) {
        helpers.ajax(url, function(response){
          if (response.status >= 200 && response.status < 400) {
            var r = document.createElement('div');
            r.innerHTML = response.responseText;
            (content = r.querySelector('main')) && _render(content.innerHTML);
          } else {
            w.location = url;
          }
        });
      } else {
        w.location = url;
      }
      
    },
    
    'choices': function(e){
      var 
        el = this.hash && document.getElementById(this.hash.substring(1)),
        form = el && _closest(el, 'form'),
        template = '<div class="modal-inner">[[CONTENT]]</div><a href="#" class="modal-close" data-handler="modal-close">SLUITEN</a>',
        modal;
      
      var _render = function(content){
        modal = document.createElement('div');
        modal.classList.add('modal');
        modal.innerHTML = template.replace('[[CONTENT]]', content);
        document.body.appendChild(modal);
        setTimeout(function(){
          modal.classList.add('active');
        }, 300);
      };
      
      var _change = function(e) {
        
        
        if (e) {
          var t = e.srcElement || e.originalTarget;
          var input = _closest(t, '.group-label');

          if (input) {
            
            var inputs = input.nextElementSibling.querySelectorAll('input');

            for (var l=0; l<inputs.length; l++) {
              inputs[l].checked = input.querySelector('input').checked;
            }

          }
        }

        setTimeout(function(){
          var els = modal.querySelectorAll('.group-label');
          for (var i = els.length; i > 0; i--) {
            var 
              input = els[(i-1)],
              next = input.nextElementSibling;

              input.querySelector('input').checked = (next.querySelectorAll('input').length == next.querySelectorAll(':checked').length);
          }
          
        },100);
        
        var els = modal.querySelectorAll('input');
        for (var i = 0; i < els.length; i++) {
          var input = document.getElementById(els[i].dataset.id);
          if (input) {
            input.checked = els[i].checked;
          }
        }
        
        el.classList[el.querySelectorAll(':checked').length ? 'add' : 'remove']('has-items');

      };
      
      if (el) {
        e.preventDefault();
        var fieldset = _closest(el, 'fieldset');
        _render('<div class="well">' + fieldset.innerHTML.replace(/ (for|id)="/gi, ' data-id="') + '</div>');
        
        var els = modal.querySelectorAll('input');
        for (var i = 0; i < els.length; i++) {
          els[i].removeAttribute('checked');
          var input = document.getElementById(els[i].dataset.id);
          if (input && input.checked) els[i].setAttribute('checked', 'checked');
        }
        modal.addEventListener('change', function(e){
          form.classList.add('changed');
          _change(e);
        }); _change(false);
        
      }
    },
    
    'back': function(e){
      !this.handled && history.go(-1);
    },
    
    'modal-close': function(e){
      var modal = _closest(this, '.modal');
      if (modal) {
        e.preventDefault();
        this.handled = true;
        modal.parentNode.removeChild(modal);
      }
    },
    
    'contact': function(e) {
      var 
        hash = this.hash.substr(1),
        card = document.getElementById(hash);
      if (!card) return;
      
      e.preventDefault();
      
      var _position = function(){
        
        var placeholderBC = card.getBoundingClientRect();
        
        card.clone.style.marginLeft = placeholderBC.left + 'px';
        card.clone.style.marginTop = placeholderBC.top + 'px';
      
        card.clone.style.width = placeholderBC.width + 'px';
        card.clone.style.height = placeholderBC.height + 'px';
        
      };
      
      
      
      if (!card.modal) {
        card.modal = document.createElement('div');
        card.modal.classList.add('modal-contact');
        card.clone = card.cloneNode(true);
        card.modal.appendChild(card.clone);
        
        var closeModal = document.createElement('a');
        closeModal.classList.add('modal-close');
        closeModal.href = this.hash;
        closeModal.dataset.handler = 'contact';
        
        card.modal.appendChild(closeModal);
        
        card.clone.removeAttribute('id');
        
        document.body.appendChild(card.modal);
        
      }
      _position();
      
      if (card.modal.classList.contains('active')) {
        
        card.modal.classList.remove('on');
        card.modal.classList.remove('focus');
        card.modal.classList.remove('active');
        card.classList.remove('ghost');
        
      } else {

        card.classList.add('ghost');
        card.modal.classList.add('active');
        
        setTimeout(function(){
          card.modal.classList.add('focus');
          setTimeout(function(){
            card.modal.classList.add('on');
            card.modal.classList.add('extended');
          }, 300);
        }, 100);

      }

    },
    
    'search-close': function(e){
      e.preventDefault();
      var q = d.querySelector('input[name="q"]');
      if (q) q.value = '';
      d.classList.remove('search-mode');
    }
    
  };
  
  var decorators = {
    
    'list': function(){
      
      var remove = document.createElement('button');
      remove.dataset.handler = 'list-remove';
      remove.type = 'button';
      remove.innerHTML = '[-] item verwijderen';

      for (var i=0; i<this.children.length; i++) {
        this.children[i].appendChild(remove.cloneNode(true));
      }
      
      var add = document.createElement('button');
      add.dataset.handler = 'list-add';
      add.type = 'button';
      add.innerHTML = '[+] item toevoegen';

      add.list = this;
      
      add.template = add.list.querySelectorAll("li:last-child")[0].cloneNode(true);

      this.parentNode.appendChild(add);
    },
    
    'scroll': function(){
      if (document.getElementById(this.hash.substr(1))) {
        this.dataset.handler = 'scroll';
      } else {
        this.classList.add('disabled');
      }
    },
    
    'scroller': function(){
      scrollers.push({
        el: this,
        fn: function(){
          d.classList[this.getBoundingClientRect().top < -100 ? 'add' : 'remove']('scrolled');
        }
      });
      
    },
    
    'avatar': function(){
      this.addEventListener('change', function(e){
        var 
          remove = this.querySelectorAll('[name*="clear"]'),
          file = this.querySelectorAll('[type="file"]'),
          avatar = this.querySelectorAll('.icon-avatar'),
          original = this.querySelectorAll('a');
          
        if (!file || !avatar) return;
        remove = remove && remove[0];
        file = file[0];
        avatar = avatar[0];
        original = original && original[0];
        
        if (remove && remove.checked) {
          avatar.setAttribute('style', null);
          file.value = '';
        } else {
          var url = (file.value != '' ? URL.createObjectURL(e.target.files[0]) : original ? original.href : '');
          if (url) {
            avatar.style.backgroundImage = 'url(' + url + ')';
          } else {
            avatar.setAttribute('style', null);
          }
        }
          
      });
    },
    
    'change': function(){
      this.addEventListener('change', function(){
        this.classList.add('changed');
      });
      this.addEventListener('keyup', function(){
        this.classList.add('changed');
      });
    },
    
    'empty': function(){
      var el = this;
      
      var _empty = function(){
        el.classList[el.querySelectorAll(':checked').length ? 'add' : 'remove']('has-items');
      };
      
      el.addEventListener('change', _empty); _empty();
      
    },
    
    'search': function(){
      var q = [],
          cards = [],
          zoekContainer = document.querySelector('#zoeken > .container'),
          contains = function(selector, text) {
            var elements = document.querySelectorAll(selector),
                results = [];
            for(var i = 0; i < text.length; i++){
              results.push(false);
            }
            return Array.prototype.filter.call(elements, function(element){
              var searchables = element.querySelectorAll('[data-zb]'),
                  elResults = results.slice(0),
                  i, j;
              for (i = 0; i < searchables.length; i++){
                var t = searchables[i].dataset.zb;
                for(j = 0; j < text.length; j++){
                  var q = text[j].replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&'),
                      r = RegExp(q + '(?![^<]*>|[^<>]*</)', 'gi'),
                      match,
                      l = text[j].length;
                  while (match = r.exec(t)) {
                    var m = t.substr(match.index, l);
                    t = t.substr(0, match.index) + '<mark>' + m + '</mark>' + t.substr(match.index + l);
                    elResults[j] = true;
                  }
                }
                searchables[i].innerHTML = t;
              }
              for (i = 0; i < elResults.length; i++){
                if (!elResults[i]){
                  return false
                }
              }
              return true;
            });
          },
          cleanQ = function (qRaw) {
              var i;
              if (qRaw === '') return [];

              var _q = (qRaw.split(' ').length > 0) ? qRaw.split(' ') : [qRaw];
              for (i = 0; i < _q.length; i++){
                _q[i] = _q[i].trim();
              }
              _q = _q.filter(function(item, pos) {
                  if (item === '') return false;
                  return _q.indexOf(item) === pos;
              });
              _q = Array.prototype.filter.call(_q, function(qu, index){
                for (var i = 0; i < _q.length; i++){
                  if (index !== i && _q[i].indexOf(qu) !== -1){
                    return false;
                  }
                }
                return true;
              });
              return _q;
          },
          zoek = function () {
              var panes = zoekContainer.querySelectorAll('[data-resultcount]'),
                  i;
              
              for (i = 0; i < panes.length; i++) {
                panes[i].dataset.resultcount = 0;
              }
              
              for (i = 0; i < cards.length; i++){
                cards[i].parentNode.classList.add('zoeken-verberg');
              }
              var foundlements = contains('.zr', q);

              for (i = 0; i < foundlements.length; i++){
                foundlements[i].parentNode.classList.remove('zoeken-verberg');
                foundlements[i].parentNode.parentNode.parentNode.dataset.resultcount++;
                
              }
              zoekContainer.style.display='block';

          };
          

      this.addEventListener('focus', function(e){

        var 
          input = this,
          hasData = false;

        helpers.ajax('/zoek/', function(response){
          if (response.status >= 200 && response.status < 400) {
            zoekContainer.innerHTML = response.responseText;
            cards = zoekContainer.querySelectorAll('.zr');
            hasData = true;
            if (q.length > 0) {
              zoek();
            }
          }
        });
        input.addEventListener('keydown', function(e){
          if (e.keyCode == 13) e.preventDefault();
        });
        input.addEventListener('keyup', function(e){
          if (hasData) {
            q = cleanQ(this.value);
            zoek();
          }
        });
        
        d.classList.add('search-mode');
        
      });
    },
    'profiel-connect': function () {
        var el = this,
            handler = function(e){
              e.preventDefault();
              var data = {}
              for (var k in this.dataset) {
                data[k.replace(/(?:^|\.?)([A-Z])/g, function (x,y){return "_" + y.toLowerCase()}).replace(/^_/, "")] = this.dataset[k]
              }
              post('/profiel-connect/', data);
            },
            post = function(endpoint, data){
              var xhr = new XMLHttpRequest();
              xhr.open('post', endpoint, true);
              xhr.setRequestHeader("X-CSRFToken", d.querySelector('script[data-counter-token]').dataset.counterToken);
              xhr.setRequestHeader("Content-Type", "application/json");
              xhr.onload = function() {
                if (xhr.status >= 200 && xhr.status < 400) {

                  var status = JSON.parse(xhr.responseText).status;
                  if (status === 'toegevoegd'){
                    el.classList.add('aan');
                  } else {
                    el.classList.remove('aan');

                  }
                } else {
                  console.log(xhr.status);
                }
              };
              var str = JSON.stringify(data);
              xhr.send(str);
            };
        this.addEventListener('click', handler);
    },

    // Dit is niet een paasei
    'vraag-mij-maar-amsterdam': function(){
      var player;
      
      var
        trigger = 'vraagmijmaaramsterdam',
        keystroke = '';
      
      this.addEventListener('keyup', function(e){
        var char = String.fromCharCode(e.keyCode).toLowerCase();
        if (trigger.indexOf(keystroke) === 0) {
          keystroke += char;
        } else {
          keystroke = char;
        }
        
        if (!player && keystroke == trigger) {
          player = document.createElement('iframe');
          player.classList.add('vraag-mij-maar-amsterdam');
          player.src = 'https://www.youtube.com/embed/Z8XbFcl-yJg?autoplay=1';
          player.allow = 'autoplay; encrypted-media';
          
          document.body.appendChild(player);

        }
      });
    }
  
  };
  
  var submitters = {
    'gebruiker-uitnodigen': function(e){
      
      var 
        container = this,
        form = container.querySelector('form');

      var post = function (endpoint, data) {
        var xhr = new XMLHttpRequest();
        xhr.open('post', endpoint, true);
        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhr.onload = function() {
          if (xhr.status >= 200 && xhr.status < 400) {
            container.innerHTML = xhr.responseText;
          } else {
            console.log(xhr.status);
          }
        };
        var str = serialize(data);
        xhr.send(str);
      };
      var serialize = function(obj) {
        var str = [];
        for (var p in obj)
          if (obj.hasOwnProperty(p)) {
            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
          }
        return str.join("&");
      };
      
      e.preventDefault();
      var elements = form.querySelectorAll('input');
      var obj ={};
      for(var i = 0 ; i < elements.length ; i++){
          var item = elements.item(i);
          obj[item.name] = item.value;
      }
      post(form.getAttribute('action'), obj);
      
    },
    
    
    
  };
  
  var helpers = {
    'ajax': function(url, callback){
      var request = new XMLHttpRequest();
      
      request.open('GET', url, true);
      request.onload = function() {
        callback(request);
      }
      
      request.send();
      
    }
    
  };
  
  if (w.location.hash) {
    var el = document.querySelector('.main ' + w.location.hash);
    if (el) {
      setTimeout(function(){
        d.classList.add('scrollable');
        w.scrollTo(0,0);
        setTimeout(function(){
          _scrollTo(el);
        }, 800);
      },1);
    }
  }
  
  d.addEventListener('click',function(t){var k,e,a=t&&t.target;if(a=_closest(a,'[data-handler]')){var r=a.getAttribute('data-handler').split(/\s+/);if('A'==a.tagName&&(t.metaKey||t.shiftKey||t.ctrlKey||t.altKey))return;for(e=0;e<r.length;e++){k=r[e].split(/[\(\)]/);handlers[k[0]]&&handlers[k[0]].call(a,t,k[1])}}});
  
  d.addEventListener('submit',function(t){var k,e,f=t&&t.target;if(f=_closest(f,'[data-submitter]')){var r=f.getAttribute('data-submitter').split(/\s+/);for(e=0;e<r.length;e++){k=r[e].split(/[\(\)]/);submitters[k[0]]&&submitters[k[0]].call(f,t,k[1])}}});

  var scrollers=[];w.addEventListener('scroll',function(){requestAnimationFrame(function(){for(var l=0;l<scrollers.length;l++)scrollers[l].el&&scrollers[l].fn.call(scrollers[l].el)})},!1);
  
  var _scrollTo=function(n,o){var e,i=window.pageYOffset,t=window.pageYOffset+n.getBoundingClientRect().top,r=(document.body.scrollHeight-t<window.innerHeight?document.body.scrollHeight-window.innerHeight:t)-i,w=function(n){return n<.5?4*n*n*n:(n-1)*(2*n-2)*(2*n-2)+1},o=o||1e3;r&&window.requestAnimationFrame(function n(t){e||(e=t);var d=t-e,a=Math.min(d/o,1);a=w(a),window.scrollTo(0,i+r*a),d<o&&window.requestAnimationFrame(n)})};

  var _decorate = function(){var k,i,j,decoratorString,el,els=d.querySelectorAll('[data-decorator]');for(i=0;i<els.length;i++){for(decoratorString=(el=els[i]).getAttribute('data-decorator').split(/\s+/),j=0;j<decoratorString.length;j++){k=decoratorString[j].split(/[\(\)]/);decorators[k[0]]&&decorators[k[0]].call(el,k[1]);el.removeAttribute('data-decorator')}}};

  var _closest=function(e,t){var ms='MatchesSelector',c;['matches','webkit'+ms,'moz'+ms,'ms'+ms,'o'+ms].some(function(e){return'function'==typeof document.body[e]&&(c=e,!0)});var r=e;try{for(;e;){if(r&&r[c](t))return r;e=r=e.parentElement}}catch(e){}return null};
  
  _decorate();

}(window, document.documentElement);