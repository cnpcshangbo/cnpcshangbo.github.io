(function () {
  'use strict';
  var root = document.querySelector('.pubs');
  if (!root) return;
  var search = root.querySelector('#publication-search');
  var type = root.querySelector('#publication-type');
  var chips = Array.from(root.querySelectorAll('[data-filter]'));
  var sections = Array.from(root.querySelectorAll('[data-year-section]'));
  var entries = Array.from(root.querySelectorAll('[data-publication]')).map(function (element) {
    return { element: element, text: normalize(element.textContent) };
  });
  var reset = root.querySelector('[data-pub-reset]');
  var topic = 'all';

  function normalize(text) {
    return text.toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[\u2010-\u2015]/g, '-');
  }

  function apply() {
    var words = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    var count = 0;
    entries.forEach(function (entry) {
      var element = entry.element;
      var match = (topic === 'all' || element.dataset.topic === topic) &&
        (type.value === 'all' || element.dataset.type === type.value) &&
        words.every(function (word) { return entry.text.indexOf(word) !== -1; });
      element.hidden = !match;
      if (match) count++;
    });
    sections.forEach(function (section) {
      var visible = section.querySelectorAll('[data-publication]:not([hidden])').length;
      section.hidden = visible === 0;
      section.querySelector('[data-year-count]').textContent = visible;
      root.querySelector('[data-year-link="' + section.dataset.yearSection + '"]').hidden = visible === 0;
    });
    chips.forEach(function (chip) {
      var active = chip.dataset.filter === topic;
      chip.classList.toggle('is-active', active);
      chip.setAttribute('aria-pressed', String(active));
    });
    var filtered = words.length > 0 || topic !== 'all' || type.value !== 'all';
    reset.hidden = !filtered;
    root.querySelector('[data-pub-empty]').hidden = count !== 0;
    root.querySelector('[data-pub-count]').textContent = filtered ?
      'Showing ' + count + ' of ' + entries.length + ' research outputs' :
      'Showing all ' + entries.length + ' research outputs';
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () { topic = chip.dataset.filter; apply(); });
  });
  search.addEventListener('input', apply);
  type.addEventListener('change', apply);
  reset.addEventListener('click', function () {
    search.value = '';
    type.value = 'all';
    topic = 'all';
    apply();
    search.focus();
  });
  root.querySelector('[data-pub-controls]').hidden = false;
  apply();
})();
