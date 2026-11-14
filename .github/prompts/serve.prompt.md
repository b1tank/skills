---
name: serve
description: Serve the current artifact or approved app in the shared LAN portal (0.0.0.0:12345), returning phone-ready links.
argument-hint: "[file-or-folder ... | --live folder | --app local-url --name title | --list]"
---

Read and follow `~/.agents/skills/serve/SKILL.md` (resolve `~` to the user's home). This is the single serving workflow; do not create a separate ad-hoc HTTP server for static output.

Use the invocation input as the artifact paths/options or app request. With no input, select the clearly identified output from the current conversation; if there is none, ensure/show the portal. Ask only if the intended output is ambiguous.

Default to `0.0.0.0:12345`, preserve the shared artifact library and existing publications, and return both an artifact/app link and the LAN portal bookmark. Do not ask the user to repeat bind addresses. Do not assume an HTML file requiring backend APIs becomes a working app by copying it.
