<template>
  <NuxtPage />
</template>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #0a0a0f;
  --surface: #111118;
  --border: #1e1e2e;
  --border-hover: #313145;
  --text: #cdd6f4;
  --muted: #6c7086;
  --accent: #89b4fa;
  --green: #a6e3a1;
  --red: #f38ba8;
  --yellow: #f9e2af;
  --orange: #fab387;
  --mono: 'JetBrains Mono', 'Fira Code', monospace;
}

body {
  font-family: system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.6;
}

a { color: inherit; text-decoration: none; }
button { cursor: pointer; font-family: inherit; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
