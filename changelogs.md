---
title: Changelog
description: Even the best need some changes sometimes
layout: default
---

# Changelogs
{% for post in site.posts %}
  - [{{ post.version | default: post.title }} {{ post.released | default: "test"}} {% if post.released  == "no" %}[DEV]{% endif %}]({{ site.url }}{{ post.url }})
{% endfor %}