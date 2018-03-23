!function(w, d){
  
  var handlers = {
    'list-add': function(){
      var 
        template = this.template.cloneNode(true),
        inputs = template.querySelectorAll('input, select');
        
      for (var i =0; i<inputs.length; i++) {
        inputs[i].id = inputs[i].id.replace(/-\d-/, '-' + this.list.children.length + '-');
        inputs[i].name = inputs[i].name.replace(/-\d-/, '-' + this.list.children.length + '-');
      }
      
      this.list.appendChild(template);
      
      var totalInputs = this.list.parentNode.querySelectorAll('[id*="-TOTAL_FORMS"]');
      
      for (var i =0; i<totalInputs.length; i++) {
        totalInputs[i].value = this.list.children.length;
      
      }
    },
    
    'list-remove': function(){
      var 
        li = this.parentNode,
        del = li.querySelectorAll('[name*="-DELETE"]');

      if (del.length) del[0].checked = true;
      li.classList.add('item-deleted');
    },
    
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
        
        // card.clone.style.transform = 'translate3d(' + placeholderBC.left + 'px, ' + placeholderBC.top + 'px, 0)';
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
        
        card.modal.classList.remove('extended');
        card.modal.classList.remove('on');
        card.modal.classList.remove('focus');
        card.modal.classList.remove('active');
        card.classList.remove('ghost');
        
        
        // with animation
        
        // d.classList.remove('has-modal-contact');
        //
        // card.modal.classList.remove('extended');
        //
        // setTimeout(function(){
        //   card.modal.classList.remove('on');
        //   setTimeout(function(){
        //     card.modal.classList.remove('focus');
        //     setTimeout(function(){
        //       card.modal.classList.remove('active');
        //       card.classList.remove('ghost');
        //     }, 200);
        //   }, 400);
        // },300);
        
      } else {

        card.classList.add('ghost');
        card.modal.classList.add('active');
        
        setTimeout(function(){
          card.modal.classList.add('focus');
          setTimeout(function(){
            card.modal.classList.add('on');
            card.modal.classList.add('extended');
          }, 400);
        }, 100);

      }

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
  
  d.addEventListener('click',function(t){var k,e,a=t&&t.target;if(a=_closest(a,'[data-handler]')){var r=a.getAttribute('data-handler').split(/\s+/);if('A'==a.tagName&&(t.metaKey||t.shiftKey||t.ctrlKey||t.altKey))return;for(e=0;e<r.length;e++){k=r[e].split(/[\(\)]/);handlers[k[0]]&&handlers[k[0]].call(a,t,k[1])}}});

  var scrollers=[];w.addEventListener('scroll',function(){requestAnimationFrame(function(){for(var l=0;l<scrollers.length;l++)scrollers[l].el&&scrollers[l].fn.call(scrollers[l].el)})},!1);
  
  var _scrollTo=function(n,o){var e,i=window.pageYOffset,t=window.pageYOffset+n.getBoundingClientRect().top,r=(document.body.scrollHeight-t<window.innerHeight?document.body.scrollHeight-window.innerHeight:t)-i,w=function(n){return n<.5?4*n*n*n:(n-1)*(2*n-2)*(2*n-2)+1},o=o||1e3;r&&window.requestAnimationFrame(function n(t){e||(e=t);var d=t-e,a=Math.min(d/o,1);a=w(a),window.scrollTo(0,i+r*a),d<o&&window.requestAnimationFrame(n)})};

  var _decorate = function(){var k,i,j,decoratorString,el,els=d.querySelectorAll('[data-decorator]');for(i=0;i<els.length;i++){for(decoratorString=(el=els[i]).getAttribute('data-decorator').split(/\s+/),j=0;j<decoratorString.length;j++){k=decoratorString[j].split(/[\(\)]/);decorators[k[0]]&&decorators[k[0]].call(el,k[1]);el.removeAttribute('data-decorator')}}};

  var _closest=function(e,t){var ms='MatchesSelector',c;['matches','webkit'+ms,'moz'+ms,'ms'+ms,'o'+ms].some(function(e){return'function'==typeof document.body[e]&&(c=e,!0)});var r=e;try{for(;e;){if(r&&r[c](t))return r;e=r=e.parentElement}}catch(e){}return null};
  
  _decorate();

}(window, document.documentElement);