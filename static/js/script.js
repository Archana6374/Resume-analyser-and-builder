(function () {
  if (window.__resumeBuilderScriptRunning) {
    return;
  }
  window.__resumeBuilderScriptRunning = true;

  const templateCatalog = {
    classic: {
      name: 'Classic',
      label: 'Classic (ATS-friendly)',
      description: 'Clean single-column structure with traditional section flow.',
      palettes: ['#0f4c81', '#2f6b2f', '#7c3aed', '#b45309'],
      category: 'ats',
      badge: 'Recommended'
    },
    modern: {
      name: 'Modern',
      label: 'Modern Professional',
      description: 'Balanced split layout with polished cards and a professional accent.',
      palettes: ['#2563eb', '#0f766e', '#7c3aed', '#db2777'],
      category: 'professional',
      badge: 'Popular'
    },
    executive: {
      name: 'Executive',
      label: 'Executive ATS',
      description: 'Leadership-first presentation with strong headers and compact side summaries.',
      palettes: ['#1d4ed8', '#7c2d12', '#0f766e', '#475569'],
      category: 'premium',
      badge: 'Premium',
      price: 'Rs.199'
    },
    creative: {
      name: 'Creative',
      label: 'Creative',
      description: 'High-contrast sidebar layout with visual branding and a portfolio feel.',
      palettes: ['#0f766e', '#c2410c', '#7c3aed', '#e11d48'],
      category: 'creative',
      badge: 'Creative'
    },
    minimal: {
      name: 'Minimal',
      label: 'Minimal Editorial',
      description: 'Airy editorial layout with subtle separators and understated emphasis.',
      palettes: ['#334155', '#0f766e', '#7c2d12', '#4338ca'],
      category: 'professional',
      badge: 'Clean'
    },
    bold: {
      name: 'Bold',
      label: 'Bold Contrast',
      description: 'Strong top band and confident contrast for visible personal branding.',
      palettes: ['#111827', '#1d4ed8', '#be123c', '#14532d'],
      category: 'creative',
      badge: 'Bold'
    },
    timeline: {
      name: 'Timeline',
      label: 'Timeline Focus',
      description: 'Chronological storytelling layout with a guided career timeline.',
      palettes: ['#0f766e', '#2563eb', '#7c3aed', '#9a3412'],
      category: 'professional',
      badge: 'Structured'
    },
    studio: {
      name: 'Studio',
      label: 'Studio Portfolio',
      description: 'Portfolio-forward layout with a premium split canvas presentation.',
      palettes: ['#111827', '#0f766e', '#9333ea', '#c2410c'],
      category: 'premium',
      badge: 'Premium',
      price: 'Rs.249'
    },
    compact: {
      name: 'Compact',
      label: 'Compact Pro',
      description: 'Tighter one-page style format for efficient and focused resumes.',
      palettes: ['#334155', '#2563eb', '#166534', '#b91c1c'],
      category: 'compact',
      badge: 'One Page'
    },
    prestige: {
      name: 'Prestige',
      label: 'Prestige Editorial',
      description: 'Elegant editorial rhythm with spacious blocks and premium contrast.',
      palettes: ['#1e293b', '#7c2d12', '#4338ca', '#0f766e'],
      category: 'premium',
      badge: 'Premium',
      price: 'Rs.299'
    },
    signature: {
      name: 'Signature',
      label: 'Signature Luxe',
      description: 'Luxury split-panel layout with a standout profile rail and polished executive spacing.',
      palettes: ['#0f172a', '#7c3aed', '#0f766e', '#b45309'],
      category: 'premium',
      badge: 'Premium',
      price: 'Rs.349'
    }
  };
  const premiumStorageKey = 'resumeBuilderPremiumUnlocks';
  const configNode = document.getElementById('resume-builder-config');
  const manualPaymentTesting = configNode?.dataset.manualPaymentTesting === 'true';
  const razorpayConfigured = configNode?.dataset.razorpayConfigured === 'true';

  let output = null;
  let previewTemplateSelect = null;
  let accentColorPicker = null;
  let previewAccentColor = null;
  let currentTemplate = 'classic';
  let currentAccent = templateCatalog.classic.palettes[0];
  let currentResumeHtml = '';
  let draftData = null;
  let currentFilter = 'all';
  let unlockedPremiumTemplates = new Set();

  const sampleData = {
    name: 'Your Name',
    email: 'you@example.com',
    phone: '+91 98765 43210',
    linkedin: 'https://linkedin.com/in/yourprofile',
    github: 'https://github.com/yourprofile',
    portfolio: '',
    summary: 'Adaptable professional with strong communication, technical skills, and a clear focus on delivering measurable impact.',
    tech_skills: ['Python', 'Django', 'SQL'],
    soft_skills: ['Leadership', 'Communication'],
    activities: 'Hackathons, volunteering, and student leadership activities.',
    projects: 'Resume builder platform, ATS score analyzer, and portfolio-ready web apps.',
    certifications: 'Cloud certification, frontend certification, and role-based training.',
    experience: [
      { title: 'Full Stack Developer', org: 'Innovaskill', period: '2024 - Present', loc: 'Chennai', details: 'Built web applications; improved usability; collaborated with teams' }
    ],
    education: [
      { title: 'B.Tech Information Technology', org: 'Rajalakshmi Engineering College', period: '2021 - 2025', loc: 'Chennai', details: '' }
    ]
  };

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function hexToRgb(hex) {
    const clean = hex.replace('#', '');
    const normalized = clean.length === 3
      ? clean.split('').map((char) => char + char).join('')
      : clean;
    const int = parseInt(normalized, 16);
    return {
      r: (int >> 16) & 255,
      g: (int >> 8) & 255,
      b: int & 255
    };
  }

  function mixColor(hex, targetHex, ratio) {
    const base = hexToRgb(hex);
    const target = hexToRgb(targetHex);
    const mixed = {
      r: Math.round(base.r + (target.r - base.r) * ratio),
      g: Math.round(base.g + (target.g - base.g) * ratio),
      b: Math.round(base.b + (target.b - base.b) * ratio)
    };
    return `rgb(${mixed.r}, ${mixed.g}, ${mixed.b})`;
  }

  function buildTheme(accent) {
    return {
      accent,
      accentDark: mixColor(accent, '#0f172a', 0.35),
      accentSoft: mixColor(accent, '#ffffff', 0.82),
      accentMid: mixColor(accent, '#ffffff', 0.55),
      ink: '#0f172a',
      muted: '#475569',
      line: mixColor(accent, '#cbd5e1', 0.78)
    };
  }

  function loadUnlockedPremiumTemplates() {
    try {
      const saved = JSON.parse(window.localStorage.getItem(premiumStorageKey) || '[]');
      unlockedPremiumTemplates = new Set(Array.isArray(saved) ? saved : []);
    } catch (error) {
      unlockedPremiumTemplates = new Set();
    }
  }

  function persistUnlockedPremiumTemplates() {
    window.localStorage.setItem(premiumStorageKey, JSON.stringify(Array.from(unlockedPremiumTemplates)));
  }

  function getCsrfToken() {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function isPremiumTemplate(templateKey) {
    return templateCatalog[templateKey]?.category === 'premium';
  }

  function isTemplateUnlocked(templateKey) {
    return !isPremiumTemplate(templateKey) || unlockedPremiumTemplates.has(templateKey);
  }

  function formatOptionalLink(url, label) {
    if (!url) return '';
    const safeUrl = escapeHtml(url);
    return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`;
  }

  function makeBullets(rawText) {
    if (!rawText) return [];
    return rawText
      .split(/[\n;]/)
      .map((item) => item.trim())
      .flatMap((item) => item.split('.').map((part) => part.trim()))
      .filter(Boolean);
  }

  function renderList(items, emptyMessage) {
    return items.length ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : `<p>${escapeHtml(emptyMessage)}</p>`;
  }

  function renderSkills(data) {
    const skills = [...data.tech_skills, ...data.soft_skills];
    return skills.length
      ? skills.map((skill) => `<span class="skill-pill">${escapeHtml(skill)}</span>`).join('')
      : '<span class="skill-pill skill-pill-empty">Add skills</span>';
  }

  function renderExperience(entries) {
    return entries.length ? entries.map((entry) => `
      <div class="resume-item">
        <div class="resume-item-title">
          <strong>${escapeHtml(entry.title)}</strong>
          <span>${escapeHtml(entry.period)}</span>
        </div>
        <div class="resume-item-meta">${escapeHtml(entry.org)}${entry.loc ? ` | ${escapeHtml(entry.loc)}` : ''}</div>
        ${renderList(makeBullets(entry.details), 'Add experience highlights to strengthen this section.')}
      </div>
    `).join('') : '<p>Add experience entries.</p>';
  }

  function renderEducation(entries) {
    return entries.length ? entries.map((entry) => `
      <div class="resume-item">
        <div class="resume-item-title">
          <strong>${escapeHtml(entry.title)}</strong>
          <span>${escapeHtml(entry.period)}</span>
        </div>
        <div class="resume-item-meta">${escapeHtml(entry.org)}${entry.loc ? ` | ${escapeHtml(entry.loc)}` : ''}</div>
        ${entry.details ? `<p>${escapeHtml(entry.details)}</p>` : ''}
      </div>
    `).join('') : '<p>Add education entries.</p>';
  }

  function collectData(form, experienceItems, educationItems) {
    const formData = new FormData(form);
    const data = {
      name: formData.get('name')?.trim() || '',
      email: formData.get('email')?.trim() || '',
      phone: formData.get('phone')?.trim() || '',
      linkedin: formData.get('linkedin')?.trim() || '',
      github: formData.get('github')?.trim() || '',
      portfolio: formData.get('portfolio')?.trim() || '',
      summary: formData.get('summary')?.trim() || '',
      tech_skills: (formData.get('tech_skills') || '').split(',').map((value) => value.trim()).filter(Boolean),
      soft_skills: (formData.get('soft_skills') || '').split(',').map((value) => value.trim()).filter(Boolean),
      activities: formData.get('activities')?.trim() || '',
      projects: formData.get('projects')?.trim() || '',
      certifications: formData.get('certifications')?.trim() || '',
      experience: [],
      education: []
    };

    experienceItems.querySelectorAll('.entry-row').forEach((row) => {
      const title = row.querySelector('[name="experience_title"]').value.trim();
      const org = row.querySelector('[name="experience_org"]').value.trim();
      const period = row.querySelector('[name="experience_period"]').value.trim();
      const loc = row.querySelector('[name="experience_loc"]').value.trim();
      const details = row.querySelector('[name="experience_details"]').value.trim();
      if (title || org || details) {
        data.experience.push({ title, org, period, loc, details });
      }
    });

    educationItems.querySelectorAll('.entry-row').forEach((row) => {
      const title = row.querySelector('[name="education_title"]').value.trim();
      const org = row.querySelector('[name="education_org"]').value.trim();
      const period = row.querySelector('[name="education_period"]').value.trim();
      const loc = row.querySelector('[name="education_loc"]').value.trim();
      const details = row.querySelector('[name="education_details"]').value.trim();
      if (title || org || details) {
        data.education.push({ title, org, period, loc, details });
      }
    });

    return data;
  }

  function validateData(data) {
    if (!data.name || !data.email || !data.phone) return 'Fill Name, Email, and Phone.';
    if (!data.summary || data.summary.length < 20) return 'Add a proper summary with at least 20 characters.';
    if (!data.tech_skills.length && !data.soft_skills.length) return 'Add at least one skill.';
    if (!data.experience.length) return 'Add at least one experience entry.';
    if (!data.education.length) return 'Add at least one education entry.';
    return '';
  }

  function generateResume(data, template, accent) {
    const theme = buildTheme(accent);
    const contactItems = [
      escapeHtml(data.email),
      escapeHtml(data.phone),
      formatOptionalLink(data.linkedin, 'LinkedIn'),
      formatOptionalLink(data.github, 'GitHub'),
      formatOptionalLink(data.portfolio, 'Portfolio')
    ].filter(Boolean).join(' | ');
    const experienceHtml = renderExperience(data.experience);
    const educationHtml = renderEducation(data.education);
    const skillsHtml = renderSkills(data);
    const summary = escapeHtml(data.summary || 'Add a short summary that introduces your profile and strengths.');
    const projects = escapeHtml(data.projects || 'Highlight your best projects, tools used, and measurable outcomes.');
    const certifications = escapeHtml(data.certifications || 'Add certifications, training, or credentials relevant to your target role.');
    const activities = escapeHtml(data.activities || 'Add clubs, volunteering, hackathons, or leadership activities.');
    const name = escapeHtml(data.name || 'Your Name');
    const wrapperStart = `<div class="resume-paper template-${template}" style="--resume-accent:${theme.accent};--resume-accent-dark:${theme.accentDark};--resume-accent-soft:${theme.accentSoft};--resume-accent-mid:${theme.accentMid};--resume-ink:${theme.ink};--resume-muted:${theme.muted};--resume-line:${theme.line};">`;
    const wrapperEnd = '</div>';

    if (template === 'modern') {
      return `${wrapperStart}<div class="resume-modern-shell"><section class="resume-main-column"><header class="resume-header"><div><p class="resume-kicker">Professional Resume</p><h1>${name}</h1></div><p class="resume-contact-line">${contactItems}</p></header><section class="resume-block"><h2>Professional Summary</h2><p>${summary}</p></section><section class="resume-block"><h2>Experience</h2>${experienceHtml}</section><section class="resume-block"><h2>Education</h2>${educationHtml}</section></section><aside class="resume-side-column"><section class="resume-card"><h2>Skills</h2><div class="skill-list">${skillsHtml}</div></section><section class="resume-card"><h2>Projects</h2><p>${projects}</p></section><section class="resume-card"><h2>Certifications</h2><p>${certifications}</p></section><section class="resume-card"><h2>Activities</h2><p>${activities}</p></section></aside></div>${wrapperEnd}`;
    }

    if (template === 'executive') {
      return `${wrapperStart}<header class="resume-header executive-header"><div><p class="resume-kicker">Executive Profile</p><h1>${name}</h1><p class="resume-lead">${summary}</p></div><div class="resume-contact-panel"><p>${escapeHtml(data.email)}</p><p>${escapeHtml(data.phone)}</p>${data.linkedin ? `<p>${formatOptionalLink(data.linkedin, 'LinkedIn')}</p>` : ''}${data.github ? `<p>${formatOptionalLink(data.github, 'GitHub')}</p>` : ''}${data.portfolio ? `<p>${formatOptionalLink(data.portfolio, 'Portfolio')}</p>` : ''}</div></header><div class="resume-modern-shell executive-shell"><section class="resume-main-column"><section class="resume-block"><h2>Experience</h2>${experienceHtml}</section><section class="resume-block"><h2>Education</h2>${educationHtml}</section></section><aside class="resume-side-column executive-side"><section class="resume-card"><h2>Core Skills</h2><div class="skill-list">${skillsHtml}</div></section><section class="resume-card"><h2>Projects</h2><p>${projects}</p></section><section class="resume-card"><h2>Certifications</h2><p>${certifications}</p></section><section class="resume-card"><h2>Activities</h2><p>${activities}</p></section></aside></div>${wrapperEnd}`;
    }

    if (template === 'creative') {
      return `${wrapperStart}<div class="resume-creative-shell"><aside class="resume-creative-sidebar"><div class="creative-badge">${escapeHtml((data.name || 'R').charAt(0).toUpperCase())}</div><h1>${name}</h1><p class="resume-lead">${summary}</p><section class="resume-card"><h2>Contact</h2><p>${escapeHtml(data.email)}</p><p>${escapeHtml(data.phone)}</p>${data.linkedin ? `<p>${formatOptionalLink(data.linkedin, 'LinkedIn')}</p>` : ''}${data.github ? `<p>${formatOptionalLink(data.github, 'GitHub')}</p>` : ''}${data.portfolio ? `<p>${formatOptionalLink(data.portfolio, 'Portfolio')}</p>` : ''}</section><section class="resume-card"><h2>Skills</h2><div class="skill-list">${skillsHtml}</div></section></aside><main class="resume-creative-main"><section class="resume-block"><h2>Experience</h2>${experienceHtml}</section><section class="resume-block"><h2>Projects</h2><p>${projects}</p></section><section class="resume-block"><h2>Education</h2>${educationHtml}</section><section class="resume-block"><h2>Certifications</h2><p>${certifications}</p></section><section class="resume-block"><h2>Activities</h2><p>${activities}</p></section></main></div>${wrapperEnd}`;
    }

    if (template === 'minimal') {
      return `${wrapperStart}<header class="resume-header minimal-header"><h1>${name}</h1><p class="resume-contact-line">${contactItems}</p></header><section class="resume-block"><h2>Summary</h2><p>${summary}</p></section><div class="resume-grid-two"><section class="resume-block"><h2>Experience</h2>${experienceHtml}</section><section class="resume-block"><h2>Skills</h2><div class="skill-list">${skillsHtml}</div><h2>Projects</h2><p>${projects}</p><h2>Education</h2>${educationHtml}<h2>Certifications</h2><p>${certifications}</p><h2>Activities</h2><p>${activities}</p></section></div>${wrapperEnd}`;
    }

    if (template === 'bold') {
      return `${wrapperStart}<header class="resume-header bold-header"><div><p class="resume-kicker">Bold Edition</p><h1>${name}</h1></div><p class="resume-contact-line">${contactItems}</p></header><section class="resume-banner-card"><h2>Summary</h2><p>${summary}</p></section><div class="resume-grid-two"><section class="resume-block"><h2>Experience</h2>${experienceHtml}<h2>Education</h2>${educationHtml}</section><aside class="resume-side-column"><section class="resume-card accent-card"><h2>Skills</h2><div class="skill-list">${skillsHtml}</div></section><section class="resume-card"><h2>Projects</h2><p>${projects}</p></section><section class="resume-card"><h2>Certifications</h2><p>${certifications}</p></section><section class="resume-card"><h2>Activities</h2><p>${activities}</p></section></aside></div>${wrapperEnd}`;
    }

    if (template === 'timeline') {
      return `${wrapperStart}<header class="resume-header"><p class="resume-kicker">Career Timeline</p><h1>${name}</h1><p class="resume-contact-line">${contactItems}</p></header><section class="resume-banner-card"><h2>Summary</h2><p>${summary}</p></section><div class="resume-grid-two"><section class="resume-block timeline-column"><h2>Experience</h2>${experienceHtml}</section><aside class="resume-side-column"><section class="resume-card"><h2>Skills</h2><div class="skill-list">${skillsHtml}</div></section><section class="resume-card"><h2>Education</h2>${educationHtml}</section><section class="resume-card"><h2>Projects</h2><p>${projects}</p></section><section class="resume-card"><h2>Certifications</h2><p>${certifications}</p></section></aside></div>${wrapperEnd}`;
    }

    if (template === 'studio') {
      return `${wrapperStart}<div class="resume-creative-shell studio-shell"><aside class="resume-side-column studio-side"><section class="resume-card accent-card"><p class="resume-kicker">Studio Resume</p><h2>Profile</h2><p>${summary}</p></section><section class="resume-card"><h2>Skills</h2><div class="skill-list">${skillsHtml}</div></section><section class="resume-card"><h2>Contact</h2><p>${escapeHtml(data.email)}</p><p>${escapeHtml(data.phone)}</p>${data.linkedin ? `<p>${formatOptionalLink(data.linkedin, 'LinkedIn')}</p>` : ''}${data.portfolio ? `<p>${formatOptionalLink(data.portfolio, 'Portfolio')}</p>` : ''}</section></aside><main class="resume-creative-main"><header class="resume-header"><h1>${name}</h1><p class="resume-contact-line">${contactItems}</p></header><section class="resume-block"><h2>Experience</h2>${experienceHtml}</section><section class="resume-block"><h2>Projects</h2><p>${projects}</p></section><section class="resume-block"><h2>Education</h2>${educationHtml}</section><section class="resume-block"><h2>Activities</h2><p>${activities}</p></section></main></div>${wrapperEnd}`;
    }

    if (template === 'compact') {
      return `${wrapperStart}<header class="resume-header compact-header"><div><p class="resume-kicker">Compact Pro</p><h1>${name}</h1></div><p class="resume-contact-line">${contactItems}</p></header><div class="resume-grid-two compact-grid"><section class="resume-block"><h2>Summary</h2><p>${summary}</p><h2>Experience</h2>${experienceHtml}</section><aside class="resume-side-column"><section class="resume-card"><h2>Skills</h2><div class="skill-list">${skillsHtml}</div></section><section class="resume-card"><h2>Education</h2>${educationHtml}</section><section class="resume-card"><h2>Projects</h2><p>${projects}</p></section><section class="resume-card"><h2>Certifications</h2><p>${certifications}</p><h2>Activities</h2><p>${activities}</p></section></aside></div>${wrapperEnd}`;
    }

    if (template === 'prestige') {
      return `${wrapperStart}<header class="resume-header prestige-header"><p class="resume-kicker">Prestige Editorial</p><h1>${name}</h1><p class="resume-contact-line">${contactItems}</p></header><section class="resume-block"><h2>Executive Summary</h2><p>${summary}</p></section><section class="resume-grid-two"><section class="resume-block"><h2>Experience</h2>${experienceHtml}<h2>Projects</h2><p>${projects}</p></section><section class="resume-block prestige-side"><h2>Skills</h2><div class="skill-list">${skillsHtml}</div><h2>Education</h2>${educationHtml}<h2>Certifications</h2><p>${certifications}</p><h2>Activities</h2><p>${activities}</p></section></section>${wrapperEnd}`;
    }

    if (template === 'signature') {
      return `${wrapperStart}<div class="resume-creative-shell signature-shell"><aside class="resume-creative-sidebar signature-rail"><p class="resume-kicker">Signature Luxe</p><h1>${name}</h1><p class="resume-lead">${summary}</p><section class="resume-card"><h2>Contact</h2><p>${escapeHtml(data.email)}</p><p>${escapeHtml(data.phone)}</p>${data.linkedin ? `<p>${formatOptionalLink(data.linkedin, 'LinkedIn')}</p>` : ''}${data.github ? `<p>${formatOptionalLink(data.github, 'GitHub')}</p>` : ''}${data.portfolio ? `<p>${formatOptionalLink(data.portfolio, 'Portfolio')}</p>` : ''}</section><section class="resume-card"><h2>Core Skills</h2><div class="skill-list">${skillsHtml}</div></section></aside><main class="resume-creative-main signature-main"><section class="resume-banner-card accent-card"><h2>Projects</h2><p>${projects}</p></section><section class="resume-block"><h2>Experience</h2>${experienceHtml}</section><div class="resume-grid-two"><section class="resume-block"><h2>Education</h2>${educationHtml}</section><section class="resume-block"><h2>Certifications</h2><p>${certifications}</p><h2>Activities</h2><p>${activities}</p></section></div></main></div>${wrapperEnd}`;
    }

    return `${wrapperStart}<header class="resume-header"><p class="resume-kicker">ATS Resume</p><h1>${name}</h1><p class="resume-contact-line">${contactItems}</p></header><section class="resume-block"><h2>Professional Summary</h2><p>${summary}</p></section><section class="resume-block"><h2>Skills</h2><div class="skill-list">${skillsHtml}</div></section><section class="resume-block"><h2>Experience</h2>${experienceHtml}</section><section class="resume-block"><h2>Education</h2>${educationHtml}</section><section class="resume-grid-two"><section class="resume-block"><h2>Projects</h2><p>${projects}</p></section><section class="resume-block"><h2>Certifications</h2><p>${certifications}</p><h2>Activities</h2><p>${activities}</p></section></section>${wrapperEnd}`;
  }

  function getExportStyles() {
    return `
      @page{size:A4;margin:10mm;}
      *{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
      html,body{margin:0;padding:0;background:#f5f7fb;font-family:Segoe UI,Arial,sans-serif;color:#0f172a;}
      body{padding:24px;}
      .resume-paper{width:100%;max-width:210mm;min-height:277mm;margin:0 auto;background:#fff;border-radius:24px;padding:32px;box-shadow:0 20px 60px rgba(15,23,42,.12);color:var(--resume-ink);}
      .resume-paper a{color:var(--resume-accent-dark);text-decoration:none;}
      .resume-paper h1,.resume-paper h2,.resume-paper p{margin-top:0}
      .resume-header{border-bottom:3px solid var(--resume-line);padding-bottom:18px;margin-bottom:22px}
      .resume-header h1{font-size:2.2rem;line-height:1.05;margin:8px 0}
      .resume-kicker{text-transform:uppercase;letter-spacing:.12em;font-size:.78rem;font-weight:800;color:var(--resume-accent-dark);margin:0}
      .resume-contact-line,.resume-lead{color:var(--resume-muted);line-height:1.7}
      .resume-block{margin-bottom:22px}
      .resume-block h2,.resume-card h2,.resume-banner-card h2{font-size:1rem;letter-spacing:.08em;text-transform:uppercase;color:var(--resume-accent-dark);margin-bottom:10px}
      .resume-block h2{border-bottom:1px solid var(--resume-line);padding-bottom:8px}
      .resume-grid-two,.resume-modern-shell{display:grid;grid-template-columns:2fr 1fr;gap:20px}
      .resume-side-column{display:grid;gap:16px;align-content:start}
      .resume-card,.resume-banner-card{background:var(--resume-accent-soft);border:1px solid var(--resume-line);border-radius:18px;padding:16px}
      .resume-item{margin-bottom:16px}
      .resume-item-title{display:flex;justify-content:space-between;gap:10px;font-weight:700;margin-bottom:4px}
      .resume-item-meta{color:var(--resume-muted);font-size:.95rem;margin-bottom:8px}
      .resume-item ul,.resume-block ul{margin:8px 0 0;padding-left:18px;color:var(--resume-muted)}
      .resume-paper p{color:var(--resume-muted);line-height:1.7}
      .skill-list{display:flex;flex-wrap:wrap;gap:8px}
      .skill-pill{display:inline-flex;align-items:center;padding:7px 12px;border-radius:999px;background:var(--resume-accent-mid);color:var(--resume-accent-dark);font-size:.86rem;font-weight:700}
      .skill-pill-empty{background:#eef2f7;color:#64748b}
      .template-modern .resume-side-column,.template-bold .resume-side-column,.template-executive .executive-side{background:var(--resume-accent-soft);padding:18px;border-radius:20px}
      .template-studio .studio-side,.template-compact .resume-side-column,.template-prestige .prestige-side{background:var(--resume-accent-soft);padding:18px;border-radius:20px}
      .template-executive{border-top:10px solid var(--resume-accent)}
      .executive-header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start}
      .resume-contact-panel{min-width:220px;background:var(--resume-accent-soft);border:1px solid var(--resume-line);border-radius:18px;padding:16px}
      .resume-contact-panel p{margin-bottom:8px}
      .resume-creative-shell{display:grid;grid-template-columns:280px 1fr;gap:22px}
      .studio-shell{grid-template-columns:320px 1fr}
      .signature-shell{grid-template-columns:300px 1fr}
      .signature-rail{background:linear-gradient(180deg,var(--resume-accent-dark),var(--resume-accent));}
      .signature-main{display:grid;gap:20px}
      .resume-creative-sidebar{background:var(--resume-accent-dark);color:#fff;border-radius:24px;padding:24px;display:grid;gap:18px}
      .resume-creative-sidebar .resume-card{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.18)}
      .resume-creative-sidebar h1,.resume-creative-sidebar h2,.resume-creative-sidebar p,.resume-creative-sidebar a,.resume-creative-sidebar .skill-pill{color:#fff}
      .resume-creative-sidebar .skill-pill{background:rgba(255,255,255,.18)}
      .creative-badge{width:64px;height:64px;border-radius:18px;background:#fff;color:var(--resume-accent-dark);display:grid;place-items:center;font-size:1.9rem;font-weight:800}
      .timeline-column .resume-item{position:relative;padding-left:18px;border-left:2px solid var(--resume-line)}
      .timeline-column .resume-item::before{content:"";position:absolute;left:-7px;top:6px;width:12px;height:12px;border-radius:50%;background:var(--resume-accent)}
      .compact-header{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}
      .prestige-header h1{font-size:2.6rem}
      .minimal-header{text-align:center}
      .minimal-header h1{font-size:2.4rem}
      .bold-header{background:linear-gradient(135deg,var(--resume-accent-dark),var(--resume-accent));color:#fff;padding:24px;border-radius:22px;border-bottom:none}
      .bold-header h1,.bold-header p,.bold-header .resume-kicker,.bold-header a{color:#fff}
      .accent-card{background:var(--resume-accent-dark)}
      .accent-card h2,.accent-card p,.accent-card .skill-pill{color:#fff}
      .accent-card .skill-pill{background:rgba(255,255,255,.16)}
      @media (max-width: 900px){body{padding:0}.resume-paper{padding:20px;border-radius:0;min-height:auto}.resume-creative-shell,.resume-grid-two,.resume-modern-shell,.executive-header{grid-template-columns:1fr;display:grid}}
      @media print{
        html,body{background:#fff !important;}
        body{padding:0;}
        .resume-paper{
          max-width:none;
          min-height:auto;
          box-shadow:none;
          border-radius:0;
          padding:14mm 12mm;
          page-break-inside:avoid;
        }
        .resume-header,
        .resume-block,
        .resume-card,
        .resume-banner-card,
        .resume-item{
          break-inside:avoid;
          page-break-inside:avoid;
        }
        .resume-creative-shell,
        .resume-grid-two,
        .resume-modern-shell{
          align-items:start;
        }
      }
    `;
  }

  function updateTemplateSummary() {
    const selected = templateCatalog[currentTemplate];
    const title = document.getElementById('selected-template-name');
    const copy = document.getElementById('selected-template-copy');
    const builderTitle = document.getElementById('builder-selected-template-name');
    const builderCopy = document.getElementById('builder-selected-template-copy');
    if (title) title.textContent = selected.name;
    if (builderTitle) builderTitle.textContent = selected.name;
    if (copy) {
      copy.textContent = isTemplateUnlocked(currentTemplate)
        ? selected.description
        : `${selected.description} Unlock this premium template to continue.`;
    }
    if (builderCopy) {
      builderCopy.textContent = isTemplateUnlocked(currentTemplate)
        ? `${selected.description} The preview updates here while you build.`
        : `${selected.description} Unlock this premium template to continue.`;
    }
    const useButton = document.getElementById('use-selected-template');
    if (useButton) {
      useButton.textContent = isTemplateUnlocked(currentTemplate) ? 'Use Selected Template' : `Unlock ${selected.name}`;
    }
  }

  function syncControls() {
    if (previewTemplateSelect) previewTemplateSelect.value = currentTemplate;
    if (accentColorPicker) accentColorPicker.value = currentAccent;
    if (previewAccentColor) previewAccentColor.value = currentAccent;
  }

  function renderCurrentResume() {
    if (!draftData || !output) return;
    currentResumeHtml = generateResume(draftData, currentTemplate, currentAccent);
    output.innerHTML = currentResumeHtml;
    document.querySelectorAll('[data-template-preview-target]').forEach((preview) => {
      preview.innerHTML = currentResumeHtml;
    });
  }

  function renderTemplateGallery() {
    const gallery = document.getElementById('template-gallery');
    if (!gallery) return;

    gallery.innerHTML = Object.entries(templateCatalog)
      .filter(([, template]) => currentFilter === 'all' || template.category === currentFilter)
      .map(([key, template]) => {
      const unlocked = isTemplateUnlocked(key);
      const statusLabel = currentTemplate === key ? 'Selected' : unlocked ? 'Choose' : 'Locked';
      const palettes = template.palettes.map((color) => `
        <button type="button" class="palette-swatch ${currentTemplate === key && currentAccent === color ? 'active' : ''}" data-template="${key}" data-color="${color}" aria-label="${template.name} color ${color}" style="--swatch:${color};"></button>
      `).join('');

      return `
        <article class="template-card ${currentTemplate === key ? 'active' : ''} ${!unlocked ? 'locked' : ''}">
          <button type="button" class="template-card-button" data-template="${key}">
            <div class="template-thumb template-thumb-${key}" style="--thumb-accent:${currentTemplate === key ? currentAccent : template.palettes[0]};">
              <span class="template-badge">${template.badge || 'Template'}</span>
              ${!unlocked ? `<span class="template-lock">Premium ${template.price || ''}</span>` : ''}
              <div class="thumb-bar"></div>
              <div class="thumb-body">
                <div class="thumb-sidebar"></div>
                <div class="thumb-content">
                  <div class="thumb-line thumb-line-lg"></div>
                  <div class="thumb-line"></div>
                  <div class="thumb-line thumb-line-sm"></div>
                  <div class="thumb-grid"><span></span><span></span><span></span></div>
                </div>
              </div>
            </div>
            <div class="template-card-copy">
              <div><h3>${template.name}</h3><p>${template.description}</p><span class="template-category">${template.category}</span></div>
              <span class="template-status">${statusLabel}</span>
            </div>
          </button>
          <div class="template-swatches">${palettes}</div>
        </article>
      `;
    }).join('');

    gallery.querySelectorAll('[data-template]').forEach((button) => {
      button.addEventListener('click', () => {
        currentTemplate = button.dataset.template;
        currentAccent = button.dataset.color || templateCatalog[currentTemplate].palettes[0];
        updateTemplateSummary();
        syncControls();
        renderTemplateGallery();
        renderCurrentResume();
      });
    });
  }

  function updatePaymentPanel() {
    const selected = templateCatalog[currentTemplate];
    if (!selected) return;
    const title = document.getElementById('payment-template-name');
    const copy = document.getElementById('payment-template-copy');
    const price = document.getElementById('payment-template-price');
    const note = document.getElementById('payment-mode-note');
    const debugTemplate = document.getElementById('debug-current-template');
    const debugManual = document.getElementById('debug-manual-mode');
    const debugConfigured = document.getElementById('debug-razorpay-configured');
    if (title) title.textContent = selected.name;
    if (copy) copy.textContent = selected.description;
    if (price) price.textContent = selected.price || 'Rs.199';
    if (note) {
      note.textContent = manualPaymentTesting
        ? 'Manual payment testing is enabled. Submit the form to unlock this premium template without a real transaction.'
        : 'Live Razorpay checkout will open for this purchase.';
    }
    if (debugTemplate) debugTemplate.textContent = currentTemplate;
    if (debugManual) debugManual.textContent = manualPaymentTesting ? 'ON' : 'OFF';
    if (debugConfigured) debugConfigured.textContent = razorpayConfigured ? 'YES' : 'NO';
  }

  function setPaymentDebugStatus(message) {
    const status = document.getElementById('debug-payment-status');
    if (status) status.textContent = message;
  }

  function updateProgress(sectionId) {
    const map = {
      'landing-section': 'step-landing',
      'builder-section': 'step-builder',
      'template-panel': 'step-template',
      'payment-panel': 'step-template',
      'preview-panel': 'step-preview',
      'export-panel': 'step-export'
    };
    const activeId = map[sectionId];
    const steps = Array.from(document.querySelectorAll('.progress-bar .step'));
    let activeIndex = steps.findIndex((step) => step.id === activeId);
    if (activeIndex < 0) activeIndex = 0;

    steps.forEach((step, index) => {
      step.classList.remove('active', 'completed');
      if (index < activeIndex) step.classList.add('completed');
      else if (index === activeIndex) step.classList.add('active');
    });
  }

  function setVisible(sectionId) {
    const sections = document.querySelectorAll('.resume-portal > main > section.panel');
    sections.forEach((section) => section.classList.add('hidden'));
    const target = document.getElementById(sectionId);
    if (target) {
      target.classList.remove('hidden');
      updateProgress(sectionId);
    }
  }
  window.setVisible = setVisible;

  function completeExport() {
    document.getElementById('step-export')?.classList.add('completed');
    document.getElementById('post-download-actions')?.classList.remove('hidden');
  }

  async function saveResumeToBackend(data) {
    const response = await fetch('/builder/save-resume/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, template: currentTemplate })
    });
    const responseBody = await response.text();
    const json = JSON.parse(responseBody);
    if (!response.ok) throw new Error(json.details || json.error || response.statusText);
    return json;
  }

  async function createRazorpayOrder(templateKey) {
    const response = await fetch('/builder/payments/razorpay/order/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ template: templateKey })
    });
    const json = await response.json();
    if (!response.ok) throw new Error(json.details || json.error || 'Unable to create Razorpay order');
    return json;
  }

  async function verifyRazorpayPayment(paymentResponse) {
    const response = await fetch('/builder/payments/razorpay/verify/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        order_id: paymentResponse.razorpay_order_id,
        payment_id: paymentResponse.razorpay_payment_id,
        signature: paymentResponse.razorpay_signature,
        template: currentTemplate
      })
    });
    const json = await response.json();
    if (!response.ok || !json.verified) throw new Error(json.error || 'Payment verification failed');
    return json;
  }

  async function verifyManualPayment(reference) {
    const response = await fetch('/builder/payments/razorpay/verify/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        template: currentTemplate,
        payment_id: `manual_${Date.now()}`,
        manual_reference: reference
      })
    });
    const json = await response.json();
    if (!response.ok || !json.verified) throw new Error(json.error || 'Manual payment verification failed');
    return json;
  }

  async function unlockPremiumTemplateAfterPayment(form) {
    unlockedPremiumTemplates.add(currentTemplate);
    persistUnlockedPremiumTemplates();
    updateTemplateSummary();
    renderTemplateGallery();
    updatePaymentPanel();
    await saveResumeToBackend(draftData);
    form.reset();
    const defaultMethod = form.querySelector('input[value="upi"]');
    if (defaultMethod) {
      defaultMethod.checked = true;
      document.querySelectorAll('.payment-method').forEach((card) => card.classList.remove('active'));
      defaultMethod.closest('.payment-method')?.classList.add('active');
    }
    applySelectedTemplate(true);
  }

  function exportDocument(title) {
    return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>${escapeHtml(title)}</title><style>${getExportStyles()}</style></head><body>${currentResumeHtml}</body></html>`;
  }

  function applySelectedTemplate(showPreview) {
    if (!draftData) return;
    renderTemplateGallery();
    updateTemplateSummary();
    syncControls();
    renderCurrentResume();
    if (showPreview) {
      setVisible('preview-panel');
    }
  }

  function continueWithCurrentTemplate() {
    if (isTemplateUnlocked(currentTemplate)) {
      return true;
    }
    updatePaymentPanel();
    setVisible('payment-panel');
    return false;
  }

  function initResumeBuilder() {
    const form = document.getElementById('resume-form');
    output = document.getElementById('resume-output');
    previewTemplateSelect = document.getElementById('preview-template-select');
    accentColorPicker = document.getElementById('accent-color-picker');
    previewAccentColor = document.getElementById('preview-accent-color');

    if (!form || !output) return;

    const experienceItems = document.getElementById('experience-items');
    const educationItems = document.getElementById('education-items');
    const atsFeedback = document.getElementById('ats-feedback');
    const premiumPaymentForm = document.getElementById('premium-payment-form');
    const defaultExperience = { title: '', org: '', period: '', loc: '', details: '' };
    const defaultEducation = { title: '', org: '', period: '', loc: '', details: '' };

    function createEntry(type, data = {}) {
      const entry = document.createElement('div');
      entry.className = 'entry-row';
      entry.innerHTML = `
        <div class="row-top">
          <strong>${type}</strong>
          <button type="button" class="btn-sm remove">Remove</button>
        </div>
        <label>${type} Title <input name="${type.toLowerCase()}_title" value="${escapeHtml(data.title || '')}" required></label>
        <label>Organization <input name="${type.toLowerCase()}_org" value="${escapeHtml(data.org || '')}"></label>
        <label>Period <input name="${type.toLowerCase()}_period" value="${escapeHtml(data.period || '')}"></label>
        <label>Location / Major <input name="${type.toLowerCase()}_loc" value="${escapeHtml(data.loc || '')}"></label>
        <label>Details <textarea name="${type.toLowerCase()}_details">${escapeHtml(data.details || '')}</textarea></label>
      `;
      entry.querySelector('.remove').addEventListener('click', () => {
        entry.remove();
        syncDraftPreview();
      });
      return entry;
    }

    function addExperience(data = defaultExperience) {
      experienceItems.appendChild(createEntry('Experience', data));
      syncDraftPreview();
    }

    function addEducation(data = defaultEducation) {
      educationItems.appendChild(createEntry('Education', data));
      syncDraftPreview();
    }

    function updateScoreDisplays(score, feedback) {
      document.getElementById('ats-score').textContent = `${score}`;
      if (atsFeedback) atsFeedback.textContent = feedback;
    }

    function syncDraftPreview() {
      draftData = collectData(form, experienceItems, educationItems);
      const hasUserInput = Object.values(draftData).some((value) => {
        if (Array.isArray(value)) return value.length > 0;
        return String(value || '').trim() !== '';
      });
      if (!hasUserInput) {
        draftData = { ...sampleData };
      }
      renderCurrentResume();
    }

    function generateATSSCore() {
      const data = collectData(form, experienceItems, educationItems);
      const skills = [...data.tech_skills, ...data.soft_skills].filter(Boolean);
      let score = 40;
      if (data.name && data.email && data.phone) score += 25;
      if (data.summary.length > 30) score += 10;
      score += Math.min(20, data.experience.length * 4);
      score += Math.min(15, skills.length * 2);
      if (data.education.length > 0) score += 10;
      score = Math.min(100, score);
      const feedback = score > 80
        ? 'Great! Resume is strong for ATS visibility.'
        : score > 65
          ? 'Good progress. Add more relevant keywords and measurable achievements to improve the score.'
          : 'Keep refining the summary, skills, and job-specific keywords for better ATS compatibility.';
      updateScoreDisplays(score, feedback);
    }

    document.getElementById('add-experience')?.addEventListener('click', () => addExperience());
    document.getElementById('add-education')?.addEventListener('click', () => addEducation());
    document.getElementById('generate-score')?.addEventListener('click', generateATSSCore);
    form.addEventListener('input', syncDraftPreview);
    form.addEventListener('change', syncDraftPreview);
    document.getElementById('go-home')?.addEventListener('click', () => {
      window.location.href = '/';
    });

    document.getElementById('browse-templates')?.addEventListener('click', () => {
      draftData = collectData(form, experienceItems, educationItems);
      const hasAnyUserInput = Object.values(draftData).some((value) => {
        if (Array.isArray(value)) return value.length > 0;
        return String(value || '').trim() !== '';
      });
      if (!hasAnyUserInput) {
        draftData = { ...sampleData };
      }
      applySelectedTemplate(false);
      setVisible('template-panel');
    });

    document.getElementById('generate')?.addEventListener('click', () => {
      const data = collectData(form, experienceItems, educationItems);
      const validationMessage = validateData(data);
      if (validationMessage) {
        alert(validationMessage);
        return;
      }
      draftData = data;
      renderTemplateGallery();
      updateTemplateSummary();
      syncControls();
      setVisible('template-panel');
    });

    document.querySelectorAll('.template-filter').forEach((button) => {
      button.addEventListener('click', () => {
        currentFilter = button.dataset.filter || 'all';
        document.querySelectorAll('.template-filter').forEach((item) => item.classList.remove('active'));
        button.classList.add('active');
        renderTemplateGallery();
      });
    });

    document.getElementById('use-selected-template')?.addEventListener('click', async () => {
      if (!draftData) {
        draftData = collectData(form, experienceItems, educationItems);
      }
      if (!continueWithCurrentTemplate()) {
        return;
      }
      try {
        await saveResumeToBackend(draftData);
        applySelectedTemplate(true);
      } catch (error) {
        alert(`Unable to save resume: ${error.message}`);
      }
    });

    previewTemplateSelect?.addEventListener('change', (event) => {
      currentTemplate = event.target.value;
      applySelectedTemplate(false);
    });

    accentColorPicker?.addEventListener('input', (event) => {
      currentAccent = event.target.value;
      applySelectedTemplate(false);
    });

    previewAccentColor?.addEventListener('input', (event) => {
      currentAccent = event.target.value;
      applySelectedTemplate(false);
    });

    const previewApplyHandler = () => {
      if (!draftData) {
        draftData = collectData(form, experienceItems, educationItems);
      }
      currentTemplate = previewTemplateSelect?.value || currentTemplate;
      currentAccent = previewAccentColor?.value || currentAccent;
      if (!continueWithCurrentTemplate()) {
        syncControls();
        return;
      }
      applySelectedTemplate(true);
    };

    document.getElementById('preview-render-template')?.addEventListener('click', previewApplyHandler);
    document.getElementById('render-template')?.addEventListener('click', previewApplyHandler);

    document.getElementById('finalize-template')?.addEventListener('click', () => {
      setVisible('export-panel');
    });
    document.getElementById('back-to-templates')?.addEventListener('click', () => {
      setVisible('template-panel');
    });

    document.querySelectorAll('.payment-method input').forEach((input) => {
      input.addEventListener('change', () => {
        document.querySelectorAll('.payment-method').forEach((card) => card.classList.remove('active'));
        input.closest('.payment-method')?.classList.add('active');
      });
    });

    premiumPaymentForm?.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!draftData) {
        draftData = collectData(form, experienceItems, educationItems);
      }
      const paymentData = new FormData(premiumPaymentForm);
      const payerName = String(paymentData.get('payer_name') || '').trim();
      const payerEmail = String(paymentData.get('payer_email') || '').trim();
      const paymentReference = String(paymentData.get('payment_reference') || '').trim();
      if (!payerName || !payerEmail || !paymentReference) {
        alert('Complete the payment form to unlock the premium template.');
        return;
      }

      const submitButton = document.getElementById('complete-payment');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = manualPaymentTesting ? 'Unlocking Template...' : 'Opening Razorpay...';
      }
      setPaymentDebugStatus(`Submitting ${currentTemplate}`);

      try {
        const order = await createRazorpayOrder(currentTemplate);
        setPaymentDebugStatus(order.manual_testing ? 'Manual order created' : 'Razorpay order created');
        if (order.manual_testing) {
          await verifyManualPayment(paymentReference);
          setPaymentDebugStatus('Manual payment verified');
          await unlockPremiumTemplateAfterPayment(premiumPaymentForm);
          alert(`${order.template_name} unlocked in manual test mode.`);
          if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Pay & Unlock Template';
          }
          return;
        }

        if (typeof window.Razorpay !== 'function') {
          throw new Error('Razorpay checkout failed to load. Refresh the page and try again.');
        }

        const selectedMethod = premiumPaymentForm.querySelector('input[name="payment_method"]:checked')?.value;
        const options = {
          key: order.key,
          amount: order.amount,
          currency: order.currency,
          name: 'AI Resume Pro',
          description: `${order.template_name} Premium Template`,
          order_id: order.order_id,
          handler: async function (response) {
            try {
              await verifyRazorpayPayment(response);
              setPaymentDebugStatus('Razorpay payment verified');
              await unlockPremiumTemplateAfterPayment(premiumPaymentForm);
            } catch (error) {
              setPaymentDebugStatus(`Verification failed: ${error.message || 'unknown error'}`);
              alert(error.message || 'Payment verification failed.');
            } finally {
              if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = 'Pay & Unlock Template';
              }
            }
          },
          prefill: {
            name: payerName,
            email: payerEmail,
            contact: document.querySelector('[name="phone"]')?.value || ''
          },
          notes: {
            template: currentTemplate,
            reference: paymentReference,
            preferred_method: selectedMethod || 'upi'
          },
          theme: {
            color: currentAccent
          },
          modal: {
            ondismiss: function () {
              if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = 'Pay & Unlock Template';
              }
            }
          }
        };

        const razorpay = new window.Razorpay(options);
        razorpay.on('payment.failed', function (response) {
          const reason = response?.error?.description || 'Payment failed. Please try again.';
          alert(reason);
          if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Pay & Unlock Template';
          }
        });
        razorpay.open();
      } catch (error) {
        setPaymentDebugStatus(`Error: ${error.message || 'Unable to start premium template checkout.'}`);
        alert(error.message || 'Unable to start premium template checkout.');
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = 'Pay & Unlock Template';
        }
      }
    });

    document.getElementById('export-html')?.addEventListener('click', () => {
      if (!currentResumeHtml) {
        alert('Generate resume first!');
        return;
      }
      const html = exportDocument(document.querySelector('[name="name"]')?.value || 'resume');
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `${currentTemplate}-resume.html`;
      anchor.click();
      URL.revokeObjectURL(url);
      completeExport();
    });

    document.getElementById('export-docx')?.addEventListener('click', () => {
      if (!currentResumeHtml) {
        alert('Generate resume first!');
        return;
      }
      const html = exportDocument(document.querySelector('[name="name"]')?.value || 'resume');
      const blob = new Blob([html], { type: 'application/msword' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `${currentTemplate}-resume.doc`;
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      URL.revokeObjectURL(url);
      completeExport();
    });

    document.getElementById('export-pdf')?.addEventListener('click', () => {
      if (!currentResumeHtml) {
        alert('Generate resume first!');
        return;
      }
      const printWindow = window.open('', '', 'width=1000,height=900');
      if (!printWindow) {
        alert('Allow pop-ups to print the PDF.');
        return;
      }
      printWindow.document.write(exportDocument('Resume'));
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
      completeExport();
    });

    addExperience();
    addEducation();
    loadUnlockedPremiumTemplates();
    draftData = { ...sampleData };
    renderTemplateGallery();
    updateTemplateSummary();
    syncControls();
    renderCurrentResume();
    setVisible('builder-section');
    updateScoreDisplays(0, 'Complete resume builder entries and click "Generate Score".');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initResumeBuilder);
  } else {
    initResumeBuilder();
  }
})();
