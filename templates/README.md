# Django Templates

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Overview

Django HTML templates and template files used for server-side rendering and email templates. Templates are organised by app and include base templates for inheritance, model-specific templates for CRUD operations, and email templates for transactional messages.

## Table of Contents

- [Overview](#overview)
- [Template Organization](#template-organization)
- [Template Tags and Filters](#template-tags-and-filters)
- [Best Practices](#best-practices)

---

## Template Organization

```
templates/
├── base.html              # Base template extended by others
├── home.html              # Home page template
├── [app_name]/            # App-specific templates
│   ├── [model]_list.html
│   ├── [model]_detail.html
│   └── [model]_form.html
└── email/                 # Email templates
    ├── welcome.html
    └── confirmation.html
```

---

## Template Tags and Filters

### Load Static Files

```html
{% load static %}

<img src="{% static 'images/logo.png' %}" alt="Logo" />
<link rel="stylesheet" href="{% static 'css/style.css' %}" />
```

### Common Tags

```html
{% for item in items %}
<li>{{ item.name }}</li>
{% endfor %} {% if user.is_authenticated %} Welcome, {{ user.username }}! {% else %} Please log in.
{% endif %} {% include "components/header.html" %}
```

### Common Filters

```html
{{ text|upper }} {# Convert to uppercase #} {{ price|floatformat:2 }} {# Format decimal places #} {{
date|date:"Y-m-d" }} {# Format date #} {{ items|length }} {# Count items #} {{ text|truncatewords:10
}} {# Truncate text #}
```

---

## Best Practices

1. **Extend Base Template:** All templates should extend `base.html`
2. **Use Template Blocks:** Define reusable blocks in base template
3. **Load Static Files:** Use `{% static %}` tag for static files
4. **Escape Variables:** Automatic (unless using `|safe` filter)
5. **Comments:** Use `{# comment #}` for documentation
6. **Formatting:** Keep templates readable with proper indentation

### Example Template

```html
{% extends "base.html" %} {% load static %} {% block title %}My Page{% endblock %} {% block content
%}
<h1>{{ title }}</h1>

{% for item in items %}
<div class="item">
  <h2>{{ item.name }}</h2>
  <p>{{ item.description }}</p>
</div>
{% empty %}
<p>No items available.</p>
{% endfor %} {% endblock %}
```

---

## Related Documentation

- [Django Templates](https://docs.djangoproject.com/en/5.2/topics/templates/) - Official Django template docs
- [Template Tags](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/) - Built-in template tags and filters

---

**Last Updated:** 2026-01-03
