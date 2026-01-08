# Static Files

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Static CSS, JavaScript, and image assets served by the web server.

## Table of Contents

- [Static Files](#static-files)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Using Static Files](#using-static-files)
    - [In Templates](#in-templates)
    - [In CSS](#in-css)
  - [Best Practices](#best-practices)
  - [Collecting Static Files](#collecting-static-files)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains static files (CSS, JavaScript, images) served directly by Nginx in production or by Django in development.

**Best Practice:** Static files are compiled and minified before deployment.

---

## Directory Structure

```
static/
├── css/                   # Stylesheets
│   ├── style.css
│   └── responsive.css
├── js/                    # JavaScript files
│   ├── main.js
│   └── utils.js
├── images/                # Image assets
│   ├── logo.png
│   └── icons/
├── fonts/                 # Custom fonts
└── vendor/                # Third-party libraries
    ├── bootstrap.css
    └── jquery.js
```

---

## Using Static Files

### In Templates

```html
{% load static %}

<!-- Link stylesheet -->
<link rel="stylesheet" href="{% static 'css/style.css' %}" />

<!-- Image -->
<img src="{% static 'images/logo.png' %}" alt="Logo" />

<!-- Script -->
<script src="{% static 'js/main.js' %}"></script>
```

### In CSS

```css
/* Reference images in CSS */
.background {
  background-image: url('/static/images/bg.jpg');
}
```

---

## Best Practices

1. **Use Static Tag:** Always use `{% static %}` tag in templates
2. **Organize by Type:** Group files by CSS, JS, images
3. **Minify in Production:** Minify CSS and JavaScript before deployment
4. **Use CDN:** Consider CDN for large files (images, fonts)
5. **Cache Busting:** Use versioned filenames for cache busting
6. **Compress:** Enable gzip compression for assets

---

## Collecting Static Files

```bash
# Collect static files into single directory
./scripts/env/dev.sh collectstatic

# In Docker
docker compose -f docker/dev/docker-compose.yml exec web \
  python manage.py collectstatic --noinput
```

---

## Related Documentation

- [Django Static Files](https://docs.djangoproject.com/en/5.2/howto/static-files/) - Official Django docs
- [Whitenoise](http://whitenoise.evans.io/) - Static file serving package

---

**Last Updated:** 2026-01-03
