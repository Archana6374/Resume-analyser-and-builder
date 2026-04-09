document.addEventListener('DOMContentLoaded', () => {
  const portal = document.querySelector('.resume-portal');
  if (!portal) return;

  const previewPanel = document.getElementById('preview-panel');
  const exportPanel = document.getElementById('export-panel');
  const templatePanel = document.getElementById('template-panel');
  const scoreWidget = document.getElementById('score-widget');

  if (previewPanel) previewPanel.classList.add('hidden');
  if (exportPanel) exportPanel.classList.add('hidden');

  const revealBuilderPanels = () => {
    templatePanel?.classList.remove('hidden');
  };

  ['card-builder', 'card-analyzer', 'card-ats'].forEach((id) => {
    const card = document.getElementById(id);
    card?.addEventListener('click', () => {
      if (id === 'card-builder') {
        window.location.href = '/builder/';
      } else if (id === 'card-analyzer') {
        window.location.href = '/analysis/';
      } else if (id === 'card-ats') {
        window.location.href = '/score/';
      }
    });
  });

  document.querySelectorAll('.top-nav a, .app-nav .nav-link').forEach((link) => {
    link.addEventListener('click', (event) => {
      const href = link.getAttribute('href');
      const target = link.dataset.target;

      // Skip full page redirects (analysis/score) so they can still navigate normally.
      if (href === '/analysis/' || href === '/score/') {
        return;
      }

      event.preventDefault();
      const selectedTarget = target || (href && href.startsWith('/#') ? href.substring(2) : null);

      if (selectedTarget === 'builder-section') {
        setTimeout(revealBuilderPanels, 60);
      }
      if (selectedTarget && typeof setVisible === 'function') {
        setVisible(selectedTarget);
      }
    });
  });

  ['generate', 'render-template'].forEach((id) => {
    const button = document.getElementById(id);
    button?.addEventListener('click', () => {
      revealBuilderPanels();
      previewPanel?.classList.remove('hidden');
      exportPanel?.classList.remove('hidden');

      setTimeout(() => {
        previewPanel?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 120);
    });
  });

  document.getElementById('generate-score')?.addEventListener('click', () => {
    scoreWidget?.classList.remove('hidden');
  });
});