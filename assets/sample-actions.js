(() => {
  const copy = {
    es: {
      heading: '¿Qué quieres mejorar?',
      intro: 'Elige una opción y se abrirá un email para hablarlo.',
      pyramid: 'Propuesta ilustrativa de pirámide QR para mesa.',
      generatedCaption: 'Ilustración creada con IA; no es una fotografía de los platos ni del local del restaurante.',
      generatedAlt: 'Ilustración gastronómica creada con IA; no muestra platos ni espacios reales del restaurante.',
      note: 'Se abrirá un email dirigido a info@web-by-elie.com.',
      subject: 'Muestra de carta',
      body: 'Hola, me interesa',
      labels: {
        complete: 'Completar el menú',
        languages: 'Añadir más idiomas',
        prices: 'Actualizar precios',
        pyramids: 'Pedir pirámides',
      },
    },
    en: {
      heading: 'Make this sample yours',
      intro: 'Choose an option to start an email conversation.',
      pyramid: 'Illustrative QR pyramid proposal for a restaurant table.',
      generatedCaption: 'AI-created illustration; not a photograph of the restaurant’s dishes or premises.',
      generatedAlt: 'AI-created food illustration; it does not show the restaurant’s actual dishes or premises.',
      note: 'This opens an email addressed to info@web-by-elie.com.',
      subject: 'Menu sample',
      body: "Hello, I'm interested in",
      labels: {
        complete: 'Complete the menu',
        languages: 'Add more languages',
        prices: 'Update prices',
        pyramids: 'Order pyramids',
      },
    },
    fr: {
      heading: 'Personnalisez cet exemple',
      intro: 'Choisissez une option pour démarrer un email.',
      pyramid: 'Proposition illustrative de pyramide QR pour une table.',
      generatedCaption: 'Illustration créée par IA ; ce n’est pas une photographie des plats ni du lieu du restaurant.',
      generatedAlt: 'Illustration culinaire créée par IA ; elle ne montre pas les plats ni les lieux réels du restaurant.',
      note: 'Un email sera adressé à info@web-by-elie.com.',
      subject: 'Exemple de carte',
      body: 'Bonjour, je souhaite parler de',
      labels: {
        complete: 'Compléter le menu',
        languages: 'Ajouter des langues',
        prices: 'Mettre à jour les prix',
        pyramids: 'Commander des pyramides',
      },
    },
    de: {
      heading: 'Machen Sie diese Musterkarte zu Ihrer',
      intro: 'Wählen Sie eine Option, um eine E-Mail zu beginnen.',
      pyramid: 'Illustrativer QR-Pyramidenentwurf für den Tisch.',
      generatedCaption: 'KI-generierte Illustration; kein Foto der Gerichte oder Räumlichkeiten des Restaurants.',
      generatedAlt: 'KI-generierte Speisenillustration; sie zeigt keine tatsächlichen Gerichte oder Räume des Restaurants.',
      note: 'Eine E-Mail an info@web-by-elie.com wird geöffnet.',
      subject: 'Menübeispiel',
      body: 'Hallo, ich interessiere mich für',
      labels: {
        complete: 'Menü vervollständigen',
        languages: 'Weitere Sprachen hinzufügen',
        prices: 'Preise aktualisieren',
        pyramids: 'QR-Pyramiden bestellen',
      },
    },
    it: {
      heading: 'Personalizza questo esempio',
      intro: 'Scegli un’opzione per iniziare un’email.',
      pyramid: 'Proposta illustrativa di piramide QR per il tavolo.',
      generatedCaption: 'Illustrazione creata con l’IA; non è una fotografia dei piatti o del locale del ristorante.',
      generatedAlt: 'Illustrazione gastronomica creata con l’IA; non mostra piatti o ambienti reali del ristorante.',
      note: 'Si aprirà un’email indirizzata a info@web-by-elie.com.',
      subject: 'Esempio di menu',
      body: 'Buongiorno, vorrei informazioni su',
      labels: {
        complete: 'Completa il menu',
        languages: 'Aggiungi altre lingue',
        prices: 'Aggiorna i prezzi',
        pyramids: 'Ordina le piramidi QR',
      },
    },
    nl: {
      heading: 'Maak dit voorbeeld persoonlijk',
      intro: 'Kies een optie om een e-mail te beginnen.',
      pyramid: 'Illustratief voorstel voor een QR-piramide op tafel.',
      generatedCaption: 'AI-illustratie; geen foto van de gerechten of het restaurant.',
      generatedAlt: 'AI-illustratie van eten; toont geen echte gerechten of ruimtes van het restaurant.',
      note: 'Er wordt een e-mail geopend voor info@web-by-elie.com.',
      subject: 'Menukaartvoorbeeld',
      body: 'Hallo, ik heb interesse in',
      labels: {
        complete: 'Menu aanvullen',
        languages: 'Meer talen toevoegen',
        prices: 'Prijzen bijwerken',
        pyramids: 'QR-piramides bestellen',
      },
    },
    ru: {
      heading: 'Настройте этот образец',
      intro: 'Выберите действие, чтобы начать письмо.',
      pyramid: 'Иллюстративный макет QR-пирамиды для стола.',
      generatedCaption: 'Иллюстрация, созданная ИИ; это не фотография блюд или интерьера ресторана.',
      generatedAlt: 'Иллюстрация еды, созданная ИИ; она не показывает реальные блюда или помещения ресторана.',
      note: 'Откроется письмо на info@web-by-elie.com.',
      subject: 'Образец меню',
      body: 'Здравствуйте, меня интересует',
      labels: {
        complete: 'Дополнить меню',
        languages: 'Добавить языки',
        prices: 'Обновить цены',
        pyramids: 'Заказать QR-пирамиды',
      },
    },
  };

  const section = document.querySelector('[data-sample-actions]');
  if (!section) return;

  const menuData = JSON.parse(document.getElementById('data').textContent);
  const restaurant = menuData.title;

  function updateActions() {
    const locale = copy[document.documentElement.lang] ? document.documentElement.lang : 'es';
    const strings = copy[locale];
    section.querySelector('[data-actions-heading]').textContent = strings.heading;
    section.querySelector('[data-actions-intro]').textContent = strings.intro;
    section.querySelector('[data-pyramid-caption]').textContent = strings.pyramid;
    section.querySelector('[data-contact-note]').textContent = strings.note;
    const pyramidImage = section.querySelector('[data-pyramid-image]');
    if (pyramidImage) pyramidImage.alt = strings.pyramid;
    document.querySelectorAll('figcaption[data-caption="generated"]').forEach((caption) => {
      caption.textContent = strings.generatedCaption;
      const figure = caption.closest('figure');
      figure?.querySelectorAll('img').forEach((image) => { image.alt = strings.generatedAlt; });
      figure?.querySelectorAll('svg[role="img"]').forEach((image) => { image.setAttribute('aria-label', strings.generatedAlt); });
    });
    document.querySelectorAll('[data-generated-image]').forEach((image) => {
      image.alt = strings.generatedAlt;
    });

    for (const link of section.querySelectorAll('[data-action]')) {
      const action = link.dataset.action;
      const label = strings.labels[action];
      link.textContent = label;
      const subject = `${strings.subject}: ${label} — ${restaurant}`;
      const body = `${strings.body}: ${label}\n\n${restaurant}\n${section.dataset.sampleUrl}`;
      link.href = `mailto:info@web-by-elie.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      link.setAttribute('aria-label', `${label} — info@web-by-elie.com`);
    }
  }

  updateActions();
  new MutationObserver(updateActions).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['lang'],
  });
})();
