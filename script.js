document.addEventListener('DOMContentLoaded', () => {
  const body = document.body;
  const header = document.querySelector('.site-header');
  const navLinks = Array.from(document.querySelectorAll('.site-nav a[href^="#"]'));
  const sections = navLinks
    .map((link) => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);

  const revealItems = Array.from(document.querySelectorAll('.feature-card, .panel, .artifact-card, .risk-card, .timeline-item, .proof-card'));

  const setActiveNav = () => {
    const offset = (header?.offsetHeight || 0) + 120;
    let currentId = '';

    sections.forEach((section) => {
      if (window.scrollY + offset >= section.offsetTop) {
        currentId = section.id;
      }
    });

    navLinks.forEach((link) => {
      const isActive = currentId && link.getAttribute('href') === `#${currentId}`;
      link.classList.toggle('is-active', isActive);
    });
  };

  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.14, rootMargin: '0px 0px -40px 0px' }
  );

  revealItems.forEach((item, index) => {
    item.classList.add('reveal');
    item.style.setProperty('--reveal-delay', `${Math.min(index % 4, 3) * 55}ms`);
    revealObserver.observe(item);
  });

  navLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      const target = document.querySelector(link.getAttribute('href'));
      if (!target) return;
      event.preventDefault();
      const top = target.getBoundingClientRect().top + window.scrollY - ((header?.offsetHeight || 0) + 18);
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  window.addEventListener('scroll', () => {
    body.classList.toggle('scrolled', window.scrollY > 20);
    setActiveNav();
  }, { passive: true });

  setActiveNav();
  body.classList.toggle('scrolled', window.scrollY > 20);
});
