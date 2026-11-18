/* ==========================================================================
   Interactive Product Showcase & Telemetry Engine (Bo Shang Portfolio & Site)
   Zero dependencies · Progressive enhancement · Reduced-motion friendly
   ========================================================================== */
(function () {
  'use strict';

  var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1. Inline Click-to-Play YouTube Video Cards (.js-yt-trigger) */
  function initVideoPlayers() {
    document.addEventListener('click', function (e) {
      var trigger = e.target.closest('.js-yt-trigger');
      if (!trigger) return;
      e.preventDefault();
      var videoId = trigger.getAttribute('data-yt-id');
      var title = trigger.getAttribute('data-yt-title') || 'Experimental video playback';
      if (!videoId) return;

      var stage = trigger.closest('.sc-video-card__stage');
      if (!stage) return;

      var iframe = document.createElement('iframe');
      iframe.setAttribute('src', 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(videoId) + '?autoplay=1&rel=0');
      iframe.setAttribute('title', title);
      iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
      iframe.setAttribute('allowfullscreen', '');
      iframe.className = 'sc-video-card__iframe';

      stage.innerHTML = '';
      stage.appendChild(iframe);
      stage.classList.add('is-playing');
    });
  }

  /* 2. Portfolio Scale Filter Tabs (.js-filter-btn) */
  function initPortfolioFilter() {
    var filterBar = document.querySelector('.js-portfolio-filters');
    if (!filterBar) return;

    var buttons = Array.prototype.slice.call(filterBar.querySelectorAll('.js-filter-btn'));
    var cards = Array.prototype.slice.call(document.querySelectorAll('.js-system-card'));

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var cat = btn.getAttribute('data-filter') || 'all';
        buttons.forEach(function (b) {
          var active = b === btn;
          b.classList.toggle('is-active', active);
          b.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
        cards.forEach(function (card) {
          var cardCat = card.getAttribute('data-category') || '';
          var match = (cat === 'all') || (cardCat.indexOf(cat) !== -1);
          card.hidden = !match;
        });
      });
    });
  }

  /* 3. Interactive PACO Cooperative Observability Simulator (#paco-sim) */
  function initPacoSimulator() {
    var root = document.getElementById('paco-sim');
    if (!root) return;

    var modes = {
      adas: {
        score: '0.37',
        partner: '41%',
        occluded: '3.3 / frame',
        constraint: 'Narrow 120° FOV + dynamic box-truck occlusion cone',
        fovDisplay: 'block',
        avDisplay: 'none',
        v2iDisplay: 'none',
        shadowOpacity: '0.78',
        vru1Class: 'is-occluded',
        vru2Class: 'is-occluded',
        vruStatus: '2 VRUs Masked in Truck Blind Zone',
        barWidth: '37%'
      },
      av360: {
        score: '0.61',
        partner: '97% → drops on turn',
        occluded: '3.3 / frame (peak)',
        constraint: 'Dynamic occlusion shadow persists despite 360° roof LiDAR',
        fovDisplay: 'none',
        avDisplay: 'block',
        v2iDisplay: 'none',
        shadowOpacity: '0.72',
        vru1Class: 'is-occluded',
        vru2Class: 'is-visible',
        vruStatus: 'Crosswalk Pedestrian Still Masked by Freight Box',
        barWidth: '61%'
      },
      v2i: {
        score: '1.00',
        partner: '100%',
        occluded: '0.0 unmonitored',
        constraint: 'Elevated mast overlooks truck roof — occlusion cone eliminated',
        fovDisplay: 'none',
        avDisplay: 'block',
        v2iDisplay: 'block',
        shadowOpacity: '0.12',
        vru1Class: 'is-visible',
        vru2Class: 'is-visible',
        vruStatus: 'All Conflict Partners Tracked in Metric 3D',
        barWidth: '100%'
      }
    };

    var btns = Array.prototype.slice.call(root.querySelectorAll('[data-paco-mode]'));
    var elScore = root.querySelector('[data-paco-out="score"]');
    var elPartner = root.querySelector('[data-paco-out="partner"]');
    var elOccluded = root.querySelector('[data-paco-out="occluded"]');
    var elConstraint = root.querySelector('[data-paco-out="constraint"]');
    var elStatus = root.querySelector('[data-paco-out="status"]');
    var elBar = root.querySelector('[data-paco-out="bar"]');
    var svgFov = root.querySelector('#paco-layer-adas');
    var svgAv = root.querySelector('#paco-layer-av');
    var svgV2i = root.querySelector('#paco-layer-v2i');
    var svgShadow = root.querySelector('#paco-occlusion-poly');
    var svgVru1 = root.querySelector('#paco-vru-1');
    var svgVru2 = root.querySelector('#paco-vru-2');

    function applyMode(key) {
      var m = modes[key];
      if (!m) return;
      btns.forEach(function (b) {
        var active = b.getAttribute('data-paco-mode') === key;
        b.classList.toggle('is-active', active);
        b.setAttribute('aria-selected', active ? 'true' : 'false');
      });
      if (elScore) elScore.textContent = m.score;
      if (elPartner) elPartner.textContent = m.partner;
      if (elOccluded) elOccluded.textContent = m.occluded;
      if (elConstraint) elConstraint.textContent = m.constraint;
      if (elStatus) elStatus.textContent = m.vruStatus;
      if (elBar) elBar.style.width = m.barWidth;
      if (svgFov) svgFov.style.display = m.fovDisplay;
      if (svgAv) svgAv.style.display = m.avDisplay;
      if (svgV2i) svgV2i.style.display = m.v2iDisplay;
      if (svgShadow) svgShadow.setAttribute('fill-opacity', m.shadowOpacity);
      if (svgVru1) {
        svgVru1.setAttribute('class', 'paco-vru ' + m.vru1Class);
      }
      if (svgVru2) {
        svgVru2.setAttribute('class', 'paco-vru ' + m.vru2Class);
      }
    }

    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        applyMode(b.getAttribute('data-paco-mode'));
      });
    });
    applyMode('v2i');
  }

  /* 4. Interactive BIRDS 4-Stage Perching & Traversal State Machine (#birds-fsm) */
  function initBirdsStateMachine() {
    var root = document.getElementById('birds-fsm');
    if (!root) return;

    var stages = {
      '1': {
        title: 'Stage 01 · GPS-Denied Approach Flight',
        desc: 'Quadrotor lifts the clamping-and-traversing payload beneath the steel bridge deck where satellite GPS is blocked, stabilizing hover via onboard IMU + optical/vision feedback.',
        rotors: 'ACTIVE (Hover Thrust)',
        vision: 'SCANNING ROI',
        clamps: 'OPEN (8.5 s travel)',
        rollers: 'STANDBY',
        droneY: '62',
        armLeftRot: '-28',
        armRightRot: '28',
        beamOpacity: '0.45'
      },
      '2': {
        title: 'Stage 02 · Onboard RGB-D Girder Center & Heading Lock',
        desc: 'NVIDIA Jetson segments the I-girder bottom flange in real time, computing lateral offset, heading angle, and vertical standoff distance until the trigger threshold is reached.',
        rotors: 'FINE ALIGNMENT',
        vision: 'LOCKED (d = 0.26 m)',
        clamps: 'ARMED FOR TRIGGER',
        rollers: 'STANDBY',
        droneY: '32',
        armLeftRot: '-24',
        armRightRot: '24',
        beamOpacity: '0.95'
      },
      '3': {
        title: 'Stage 03 · 1.3-Second Autonomous Flange Clamping',
        desc: 'Crossing the vertical distance threshold triggers rapid dual-arm closure in ~1.3 seconds with encoder position limits and PID/fractional-order force regulation against wind gust sway.',
        rotors: 'IDLE SPIN-DOWN',
        vision: 'VERIFYING GRIP',
        clamps: 'LOCKED ON FLANGE (1.3 s)',
        rollers: 'ENGAGING',
        droneY: '8',
        armLeftRot: '6',
        armRightRot: '-6',
        beamOpacity: '0.2'
      },
      '4': {
        title: 'Stage 04 · Zero-Flight-Power Motorized Girder Traversal',
        desc: 'Propellers power down completely. Motorized drive wheels roll BIRDS smoothly along the steel I-girder for continuous close-range visual, thermal, and hyperspectral inspection.',
        rotors: 'OFF (0 W Flight Power)',
        vision: 'DEFECT STREAMING',
        clamps: 'CLAMPED + ROLLING',
        rollers: 'DRIVING ALONG SPAN',
        droneY: '8',
        armLeftRot: '6',
        armRightRot: '-6',
        beamOpacity: '0.0',
        traverseShift: '36'
      }
    };

    var btns = Array.prototype.slice.call(root.querySelectorAll('[data-birds-stage]'));
    var elTitle = root.querySelector('[data-birds-out="title"]');
    var elDesc = root.querySelector('[data-birds-out="desc"]');
    var elRotors = root.querySelector('[data-birds-out="rotors"]');
    var elVision = root.querySelector('[data-birds-out="vision"]');
    var elClamps = root.querySelector('[data-birds-out="clamps"]');
    var elRollers = root.querySelector('[data-birds-out="rollers"]');
    var gVehicle = root.querySelector('#birds-svg-vehicle');
    var gArmL = root.querySelector('#birds-svg-arm-l');
    var gArmR = root.querySelector('#birds-svg-arm-r');
    var gBeam = root.querySelector('#birds-svg-beam');

    function setStage(id) {
      var s = stages[id];
      if (!s) return;
      btns.forEach(function (b) {
        var active = b.getAttribute('data-birds-stage') === id;
        b.classList.toggle('is-active', active);
        b.setAttribute('aria-selected', active ? 'true' : 'false');
      });
      if (elTitle) elTitle.textContent = s.title;
      if (elDesc) elDesc.textContent = s.desc;
      if (elRotors) elRotors.textContent = s.rotors;
      if (elVision) elVision.textContent = s.vision;
      if (elClamps) elClamps.textContent = s.clamps;
      if (elRollers) elRollers.textContent = s.rollers;

      var dx = s.traverseShift || '0';
      if (gVehicle) {
        gVehicle.setAttribute('transform', 'translate(' + dx + ',' + s.droneY + ')');
      }
      if (gArmL) {
        gArmL.setAttribute('transform', 'rotate(' + s.armLeftRot + ' 185 158)');
      }
      if (gArmR) {
        gArmR.setAttribute('transform', 'rotate(' + s.armRightRot + ' 295 158)');
      }
      if (gBeam) {
        gBeam.setAttribute('opacity', s.beamOpacity);
      }
    }

    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        setStage(b.getAttribute('data-birds-stage'));
      });
    });
    setStage('3');
  }

  /* 5. Interactive UAV Fractional-Order Sampling Period Explorer (#uav-sim) */
  function initUavSimulator() {
    var root = document.getElementById('uav-sim');
    if (!root) return;

    var presets = {
      fast: {
        h: '0.058 s (17.2 Hz)',
        fopdStatus: 'STABLE · Fast Rise, Iso-Damped (~6% Overshoot)',
        iopidStatus: 'STABLE · Higher Overshoot (~18%)',
        fopdPath: 'M 40,180 C 68,180 78,66 112,68 C 138,70 154,76 190,76 L 440,76',
        iopidPath: 'M 40,180 C 72,180 86,44 122,52 C 154,59 175,84 215,76 C 245,73 270,76 440,76'
      },
      medium: {
        h: '0.330 s (3.0 Hz)',
        fopdStatus: 'STABLE · Smooth Convergence Under Vision Latency',
        iopidStatus: 'DEGRADED · Pronounced Ringing & Slow Settling',
        fopdPath: 'M 40,180 C 78,180 96,62 138,67 C 172,71 198,76 240,76 L 440,76',
        iopidPath: 'M 40,180 C 80,180 98,28 136,36 C 172,44 196,112 238,104 C 276,96 306,62 346,72 C 378,79 406,76 440,76'
      },
      large: {
        h: '0.580 s (> 0.546 s IOPID Limit)',
        fopdStatus: 'STABLE · Remains Bounded Up to h_max = 0.933 s (+71% Margin)',
        iopidStatus: 'UNSTABLE · Exceeds 0.546 s Delay Bound — Divergent Oscillation',
        fopdPath: 'M 40,180 C 90,180 116,56 164,63 C 206,69 240,78 286,76 L 440,76',
        iopidPath: 'M 40,180 C 78,180 96,24 130,24 C 164,24 186,148 222,148 C 258,148 282,10 318,10 C 354,10 382,170 416,170 L 440,22'
      }
    };

    var btns = Array.prototype.slice.call(root.querySelectorAll('[data-uav-h]'));
    var elH = root.querySelector('[data-uav-out="h"]');
    var elFopd = root.querySelector('[data-uav-out="fopd"]');
    var elIopid = root.querySelector('[data-uav-out="iopid"]');
    var pathFopd = root.querySelector('#uav-curve-fopd');
    var pathIopid = root.querySelector('#uav-curve-iopid');

    function setPreset(key) {
      var p = presets[key];
      if (!p) return;
      btns.forEach(function (b) {
        var active = b.getAttribute('data-uav-h') === key;
        b.classList.toggle('is-active', active);
        b.setAttribute('aria-selected', active ? 'true' : 'false');
      });
      if (elH) elH.textContent = p.h;
      if (elFopd) elFopd.textContent = p.fopdStatus;
      if (elIopid) elIopid.textContent = p.iopidStatus;
      if (pathFopd) pathFopd.setAttribute('d', p.fopdPath);
      if (pathIopid) pathIopid.setAttribute('d', p.iopidPath);
    }

    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        setPreset(b.getAttribute('data-uav-h'));
      });
    });
    setPreset('large');
  }

  /* 6. Figure Lightbox Modal (.js-zoom-fig) */
  function initLightbox() {
    var figs = document.querySelectorAll('.js-zoom-fig');
    if (!figs.length) return;

    var modal = document.createElement('div');
    modal.className = 'sc-lightbox';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-label', 'Enlarged figure viewer');
    modal.hidden = true;
    modal.innerHTML =
      '<button class="sc-lightbox__close" aria-label="Close enlarged figure">&times;</button>' +
      '<div class="sc-lightbox__inner">' +
        '<img class="sc-lightbox__img" src="" alt="" />' +
        '<p class="sc-lightbox__caption"></p>' +
      '</div>';
    document.body.appendChild(modal);

    var modalImg = modal.querySelector('.sc-lightbox__img');
    var modalCap = modal.querySelector('.sc-lightbox__caption');
    var closeBtn = modal.querySelector('.sc-lightbox__close');

    function closeModal() {
      modal.hidden = true;
      modalImg.setAttribute('src', '');
      document.body.style.overflow = '';
    }

    document.addEventListener('click', function (e) {
      var img = e.target.closest('.js-zoom-fig');
      if (img) {
        var src = img.getAttribute('src');
        var alt = img.getAttribute('alt') || '';
        var figEl = img.closest('figure');
        var capEl = figEl ? figEl.querySelector('figcaption') : null;
        modalImg.setAttribute('src', src);
        modalImg.setAttribute('alt', alt);
        modalCap.textContent = capEl ? capEl.textContent : alt;
        modal.hidden = false;
        document.body.style.overflow = 'hidden';
        closeBtn.focus();
        return;
      }
      if (!modal.hidden && (e.target === modal || e.target.closest('.sc-lightbox__close'))) {
        closeModal();
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !modal.hidden) {
        closeModal();
      }
    });
  }

  /* 7. Scroll Reveal for Product Sections (.sc-reveal) */
  function initScrollReveal() {
    var items = document.querySelectorAll('.sc-reveal');
    if (!items.length) return;
    if (prefersReduced || !('IntersectionObserver' in window)) {
      Array.prototype.forEach.call(items, function (el) { el.classList.add('is-visible'); });
      return;
    }
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

    Array.prototype.forEach.call(items, function (el) { obs.observe(el); });
  }

  function boot() {
    initVideoPlayers();
    initPortfolioFilter();
    initPacoSimulator();
    initBirdsStateMachine();
    initUavSimulator();
    initLightbox();
    initScrollReveal();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
