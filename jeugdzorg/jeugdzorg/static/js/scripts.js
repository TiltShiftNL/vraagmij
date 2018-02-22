!function(w, d){
  
  var handlers = {
    'list-add': function(){
      var 
        template = this.template.cloneNode(true),
        inputs = template.querySelectorAll('input');
        
      for (var i =0; i<inputs.length; i++) {
        inputs[i].id = inputs[i].id.replace(/-\d-/, '-' + this.list.children.length + '-');
        inputs[i].name = inputs[i].name.replace(/-\d-/, '-' + this.list.children.length + '-');
      }
      
      this.list.appendChild(template);
      
      document.getElementById('id_voorwaarde_set-TOTAL_FORMS').value = this.list.children.length;
    }
    ,
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
        var addRemove = el.classList.contains('active') ? 'remove' : 'add';
        el.classList[addRemove]('active');
        this.classList[addRemove]('active');
      }
    },
    
    'scroll': function(e){
      var target = document.getElementById(this.hash.substr(1));
      if (!target) return;
      e.preventDefault();
      _scrollTo(target);
    }
  };
  
  var decorators = {
    
    'progress': function(){
      var el = this;
      var id = el.dataset.regelingId;
      var items = el.children;
      var hashIcons = {
        yes: '■',
        no: '□',
        maybe: '▣'
      };

      var hashIcons = {
        yes: '+',
        no: '-',
        maybe: '_'
      };

      var progress = document.createElement('svg');
      progress.classList.add('regeling-progress');
      progress.width = 88;
      progress.height = 88;
      progress.viewBox = '0 0 88 88';
      progress.innerHTML = '';
      progress.innerHTML += '<circle class="initial" cx="44" cy="44" r="41" stroke-width="6" />';
      progress.innerHTML += '<circle class="yes" cx="44" cy="44" r="41" stroke-width="6" />';
      progress.innerHTML += '<circle class="no" cx="44" cy="44" r="41" stroke-width="6" />';
      
      // var progress = document.createElement('span');
      
      // progress.classList.add('regeling-progress');
      
      // progress.innerHTML = '<span class="yes"></span><span class="no"></span><span class="result"></span>';
      el.parentNode.appendChild(progress);
      var 
        resultEl = progress.querySelector('.result'),
        yesEl = progress.querySelector('.yes'),
        noEl = progress.querySelector('.no');
      
      
        var _change = function(){
        var 
          total = items.length,
          maybe = 0,
          yes = 0,
          no = 0;
          resultHash = [];

        resultHash.push('[');
          
        for (var i=0; i<items.length; i++) {
          if (items[i].querySelectorAll('[value="yes"]:checked').length) {
            resultHash.push(hashIcons.yes);
            yes++;
          }
          else if (items[i].querySelectorAll('[value="no"]:checked').length) {
            resultHash.push(hashIcons.no);
            no++;
          }
          else if (items[i].querySelectorAll('[value="maybe"]:checked').length) {
            resultHash.push(hashIcons.maybe);
          }
        }
        resultHash.push(']');
        document.location.hash = resultHash.join('');
        
        // resultEl.innerHTML = Math.round(yes / total * 100) + '<em>%</em>';
        
        var 
          yesResult = Math.round(yes / total * 100),
          noResult = Math.round(no / total * 100);
        
        // yesEl.style.width = yesResult + '%';
        // yesEl.style.height = yesResult + '%';
        // noEl.style.width = (yesResult + noResult) + '%';
        // noEl.style.height = (yesResult + noResult) + '%';
        
        progress.classList[(yes + no == total) ? 'add' : 'remove']('complete');
        progress.classList[(yes + no > 0) ? 'add' : 'remove']('started');
        
        progress.classList.remove('complete-no');
        progress.classList.remove('complete-yes');
        
        if (yes + no == total) {
          if (yes == total) {
            progress.classList.add('complete-yes');
          } else {
            progress.classList.add('complete-no');
          }
        }
        
      };
      
      
      
      for (var i=0; i<items.length; i++) {
        var yesno = document.createElement('div');
        yesno.classList.add('regeling-voorwaarde-yesno');
        yesno.innerHTML = '';
        
        yesno.innerHTML += '<input id="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-yes" name="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '" type="radio" value="yes">';
        yesno.innerHTML += '<label for="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-yes">Ja</label>';

        yesno.innerHTML += '<input id="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-no" name="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '" type="radio" value="no">';
        yesno.innerHTML += '<label for="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-no">Nee</label>';

        yesno.innerHTML += '<input id="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-initial" name="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '" type="radio" value="maybe" checked>';
        yesno.innerHTML += '<label for="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-initial">Misschien</label>';
        items[i].appendChild(yesno);
      }
      
      // setting initial state based on hash
      
      if (w.location.hash) {
        var initial = w.location.hash.match(/\[([\+-_]*)\]/);
        if (initial && initial[1]) {
          var state = initial[1].split('');
          
          if (items.length == state.length) {
          
            for (var i=0; i<state.length; i++) {
              if (state[i] == hashIcons.yes) items[i].querySelectorAll('[value="yes"]')[0].checked = true;
              else if (state[i] == hashIcons.no) items[i].querySelectorAll('[value="no"]')[0].checked = true;
            }
            
          }
        }
      }
      
      el.addEventListener('change', _change); _change();
    },
    
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
      
    }

  };
  
  var helpers = {

  };
  
  d.addEventListener('click',function(t){var k,e,a=t&&t.target;if(a=_closest(a,'[data-handler]')){var r=a.getAttribute('data-handler').split(/\s+/);if('A'==a.tagName&&(t.metaKey||t.shiftKey||t.ctrlKey||t.altKey))return;for(e=0;e<r.length;e++){k=r[e].split(/[\(\)]/);handlers[k[0]]&&handlers[k[0]].call(a,t,k[1])}}});
  
  var scrollers=[];w.addEventListener('scroll',function(){requestAnimationFrame(function(){for(var l=0;l<scrollers.length;l++)scrollers[l].el&&scrollers[l].fn.call(scrollers[l].el)})},!1);
  
  var _scrollTo=function(n,o){var e,i=window.pageYOffset,t=window.pageYOffset+n.getBoundingClientRect().top,r=(document.body.scrollHeight-t<window.innerHeight?document.body.scrollHeight-window.innerHeight:t)-i,w=function(n){return n<.5?4*n*n*n:(n-1)*(2*n-2)*(2*n-2)+1},o=o||1e3;r&&window.requestAnimationFrame(function n(t){e||(e=t);var d=t-e,a=Math.min(d/o,1);a=w(a),window.scrollTo(0,i+r*a),d<o&&window.requestAnimationFrame(n)})};

  var _decorate = function(){
    var k,i,j,decoratorString,el,els=d.querySelectorAll('[data-decorator]');for(i=0;i<els.length;i++){for(decoratorString=(el=els[i]).getAttribute('data-decorator').split(/\s+/),j=0;j<decoratorString.length;j++){k=decoratorString[j].split(/[\(\)]/);decorators[k[0]]&&decorators[k[0]].call(el,k[1]);el.removeAttribute('data-decorator')}}    
  }; _decorate();

  var _closest=function(e,t){var ms='MatchesSelector',c;['matches','webkit'+ms,'moz'+ms,'ms'+ms,'o'+ms].some(function(e){return'function'==typeof document.body[e]&&(c=e,!0)});var r=e;try{for(;e;){if(r&&r[c](t))return r;e=r=e.parentElement}}catch(e){}return null};

}(window, document.documentElement);
