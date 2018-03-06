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
    }
  };
  
  var decorators = {
    
    'progress': function(){
      

      var 
        el = this,
        id = el.dataset.regelingId,
        items = el.children,
        prevResult = [0,0],
        result = [0,0],
        animation,
        regeling = _closest(el, '.regeling');

      var hashIcons = {
        yes: '1',
        no: '0',
        maybe: '_'
      };

      var hasAanvragen = document.getElementById('regeling-aanvragen');
      var progress = document.createElement(hasAanvragen ? 'a' : 'span');
      
      if (hasAanvragen) {
        progress.href = '#regeling-aanvragen';
        progress.dataset.handler = 'scroll';
      }
      progress.classList.add('regeling-progress');
      progress.innerHTML = '<span class="result"></span>';
      progress.innerHTML += '<span class="yes-1"><span></span></span><span class="yes-2"><span></span></span>';
      progress.innerHTML += '<span class="no-1"><span></span></span><span class="no-2"><span></span></span>';
      
      
      regeling.insertBefore(progress, regeling.firstChild);

      var 
        resultEl = progress.querySelector('.result'),
        yesEls = [progress.querySelector('.yes-1 span'), progress.querySelector('.yes-2 span')],
        noEls = [progress.querySelector('.no-1 span'), progress.querySelector('.no-2 span')],
        noEl = [progress.querySelector('.no-1'), progress.querySelector('.no-2')];
      
      var _update = function(y, n, t){
        
        resultEl.innerHTML = Math.round(y / t * 100);
        
        var 
          yesResult = (y / t * 360),
          noResult =  (n / t * 360);

        _render(yesResult, noResult);
        
      };
      
      var _updateByPercentages = function(a, b) {
        
        resultEl.innerHTML = a;
        
        var 
          yesResult = (a/100 * 360),
          noResult =  (b/100 * 360);
          
        _render(yesResult, noResult);

      };
      
      var _render = function(yesResult, noResult) {
        yesEls[0].style.transform = 'rotate(' + Math.min(180, yesResult) + 'deg)';
        yesEls[1].style.transform = 'rotate(' + Math.max(-180, yesResult - 360) + 'deg)';
        
        noEl[0].style.transform = 'rotate(' + yesResult + 'deg)';
        noEl[1].style.transform = 'rotate(' + yesResult + 'deg)';
        
        noEls[0].style.transform = 'rotate(' + Math.min(180, noResult) + 'deg)';
        noEls[1].style.transform = 'rotate(' + Math.max(-180, noResult - 360) + 'deg)';
      };
      
      var _change = function(){
        var 
          total = items.length,
          maybe = 0,
          yes = 0,
          no = 0;
          resultHash = [];

        animation && cancelAnimationFrame(animation);

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
        // document.location.hash = resultHash.join('');

        // setting counters
        progress.dataset.counter = 'click.detail.progress.' + (hasAanvragen ? 'aanvragen' : 'indicatief') + '.total.' + total + '.yes.' + yes + '.no.' + no;

        result = [Math.round(yes*100/total), Math.round(no*100/total)];
        
        var step = [prevResult[0] < result[0] ? 1 : -1, prevResult[1] < result[1] ? 1 : -1];
        
        var _animate = function(){
          animating = false;
          _updateByPercentages(prevResult[0], prevResult[1])
          if (prevResult[0] != result[0]) {
            prevResult[0] = prevResult[0] + step[0];
            animating = true;
          }
          if (prevResult[1] != result[1]) {
            prevResult[1] = prevResult[1] + step[1];
            animating = true;
          }
          if (animating) {
            animation = requestAnimationFrame(_animate);
          }

        }
        
        window.requestAnimationFrame ? _animate() : _update(yes, no, total);
        
        
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
        yesno.innerHTML += '<label data-counter="click.voorwaarde.' + items[i].dataset.voorwaardeId + '.yes mouseout.voorwaarde.' + items[i].dataset.voorwaardeId + '.yes mouseover.voorwaarde.' + items[i].dataset.voorwaardeId + '.yes" for="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-yes">Ja</label>';

        yesno.innerHTML += '<input id="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-no" name="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '" type="radio" value="no">';
        yesno.innerHTML += '<label data-counter="click.voorwaarde.' + items[i].dataset.voorwaardeId + '.no mouseout.voorwaarde.' + items[i].dataset.voorwaardeId + '.no mouseover.voorwaarde.' + items[i].dataset.voorwaardeId + '.no" for="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-no">Nee</label>';

        yesno.innerHTML += '<input id="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-initial" name="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '" type="radio" value="maybe" checked>';
        yesno.innerHTML += '<label data-counter="click.voorwaarde.' + items[i].dataset.voorwaardeId + '.initial mouseout.voorwaarde.' + items[i].dataset.voorwaardeId + '.initial mouseover.voorwaarde.' + items[i].dataset.voorwaardeId + '.initial" for="voorwaarde-' + id + '-' + items[i].dataset.voorwaardeId + '-initial">Misschien</label>';
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

  var _decorate = function(){var k,i,j,decoratorString,el,els=d.querySelectorAll('[data-decorator]');for(i=0;i<els.length;i++){for(decoratorString=(el=els[i]).getAttribute('data-decorator').split(/\s+/),j=0;j<decoratorString.length;j++){k=decoratorString[j].split(/[\(\)]/);decorators[k[0]]&&decorators[k[0]].call(el,k[1]);el.removeAttribute('data-decorator')}}};

  var _closest=function(e,t){var ms='MatchesSelector',c;['matches','webkit'+ms,'moz'+ms,'ms'+ms,'o'+ms].some(function(e){return'function'==typeof document.body[e]&&(c=e,!0)});var r=e;try{for(;e;){if(r&&r[c](t))return r;e=r=e.parentElement}}catch(e){}return null};
  
  _decorate();

}(window, document.documentElement);