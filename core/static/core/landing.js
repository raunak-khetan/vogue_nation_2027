//gowtham-start
// Vogue Nation - Alcheringa 2027

(() => {
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
      prize: '50k',
      text: "From the first sketch to the final click, let your creativity take centre stage. Glamour Nova takes participants on a complete fashion journey, from conceptualising and designing outfits to styling models and capturing their vision through photography. It's time to bring ideas to life, create striking visual stories, and make every frame a fashion statement."
    },
    {
      name: 'State of Dress',
      tab: 'sod',
      image: '/static/core/assets/card-2-detail.png',
      rulebook: '/static/core/rulebooks/state%20of%20dress.pdf',
      prize: '50k',
      text: "Who knew paper could make a fashion statement? Get ready to fold, shape, and create. State of Dress challenges participants to transform simple sheets of paper into extraordinary outfits, blending the art of origami with the magic of fashion. It's where imagination meets innovation, and every creation tells a story."
    },
    {
      name: 'Haute Couture',
      tab: 'hcd',
      image: '/static/core/assets/card-3.png',
      rulebook: '/static/core/rulebooks/haute%20couture.pdf',
      prize: '50k',
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
