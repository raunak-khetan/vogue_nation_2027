//gowtham-start
// Vogue Nation - Alcheringa 2027

(() => {
  window.addEventListener('load', () => {
    document.fonts.ready.then(() => {
      const pageLoader = document.getElementById('pageLoader');
      if (pageLoader) pageLoader.classList.add('page-loader--hidden');
    });
  });

  // Utility math
  const clamp = (v, min = 0, max = 1) => Math.min(max, Math.max(min, v));
  const lerp = (a, b, t) => a + (b - a) * t;

  // virtual canvas scaler
  const updateScale = () => {
    const scale = Math.min(window.innerWidth / 1440, window.innerHeight / 900);
    const mobileStageScale = window.innerWidth <= 768
      ? Math.max(0.88, window.innerHeight / 900)
      : Math.max(window.innerWidth / 1440, window.innerHeight / 900);
    document.documentElement.style.setProperty('--s', Math.max(0.48, Math.min(1.2, scale)));
    document.documentElement.style.setProperty('--s-cover', mobileStageScale);
  };
  window.addEventListener('resize', updateScale);
  updateScale();

  // ---- 2. DOM Elements ----
  const mainNav = document.getElementById('mainNav');
  const navLogo = document.getElementById('navLogo');

  // Page 1 Elements
  const page1Scene = document.getElementById('page1Scene');
  const introCurtain = document.getElementById('introCurtain');
  const btnEnterRunway = document.getElementById('btnEnterRunway');
  const introVideo = document.getElementById('introVideo');
  const runwayContainer = document.getElementById('runwayContainer');
  const hero = document.getElementById('hero');
  const heroTitleBox = document.getElementById('heroTitleBox');
  const scrollHint = document.getElementById('scrollHint');
  const btnSkipIntro = document.getElementById('btnSkipIntro');

  // Page 2 & Lower Elements
  const page2Scene = document.getElementById('page2Scene');
  const lowerSections = document.getElementById('lowerSections');
  const cardsCanvasVideo = document.getElementById('cardsCanvasVideo');
  const cardsCanvas = document.getElementById('cardsCanvas');
  const cardsHeader = document.getElementById('cardsHeader');
  const cardsRow = document.getElementById('cardsRow');
  const cardElements = [
    document.getElementById('card0'),
    document.getElementById('card1'),
    document.getElementById('card2')
  ].filter(Boolean);

  // Modal Elements
  const detailModal = document.getElementById('detail');
  const detailBackdrop = document.getElementById('detailBackdrop');
  const detailClose = document.getElementById('detailClose');
  const detailImg = document.getElementById('detailImg');
  const detailTitle = document.getElementById('detailTitle');
  const detailText = document.getElementById('detailText');
  const detailPrize = document.getElementById('detailPrize');
  const detailPrev = document.getElementById('detailPrev');
  const detailNext = document.getElementById('detailNext');

  // Competition Data (Figma Desktop - 122)
  const competitionData = [
    {
      name: 'Glamour Nova',
      tab: 'gnm',
      image: '/static/core/assets/card-1-detail.png',
      rulebook: '/static/core/rulebooks/glamour%20nova.pdf',
      prize: 'TBA',
      text: "From the first sketch to the final click, let your creativity take centre stage. Glamour Nova takes participants on a complete fashion journey, from conceptualising and designing outfits to styling models and capturing their vision through photography. It's time to bring ideas to life, create striking visual stories, and make every frame a fashion statement."
    },
    {
      name: 'State of Dress',
      tab: 'sod',
      image: '/static/core/assets/card-2-detail.png',
      rulebook: '/static/core/rulebooks/state%20of%20dress.pdf',
      prize: 'TBA',
      text: "Who knew paper could make a fashion statement? Get ready to fold, shape, and create. State of Dress challenges participants to transform simple sheets of paper into extraordinary outfits, blending the art of origami with the magic of fashion. It's where imagination meets innovation, and every creation tells a story."
    },
    {
      name: 'Haute Couture',
      tab: 'hcd',
      image: '/static/core/assets/card-3.png',
      rulebook: '/static/core/rulebooks/haute%20couture.pdf',
      prize: 'TBA',
      text: "Where creativity meets elegance and imagination takes the form of fashion. This competition invites participants to showcase their designing skills, originality, and artistic vision through stunning outfits and captivating runway presentations. It is an opportunity to push creative boundaries, express individuality, and transform imagination into extraordinary fashion statements."
    }
  ];

  // cards scrubber setup (dynamically switches between desktop & mobile portrait frames on resize)
  let cardsScrub = null;
  let isMobileCards = null;
  function setupCardsScrubber() {
    if (!window.createFrameScrubber || !cardsCanvasVideo) return;
    const nextMobile = window.innerWidth <= 768;
    if (nextMobile === isMobileCards && cardsScrub) return;

    const prevP = cardsScrub ? cardsScrub.getProgress() : 0;
    if (cardsScrub && cardsScrub.destroy) cardsScrub.destroy();
    isMobileCards = nextMobile;

    cardsScrub = window.createFrameScrubber({
      canvas: cardsCanvasVideo,
      frameCount: isMobileCards ? 86 : 240,
      src: i => isMobileCards
        ? `/static/core/cards_mobile_frames/c_${String(i).padStart(4, '0')}.webp`
        : `/static/core/cards_frames/c_${String(i).padStart(4, '0')}.webp`,
      lerp: 0.08,
      onProgress: p => {
        onCardsScrubProgress(p);
      }
    });
    if (prevP > 0) {
      cardsScrub.setProgress(prevP);
    }
  }
  setupCardsScrubber();
  window.addEventListener('resize', setupCardsScrubber);

  // cards scrub progress
  function onCardsScrubProgress(p) {
    // 1. Virtual design canvas (desktop scales, mobile handles natively)
    if (cardsCanvas) {
      if (window.innerWidth > 768) {
        cardsCanvas.style.transform = 'scale(var(--s, 1))';
      } else {
        cardsCanvas.style.transform = 'none';
      }
    }

    // 2. Staggered Card Drop-In across animation (stays visible at end and into Page 3)
    cardElements.forEach((card, idx) => {
      const startP = 0.10 + idx * 0.18;
      const endP = startP + 0.36;
      const rawDrop = clamp((p - startP) / (endP - startP), 0, 1);
      const easedDrop = 1 - Math.pow(1 - rawDrop, 3);

      const dropStart = window.innerWidth <= 768 ? -420 : -750;
      const translateY = lerp(dropStart, 0, easedDrop);

      card.style.opacity = String(easedDrop);
      card.style.transform = `translateY(${translateY}px)`;
    });

    if (cardsHeader) {
      cardsHeader.style.display = 'none';
    }

    // 3. Navbar hidden during Page 2 animation, revealed at end of animation
    if (mainNav && currentState === 'PAGE_2') {
      if (p >= 0.96 && !isDetailOpen) {
        mainNav.classList.add('is-visible');
      } else {
        mainNav.classList.remove('is-visible');
      }
    }
  }

  // state management
  let currentState = 'CURTAIN'; // 'CURTAIN' | 'RUNWAY_PLAYING' | 'PAGE_1' | 'PAGE_2'
  let isTransitioning = false;
  let isDetailOpen = false;
  let hasVideoLanded = false;
  let unmuteHandler = null;

  // stage 1 runway video
  function nudgeEnterBtn() {
    if (!btnEnterRunway) return;
    btnEnterRunway.classList.remove('is-nudged');
    void btnEnterRunway.offsetWidth;
    btnEnterRunway.classList.add('is-nudged');
  }

  function startRunwayVideo() {
    if (currentState !== 'CURTAIN') return;
    currentState = 'RUNWAY_PLAYING';

    // Fade out black curtain
    if (introCurtain) {
      introCurtain.style.opacity = '0';
      introCurtain.style.transform = 'scale(1.05)';
      setTimeout(() => {
        introCurtain.style.display = 'none';
      }, 500);
    }

    if (btnSkipIntro) {
      btnSkipIntro.classList.add('is-visible');
    }

    // Play runway video at native 60fps with audio (fallback to muted only if browser blocks it)
    if (introVideo) {
      introVideo.muted = false;
      introVideo.volume = 1;
      if (introVideo.currentTime > 0) introVideo.currentTime = 0;
      const playPromise = introVideo.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => {
          if (hasVideoLanded || currentState !== 'RUNWAY_PLAYING') return;
          introVideo.muted = true;
          introVideo.play().catch(() => landOnHero());
          unmuteHandler = e => {
            if (btnSkipIntro && e.target && btnSkipIntro.contains(e.target)) return;
            window.removeEventListener('click', unmuteHandler);
            unmuteHandler = null;
            if (introVideo && currentState === 'RUNWAY_PLAYING' && !hasVideoLanded) {
              introVideo.muted = false;
              introVideo.volume = 1;
              const p = introVideo.play();
              if (p !== undefined) {
                p.catch(() => {
                  if (introVideo && currentState === 'RUNWAY_PLAYING' && !hasVideoLanded) {
                    introVideo.muted = true;
                    introVideo.play().catch(() => {});
                  }
                });
              }
            }
          };
          window.addEventListener('click', unmuteHandler);
        });
      }

      introVideo.ontimeupdate = () => {
        if (hasVideoLanded) return;
        if (introVideo.currentTime >= 8.0) {
          landOnHero();
        }
      };

      introVideo.onended = () => {
        if (!hasVideoLanded) landOnHero();
      };
    }
  }

  function landOnHero() {
    if (hasVideoLanded) return;
    hasVideoLanded = true;
    currentState = 'PAGE_1';

    if (unmuteHandler) {
      window.removeEventListener('click', unmuteHandler);
      unmuteHandler = null;
    }

    if (introVideo) {
      introVideo.muted = true;
    }

    if (btnSkipIntro) {
      btnSkipIntro.classList.remove('is-visible');
    }

    // Flare up "The Runway is calling you"
    if (runwayContainer) {
      runwayContainer.style.opacity = '1';
      runwayContainer.style.transform = 'scale(1.04) translateY(0)';
    }

    setTimeout(() => {
      if (runwayContainer) {
        runwayContainer.style.opacity = '0';
        runwayContainer.style.transform = 'scale(1.08) translateY(-20px)';
      }

      // Reveal Page 1 Hero Stage
      if (hero) {
        hero.classList.add('is-active');
      }

      // Reveal Top Navigation
      if (mainNav) {
        mainNav.classList.add('is-visible');
      }

      // Hide intro video
      if (introVideo) {
        introVideo.style.opacity = '0';
        setTimeout(() => introVideo.pause(), 600);
      }
    }, 1200);
  }

  if (btnSkipIntro) {
    btnSkipIntro.addEventListener('click', e => {
      e.stopPropagation();
      landOnHero();
    });
  }

  // page transitions
  function syncPage2WithLowerScroll() {
    if (!page2Scene || !lowerSections) return;
    const offset = Math.min(lowerSections.scrollTop, window.innerHeight);
    page2Scene.style.transition = 'none';
    page2Scene.style.transform = offset > 0 ? `translateY(${-offset}px)` : '';
  }

  function resetPage2ScrollTransform() {
    if (!page2Scene) return;
    page2Scene.style.transition = '';
    page2Scene.style.transform = '';
  }

  function goToPage2(targetProgress = null, openModalIndex = null) {
    if (lowerSections) {
      lowerSections.classList.remove('is-active');
      lowerSections.scrollTop = 0;
    }
    resetPage2ScrollTransform();
    if (currentState !== 'PAGE_2') {
      currentState = 'PAGE_2';

      // Navbar disappears during animation in Page 2
      if (mainNav) {
        mainNav.classList.remove('is-visible');
      }

      // Page 1 animates out
      if (page1Scene) {
        page1Scene.classList.add('is-exited');
      }

      // Page 2 animates in
      if (page2Scene) {
        page2Scene.classList.add('is-active');
      }
    }

    if (cardsScrub && targetProgress !== null) {
      cardsScrub.setProgress(targetProgress);
    }

    if (openModalIndex !== null) {
      setTimeout(() => openDetail(openModalIndex), 350);
    }
  }

  function goToPage1() {
    if (currentState === 'PAGE_1') return;
    currentState = 'PAGE_1';

    if (isDetailOpen) closeDetail();
    if (lowerSections) {
      lowerSections.classList.remove('is-active');
      lowerSections.scrollTop = 0;
    }
    resetPage2ScrollTransform();

    // Reveal Navbar on Page 1 Hero
    if (mainNav) {
      mainNav.classList.add('is-visible');
    }

    // Page 2 animates out
    if (page2Scene) {
      page2Scene.classList.remove('is-active');
    }

    // Page 1 animates in
    if (page1Scene) {
      page1Scene.classList.remove('is-exited');
    }

    if (cardsScrub) {
      cardsScrub.reset();
    }
  }

  function goToLowerSections(targetSelector = null, initialDelta = 0) {
    if (isDetailOpen) closeDetail();
    currentState = 'LOWER_PAGE';

    if (mainNav) {
      mainNav.classList.add('is-visible');
    }
    if (page1Scene) {
      page1Scene.classList.add('is-exited');
    }
    if (page2Scene) {
      page2Scene.classList.add('is-active');
    }
    if (cardsScrub) {
      cardsScrub.setProgress(1);
    }
    if (lowerSections) {
      lowerSections.classList.add('is-active');
      if (targetSelector) {
        const el = lowerSections.querySelector(targetSelector);
        if (el) {
          setTimeout(() => el.scrollIntoView({ behavior: 'smooth' }), 60);
        }
      } else if (initialDelta > 0) {
        lowerSections.scrollTop = Math.max(1, initialDelta);
        syncPage2WithLowerScroll();
      } else {
        lowerSections.scrollTo({ top: window.innerHeight, behavior: 'smooth' });
      }
    }
  }

  function backFromLowerToPage2() {
    if (currentState !== 'LOWER_PAGE') return;
    currentState = 'PAGE_2';
    if (lowerSections) {
      lowerSections.classList.remove('is-active');
      lowerSections.scrollTop = 0;
    }
    resetPage2ScrollTransform();
    if (cardsScrub) {
      cardsScrub.setProgress(1);
    }
    if (mainNav && !isDetailOpen) {
      mainNav.classList.add('is-visible');
    }
  }

  if (lowerSections) {
    lowerSections.addEventListener('scroll', () => {
      if (currentState !== 'LOWER_PAGE') return;
      syncPage2WithLowerScroll();
      if (lowerSections.scrollTop <= 0) {
        backFromLowerToPage2();
      }
    }, { passive: true });
  }

  // wheel & scroll interceptor
  window.addEventListener('wheel', e => {
    if (currentState === 'LOWER_PAGE') {
      if (lowerSections && lowerSections.scrollTop <= 2 && e.deltaY < -5) {
        e.preventDefault();
        backFromLowerToPage2();
      }
      return;
    }

    e.preventDefault();
    if (isDetailOpen) return;

    if (currentState === 'CURTAIN') {
      nudgeEnterBtn();
      return;
    }

    if (currentState === 'RUNWAY_PLAYING') {
      return;
    }

    if (currentState === 'PAGE_1') {
      if (e.deltaY > 5) {
        goToPage2(0);
        if (cardsScrub) {
          const clamped = Math.min(e.deltaY, 80);
          cardsScrub.addDelta(clamped / 2400);
        }
      }
      return;
    }

    if (currentState === 'PAGE_2') {
      if (!cardsScrub) return;

      const p = cardsScrub.getProgress();

      // If at start of Page 2 (p <= 0.02) and user scrolls up -> return to Page 1 Hero!
      if (p <= 0.02 && e.deltaY < 0) {
        goToPage1();
        return;
      }

      // If at end of Page 2 (p >= 0.99) and user scrolls down -> smoothly move Page 3 up over locked Page 2
      if (p >= 0.99 && e.deltaY > 2) {
        goToLowerSections(null, e.deltaY);
        return;
      }

      // Symmetrical smooth scroll scrubbing for forward and backward
      const clampedDelta = Math.sign(e.deltaY) * Math.min(Math.abs(e.deltaY), 80);
      const scrubDelta = clampedDelta / 2400;
      cardsScrub.addDelta(scrubDelta);
    }
  }, { passive: false });

  // Touch handling
  let touchStartY = 0;
  window.addEventListener('touchstart', e => {
    if (e.touches.length) touchStartY = e.touches[0].clientY;
  }, { passive: true });

  window.addEventListener('touchmove', e => {
    if (isDetailOpen || !e.touches.length) return;
    const y = e.touches[0].clientY;
    const deltaY = touchStartY - y;
    touchStartY = y;

    if (currentState === 'LOWER_PAGE') {
      if (lowerSections && lowerSections.scrollTop <= 2 && deltaY < -15) {
        backFromLowerToPage2();
      }
      return;
    }

    if (currentState === 'CURTAIN') {
      nudgeEnterBtn();
      return;
    }

    if (currentState === 'RUNWAY_PLAYING') {
      return;
    }

    if (currentState === 'PAGE_1') {
      if (deltaY > 5) {
        goToPage2(0);
        if (cardsScrub) {
          cardsScrub.addDelta(Math.min(deltaY, 60) / 1600);
        }
      }
      return;
    }

    if (currentState === 'PAGE_2' && cardsScrub) {
      const p = cardsScrub.getProgress();
      if (p <= 0.02 && deltaY < 0) {
        goToPage1();
        return;
      }
      if (p >= 0.99 && deltaY > 2) {
        goToLowerSections(null, deltaY);
        return;
      }

      const clampedTouch = Math.sign(deltaY) * Math.min(Math.abs(deltaY), 60);
      cardsScrub.addDelta(clampedTouch / 1600);
    }
  }, { passive: false });

  // Keyboard navigation
  window.addEventListener('keydown', e => {
    if (e.repeat) return;
    if (isDetailOpen) {
      if (e.key === 'Escape') closeDetail();
      if (e.key === 'ArrowLeft') showCompetition(currentCardIndex - 1);
      if (e.key === 'ArrowRight') showCompetition(currentCardIndex + 1);
      return;
    }

    // ENTER key skips intro video or advances
    if (e.key === 'Enter') {
      e.preventDefault();
      if (currentState === 'CURTAIN') startRunwayVideo();
      else if (currentState === 'RUNWAY_PLAYING') landOnHero();
      else if (currentState === 'PAGE_1') goToPage2(1);
      return;
    }

    if (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ') {
      e.preventDefault();
      if (currentState === 'CURTAIN') startRunwayVideo();
      else if (currentState === 'RUNWAY_PLAYING') landOnHero();
      else if (currentState === 'PAGE_1') goToPage2(0.08);
      else if (currentState === 'PAGE_2' && cardsScrub) cardsScrub.addDelta(0.12);
    } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
      e.preventDefault();
      if (currentState === 'PAGE_2' && cardsScrub) {
        const p = cardsScrub.getProgress();
        if (p <= 0.05) goToPage1();
        else cardsScrub.addDelta(-0.12);
      }
    }
  });

  // Clicking Enter button or curtain starts video with audio
  if (btnEnterRunway) {
    btnEnterRunway.addEventListener('click', e => {
      e.stopPropagation();
      startRunwayVideo();
    });
  }
  if (introCurtain) {
    introCurtain.addEventListener('click', e => {
      e.stopPropagation();
      startRunwayVideo();
    });
  }

  // Scroll hint on Hero stage clicks straight to Page 2
  if (scrollHint) {
    scrollHint.addEventListener('click', e => {
      e.stopPropagation();
      goToPage2(1);
    });
  }

  // Nav buttons
  document.querySelectorAll('.nav__link-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const text = (btn.textContent || '').trim().toUpperCase();
      if (text === 'ABOUT' || text === 'EVENTS') {
        goToPage2(1);
      } else if (text === 'GLIMPSES') {
        goToLowerSections();
      } else if (text === 'FAQ') {
        goToLowerSections('#faq-section');
      } else if (text === 'CONTACT') {
        goToLowerSections('#main-footer');
      } else if (text === 'RULEBOOK') {
        goToPage2(1, 0); // Open Glamour Nova with rulebook
      }
    });
  });

  // Footer navigation links inside contact section
  const footerAboutLink = document.getElementById('footerAboutLink');
  if (footerAboutLink) {
    footerAboutLink.addEventListener('click', e => {
      e.preventDefault();
      goToPage2(1);
    });
  }
  const footerGlimpsesLink = document.getElementById('footerGlimpsesLink');
  if (footerGlimpsesLink) {
    footerGlimpsesLink.addEventListener('click', e => {
      e.preventDefault();
      if (lowerSections) lowerSections.scrollTo({ top: window.innerHeight, behavior: 'smooth' });
    });
  }

  if (navLogo) {
    navLogo.addEventListener('click', e => {
      e.preventDefault();
      goToPage1();
    });
  }

  // mobile hamburger toggle
  const navHamburger = document.getElementById('navHamburger');
  if (navHamburger && mainNav) {
    navHamburger.addEventListener('click', e => {
      e.stopPropagation();
      const isOpen = mainNav.classList.toggle('is-menu-open');
      navHamburger.setAttribute('aria-expanded', String(isOpen));
    });

    document.querySelectorAll('.nav__links button, .nav__links a').forEach(el => {
      el.addEventListener('click', () => {
        mainNav.classList.remove('is-menu-open');
        navHamburger.setAttribute('aria-expanded', 'false');
      });
    });

    document.addEventListener('click', e => {
      if (!mainNav.contains(e.target)) {
        mainNav.classList.remove('is-menu-open');
        navHamburger.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // hero spotlights hover (desktop) + tap toggle (mobile/touch)
  if (heroTitleBox && hero) {
    heroTitleBox.addEventListener('mouseenter', () => {
      hero.classList.add('is-lit');
    });

    heroTitleBox.addEventListener('mouseleave', () => {
      hero.classList.remove('is-lit');
    });

    heroTitleBox.addEventListener('click', (e) => {
      if (window.matchMedia('(hover: none)').matches || window.innerWidth <= 768) {
        e.stopPropagation();
        hero.classList.toggle('is-lit');
      }
    });

    hero.addEventListener('click', (e) => {
      if ((window.matchMedia('(hover: none)').matches || window.innerWidth <= 768) && !heroTitleBox.contains(e.target)) {
        hero.classList.remove('is-lit');
      }
    });
  }

  // detail modal controller
  let currentCardIndex = 0;

  function showCompetition(index) {
    currentCardIndex = (index + competitionData.length) % competitionData.length;
    const data = competitionData[currentCardIndex];

    if (detailImg) detailImg.src = data.image;
    if (detailTitle) detailTitle.textContent = data.name;
    if (detailText) detailText.textContent = data.text;
    if (detailPrize) detailPrize.textContent = data.prize;

    const detailRegBtn = document.querySelector('.btn-register--detail');
    if (detailRegBtn && data.tab) {
      detailRegBtn.setAttribute('href', `/forms/?tab=${data.tab}`);
    }
    const detailRulebook = document.getElementById('detailRulebook');
    if (detailRulebook && data.rulebook) {
      detailRulebook.setAttribute('href', data.rulebook);
    }
  }

  function openDetail(index) {
    showCompetition(index);
    if (detailModal) {
      detailModal.classList.add('is-open');
      detailModal.setAttribute('aria-hidden', 'false');
      isDetailOpen = true;
    }
    if (mainNav) {
      mainNav.classList.remove('is-visible');
    }
  }

  function closeDetail() {
    if (detailModal) {
      detailModal.classList.remove('is-open');
      detailModal.setAttribute('aria-hidden', 'true');
      isDetailOpen = false;
    }
    if (mainNav) {
      const animDone = currentState === 'PAGE_1'
        || currentState === 'LOWER_PAGE'
        || (currentState === 'PAGE_2' && cardsScrub && cardsScrub.getEasedProgress() >= 0.96);
      if (animDone) mainNav.classList.add('is-visible');
    }
  }

  cardElements.forEach((card, index) => {
    card.addEventListener('click', e => {
      e.stopPropagation();
      openDetail(index);
    });
  });

  if (detailClose) detailClose.addEventListener('click', closeDetail);
  if (detailBackdrop) detailBackdrop.addEventListener('click', closeDetail);
  if (detailPrev) detailPrev.addEventListener('click', () => showCompetition(currentCardIndex - 1));
  if (detailNext) detailNext.addEventListener('click', () => showCompetition(currentCardIndex + 1));

  // modal mobile swipe
  let modalTouchStartX = 0;
  if (detailModal) {
    detailModal.addEventListener('touchstart', e => {
      if (e.touches.length) modalTouchStartX = e.touches[0].clientX;
    }, { passive: true });

    detailModal.addEventListener('touchend', e => {
      if (!e.changedTouches.length) return;
      const diffX = e.changedTouches[0].clientX - modalTouchStartX;
      if (diffX > 45) {
        showCompetition(currentCardIndex - 1);
      } else if (diffX < -45) {
        showCompetition(currentCardIndex + 1);
      }
    }, { passive: true });
  }

  // hero slider track with SVG pill drag & click animation
  const heroSlider = document.querySelector('.btn-register--lg');
  if (heroSlider) {
    const pill = heroSlider.querySelector('.btn-register__pill');
    let isDragging = false;
    let didDrag = false;
    let startX = 0;
    let initialLeft = 6;
    const minSlide = 6;

    const getMaxSlide = () => {
      if (!pill) return 111;
      return Math.max(minSlide, heroSlider.clientWidth - pill.offsetWidth - 6);
    };

    const completeSlide = () => {
      if (heroSlider.classList.contains('is-sliding')) return;
      isDragging = false;
      heroSlider.classList.add('is-sliding');
      if (pill) {
        pill.style.transition = 'left 0.65s cubic-bezier(0.22, 1, 0.36, 1), transform 0.25s ease';
        pill.style.left = getMaxSlide() + 'px';
      }
      const targetUrl = heroSlider.getAttribute('href') || '/registration/';
      setTimeout(() => { window.location.href = targetUrl; }, 720);
    };

    const springBack = () => {
      if (!pill) return;
      pill.style.transition = 'left 0.45s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.25s ease';
      pill.style.left = minSlide + 'px';
    };

    const onStart = (clientX) => {
      if (heroSlider.classList.contains('is-sliding') || !pill) return;
      isDragging = true;
      didDrag = false;
      startX = clientX;
      initialLeft = parseFloat(getComputedStyle(pill).left) || minSlide;
      pill.style.transition = 'none';
    };

    const onMove = (clientX) => {
      if (!isDragging || !pill) return;
      const dx = clientX - startX;
      if (Math.abs(dx) > 4) didDrag = true;
      const maxSlide = getMaxSlide();
      const newLeft = Math.max(minSlide, Math.min(maxSlide, initialLeft + dx));
      pill.style.left = newLeft + 'px';
      if (newLeft >= maxSlide - 8) completeSlide();
    };

    const onEnd = () => {
      if (!isDragging) return;
      isDragging = false;
      if (!pill) return;
      const maxSlide = getMaxSlide();
      const currentLeft = parseFloat(pill.style.left) || minSlide;
      if (currentLeft >= minSlide + (maxSlide - minSlide) * 0.55) {
        completeSlide();
      } else if (didDrag) {
        springBack();
      }
    };

    heroSlider.addEventListener('click', (e) => {
      e.preventDefault();
      if (didDrag) {
        didDrag = false;
        return;
      }
      completeSlide();
    });

    if (pill) {
      pill.addEventListener('mousedown', (e) => {
        e.preventDefault();
        onStart(e.clientX);
        const onMouseMove = (ev) => onMove(ev.clientX);
        const onMouseUp = () => {
          onEnd();
          window.removeEventListener('mousemove', onMouseMove);
          window.removeEventListener('mouseup', onMouseUp);
        };
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
      });

      pill.addEventListener('touchstart', (e) => {
        if (e.touches.length > 0) onStart(e.touches[0].clientX);
      }, { passive: true });

      pill.addEventListener('touchmove', (e) => {
        if (e.touches.length > 0) onMove(e.touches[0].clientX);
      }, { passive: true });

      pill.addEventListener('touchend', () => onEnd());
    }
  }

  // Handle other register buttons (navbar + detail SVG buttons)
  document.querySelectorAll('.btn-register--sm, .btn-register--detail').forEach(btn => {
    btn.addEventListener('click', e => {
      if (btn.classList.contains('is-sliding')) return;
      const targetUrl = btn.getAttribute('href');
      if (targetUrl && targetUrl !== '#' && !targetUrl.startsWith('javascript:')) {
        e.preventDefault();
        btn.classList.add('is-sliding');
        setTimeout(() => { window.location.href = targetUrl; }, 380);
      }
    });
  });

  // Reset slider & register buttons when returning via browser Back (bfcache)
  window.addEventListener('pageshow', () => {
    if (heroSlider) {
      heroSlider.classList.remove('is-sliding');
      const pill = heroSlider.querySelector('.btn-register__pill');
      if (pill) {
        pill.style.transition = 'none';
        pill.style.left = '';
      }
    }
    document.querySelectorAll('.btn-register').forEach(btn => btn.classList.remove('is-sliding'));
  });
})();
//gowtham-end

// Dipank-Glimpses and footer Start
// gsap

 function fitBrandText() {
    const el = document.getElementById('footer-brand-text');
    if (!el) return;

    const targetW = document.documentElement.clientWidth;

    const probe = document.createElement('span');
    probe.style.cssText = [
        "font-family:'Palace Script MT','Palace Script',cursive",
        "white-space:nowrap",
        "position:fixed",
        "top:-9999px",
        "left:-9999px",
        "visibility:hidden",
        "line-height:1",
        "letter-spacing:0px"
    ].join(';');
    probe.textContent = 'Vogue Nation';
    document.body.appendChild(probe);

    let lo = 50, hi = 4000;
    for (let i = 0; i < 25; i++) {
        const mid = (lo + hi) >> 1;
        probe.style.fontSize = mid + 'px';
        (probe.getBoundingClientRect().width <= targetW) ? lo = mid : hi = mid;
    }

    document.body.removeChild(probe);

    el.style.fontSize   = lo + 'px';
    el.style.visibility = 'visible';
}

document.fonts.ready.then(fitBrandText);
window.addEventListener('resize', () => document.fonts.ready.then(fitBrandText));

document.addEventListener("DOMContentLoaded", () => {
    const track    = document.querySelector('.carousel-track');
    const images   = document.querySelectorAll('.carousel-img');
    const viewport = document.querySelector('.carousel-viewport');
    if (!track || !viewport) return;

    const imgWidth       = 320, gap = 12;
    const itemSpacing    = imgWidth + gap;
    const singleSetWidth = 5 * itemSpacing;
    let scrollPos = 0, isDragging = false, startX = 0, startScroll = 0;
    let hoveredIdx = -1;
    const hoverScales = Array.from(images, () => 1);

    images.forEach((img, i) => {
        img.addEventListener('mouseenter', () => { hoveredIdx = i; });
        img.addEventListener('mouseleave', () => { if (hoveredIdx === i) hoveredIdx = -1; });
    });

    function render() {
        const trackX = -(scrollPos % singleSetWidth);
        track.style.transform = `translateX(${trackX}px)`;
        const vc = window.innerWidth / 2;
        const P = 1050;
        const visualGap = 60;

        const meta = [];
        let centerIdx = 0;
        let minAbsD = Infinity;

        images.forEach((img, i) => {
            const c = trackX + i * itemSpacing + imgWidth / 2;
            const d = c - vc;
            const norm = Math.max(-1.25, Math.min(1.25, d / vc));
            const absNorm = Math.abs(norm);

            const scale = 0.76 + Math.pow(absNorm, 1.25) * 0.26;
            const rotateY = -norm * 34;
            const theta = rotateY * Math.PI / 180;

            const halfBase = (imgWidth / 2) * scale;
            const hCos = halfBase * Math.cos(theta);
            const hSin = halfBase * Math.sin(theta);

            const kL = P / (P - hSin);
            const kR = P / (P + hSin);

            if (Math.abs(d) < minAbsD) {
                minAbsD = Math.abs(d);
                centerIdx = i;
            }
            meta.push({ c, d, absNorm, scale, rotateY, hCos, kL, kR });
        });

        const screenL = (m, X) => vc + (X - m.hCos) * m.kL;
        const screenR = (m, X) => vc + (X + m.hCos) * m.kR;

        const X = new Array(images.length);
        const neighborIdx = meta[centerIdx].d >= 0
            ? Math.max(0, centerIdx - 1)
            : Math.min(images.length - 1, centerIdx + 1);
        const pairWidth = meta[centerIdx].hCos + meta[neighborIdx].hCos + visualGap;
        X[centerIdx] = meta[centerIdx].d * (pairWidth / itemSpacing);

        for (let i = centerIdx + 1; i < images.length; i++) {
            const targetL = screenR(meta[i - 1], X[i - 1]) + visualGap;
            X[i] = meta[i].hCos + (targetL - vc) / meta[i].kL;
        }
        for (let i = centerIdx - 1; i >= 0; i--) {
            const targetR = screenL(meta[i + 1], X[i + 1]) - visualGap;
            X[i] = -meta[i].hCos + (targetR - vc) / meta[i].kR;
        }

        images.forEach((img, i) => {
            const m = meta[i];
            const sx = (vc + X[i]) - m.c;
            const targetHover = (i === hoveredIdx && !isDragging) ? 1.06 : 1;
            hoverScales[i] += (targetHover - hoverScales[i]) * 0.14;

            img.style.transform       = `translateX(${sx}px) rotateY(${m.rotateY}deg) scale(${m.scale * hoverScales[i]})`;
            img.style.transformOrigin = "center center";
            img.style.zIndex          = (i === hoveredIdx) ? 20 : Math.round(m.absNorm * 10);
        });
    }

    function tick() {
        if (!isDragging) scrollPos += 1.0;
        render();
        requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);

    viewport.addEventListener('wheel', e => {
        if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
            e.preventDefault();
            scrollPos += e.deltaX * 0.8;
            if (scrollPos < 0) scrollPos += singleSetWidth * 10;
            render();
        }
    }, { passive: false });

    track.addEventListener('mousedown', e => {
        isDragging = true; startX = e.clientX; startScroll = scrollPos;
        track.style.cursor = 'grabbing';
    });
    window.addEventListener('mousemove', e => {
        if (!isDragging) return;
        scrollPos = startScroll - (e.clientX - startX) * 1.2;
        if (scrollPos < 0) scrollPos += singleSetWidth * 10;
        render();
    });
    window.addEventListener('mouseup', () => { isDragging = false; track.style.cursor = 'grab'; });

    track.addEventListener('touchstart', e => {
        isDragging = true; startX = e.touches[0].clientX; startScroll = scrollPos;
    }, { passive: true });
    window.addEventListener('touchmove', e => {
        if (!isDragging) return;
        scrollPos = startScroll - (e.touches[0].clientX - startX) * 1.2;
        if (scrollPos < 0) scrollPos += singleSetWidth * 10;
        render();
    }, { passive: true });
    window.addEventListener('touchend', () => { isDragging = false; });
    window.addEventListener('resize', render);
});

/* ── Mobile Stacked Cards ── */
document.addEventListener("DOMContentLoaded", () => {
    const stack = document.getElementById("mobile-card-stack");
    if (!stack) return;
    const cards = Array.from(stack.querySelectorAll(".mobile-card"));
    if (!cards.length) return;

    const restAngles = [-2, -5, -8, -11, -14];
    let order = cards.map((_, i) => i);
    let isAnimating = false;

    function layoutCards(animate) {
        order.forEach((cardIdx, pos) => {
            const card = cards[cardIdx];
            const angle = restAngles[pos % restAngles.length];
            const scale = 1 - pos * 0.015;
            const yOff  = pos * 3;
            card.style.zIndex = cards.length - pos;
            if (animate) {
                gsap.to(card, {
                    rotation: angle,
                    scale: scale,
                    y: yOff,
                    x: 0,
                    opacity: 1,
                    duration: 0.42,
                    ease: "power3.out"
                });
            } else {
                gsap.set(card, { rotation: angle, scale: scale, y: yOff, x: 0, opacity: 1 });
            }
        });
    }

    layoutCards(false);

    stack.addEventListener("click", () => {
        if (isAnimating) return;
        isAnimating = true;
        const topCard = cards[order[0]];

        gsap.to(topCard, {
            y: -48,
            scale: 1.07,
            rotation: -6,
            opacity: 0.85,
            duration: 0.22,
            ease: "power2.out",
            onComplete: () => {
                order.push(order.shift());
                layoutCards(true);
                setTimeout(() => { isAnimating = false; }, 380);
            }
        });
    });
});

/* ── FAQ ── */
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".faq-item").forEach(item => {
        const btn   = item.querySelector(".faq-item-btn");
        const panel = item.querySelector(".faq-item-panel");
        const arrow = item.querySelector(".faq-arrow");
        const inner = item.querySelector(".faq-item-inner");
        if (!btn || !panel || !arrow || !inner) return;
        let open = false;
        const apply = o => {
            item.style.background  = o ? "linear-gradient(to left,#d4af37,white)" : "linear-gradient(to left,#644E0C,#353535)";
            inner.style.background = o ? "linear-gradient(to bottom right,#292929,#303030)" : "#000";
            arrow.style.transform  = o ? "rotate(180deg)" : "rotate(0deg)";
            btn.setAttribute("aria-expanded", String(o));
        };
        apply(false);
        btn.addEventListener("click", () => { open = !open; panel.style.gridTemplateRows = open ? "1fr" : "0fr"; apply(open); });
    });
});

// lights (Smooth Scroll + Mouse Parallax)
document.addEventListener("DOMContentLoaded", () => {
  const wrap = document.getElementById("faq-footer-wrap");
  const lower = document.getElementById("lowerSections");
  const lightTopRight = document.getElementById("light-top-right");
  const lightBottomLeft = document.getElementById("light-bottom-left");
  if (!wrap || !lightTopRight || !lightBottomLeft) return;

  let mouseX = 0;
  let mouseY = 0;

  function updateLightsParallax() {
    const rect = wrap.getBoundingClientRect();
    const vh = window.innerHeight || document.documentElement.clientHeight;
    if (!rect.height) return;

    // Full 0 -> 1 progress from top of FAQ to bottom of Footer
    const scrollable = Math.max(1, rect.height - vh);
    const p = Math.min(1.2, Math.max(-0.2, -rect.top / scrollable));
    const centered = p - 0.5; // -0.5 at FAQ top, +0.5 at Footer bottom

    const topRightX = centered * -180 + mouseX * -35;
    const topRightY = centered * 520 + mouseY * -35;

    const bottomLeftX = (1 - p) * 140 + mouseX * 35;
    const bottomLeftY = (p - 1) * 480 + mouseY * 35;

    if (window.gsap) {
      gsap.to(lightTopRight, {
        x: topRightX,
        y: topRightY,
        scale: 1 + Math.abs(centered) * 0.12,
        duration: 0.75,
        ease: "power2.out",
        overwrite: "auto"
      });
      gsap.to(lightBottomLeft, {
        x: bottomLeftX,
        y: bottomLeftY,
        scale: 1 + Math.abs(centered) * 0.12,
        duration: 0.75,
        ease: "power2.out",
        overwrite: "auto"
      });
    } else {
      lightTopRight.style.transform = `translate3d(${topRightX}px, ${topRightY}px, 0)`;
      lightBottomLeft.style.transform = `translate3d(${bottomLeftX}px, ${bottomLeftY}px, 0)`;
    }
  }

  if (lower) {
    lower.addEventListener("scroll", updateLightsParallax, { passive: true });
  }
  window.addEventListener("scroll", updateLightsParallax, { passive: true, capture: true });
  window.addEventListener("resize", updateLightsParallax, { passive: true });

  // Subtle mouse-depth parallax on desktop
  window.addEventListener("mousemove", (e) => {
    mouseX = (e.clientX / window.innerWidth) - 0.5;
    mouseY = (e.clientY / window.innerHeight) - 0.5;
    updateLightsParallax();
  }, { passive: true });

  // Sync immediately when nav buttons jump to FAQ/Contact
  document.addEventListener("click", () => {
    setTimeout(updateLightsParallax, 200);
    setTimeout(updateLightsParallax, 600);
  });

  updateLightsParallax();
});
/* ── Team Webops Popup ── */
function bindTeamPopup(triggerId, popupId) {
  const trigger = document.getElementById(triggerId);
  const popup = document.getElementById(popupId);
  if (!trigger || !popup) return;

  trigger.addEventListener("mouseenter", () => {
    popup.style.display = "flex";
  });
  trigger.addEventListener("mouseleave", () => {
    popup.style.display = "none";
  });
  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    popup.style.display = popup.style.display === "flex" ? "none" : "flex";
  });
}



bindTeamPopup("creatives-trigger", "creatives-popup");
bindTeamPopup("webops-trigger", "webops-popup");

/* ── Footer Vogue Nation Writing Animation ── */

document.addEventListener("DOMContentLoaded", () => {
  const brandText = document.getElementById("footer-brand-text");
  const lower = document.getElementById("lowerSections");
  if (!brandText) return;

  let revealed = false;

  function checkBrandReveal() {
    const rect = brandText.getBoundingClientRect();
    const vh = window.innerHeight || document.documentElement.clientHeight;
    const isVisible = rect.height > 0 && rect.top < vh * 0.95 && rect.bottom > 0;

    if (isVisible && !revealed) {
      revealed = true;
      brandText.style.transition = "clip-path 2.4s cubic-bezier(0.22, 1, 0.36, 1)";
      brandText.style.clipPath = "inset(0 0% 0 0)";
    } else if ((rect.height === 0 || rect.top >= vh) && revealed) {
      revealed = false;
      brandText.style.transition = "none";
      brandText.style.clipPath = "inset(0 100% 0 0)";
      void brandText.offsetWidth; // force reflow before restoring transition
      brandText.style.transition = "clip-path 2.4s cubic-bezier(0.22, 1, 0.36, 1)";
    }
  }

  if (lower) {
    lower.addEventListener("scroll", checkBrandReveal, { passive: true });
  }
  window.addEventListener("scroll", checkBrandReveal, { passive: true, capture: true });

  document.addEventListener("click", () => {
    setTimeout(checkBrandReveal, 350);
    setTimeout(checkBrandReveal, 800);
  });

  checkBrandReveal();
});
// Dipank's End