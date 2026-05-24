<template>
  <div class="shell">

    <!-- Top bar -->
    <header class="topbar">
      <div class="brand">
        <span class="brand-icon">◈</span>
        <span class="brand-name">coderev</span>
        <span class="brand-tag">ai</span>
      </div>
      <div class="topbar-right">
        <div class="live-dot" :class="{ active: !loading }" />
        <span class="muted">{{ reviews.length }} reviews</span>
        <button class="icon-btn" @click="showSettings = true" title="Settings">⚙</button>
      </div>
    </header>

    <!-- Stats bar -->
    <div class="statsbar" v-if="reviews.length">
      <div class="stat-item">
        <span class="stat-val">{{ reviews.length }}</span>
        <span class="stat-key">total</span>
      </div>
      <div class="divider" />
      <div class="stat-item">
        <span class="stat-val green">{{ completed }}</span>
        <span class="stat-key">completed</span>
      </div>
      <div class="divider" />
      <div class="stat-item">
        <span class="stat-val red">{{ critical }}</span>
        <span class="stat-key">critical</span>
      </div>
      <div class="divider" />
      <div class="stat-item">
        <span class="stat-val accent">{{ totalFindings }}</span>
        <span class="stat-key">findings</span>
      </div>
      <div class="divider" />
      <div class="stat-item">
        <span class="stat-val mono">{{ currentModel }}</span>
        <span class="stat-key">model</span>
      </div>
    </div>

    <!-- Review list -->
    <main class="main">
      <div v-if="loading && !reviews.length" class="empty">
        <span class="pulse">●</span> waiting for reviews...
      </div>

      <div v-else-if="!reviews.length" class="empty">
        no reviews yet — open a PR on
        <span class="mono accent">{{ currentRepo || 'configured repo' }}</span>
      </div>

      <div class="review-list" v-else>
        <NuxtLink
          v-for="r in reviews"
          :key="r.id"
          :to="`/reviews/${r.id}`"
          class="review-row"
        >
          <div class="row-left">
            <span class="status-dot" :class="r.status" />
            <div class="row-info">
              <span class="row-title">{{ r.pr_title }}</span>
              <span class="row-meta mono">
                {{ r.repo_full_name }} · #{{ r.pr_number }} · {{ r.pr_author }}
              </span>
            </div>
          </div>
          <div class="row-right">
            <span v-if="r.findings?.length" class="badge-findings">
              {{ r.findings.length }} issues
            </span>
            <span v-else class="badge-clean">clean</span>
            <span class="row-time muted">{{ timeAgo(r.created_at) }}</span>
            <span class="chevron muted">›</span>
          </div>
        </NuxtLink>
      </div>
    </main>

    <!-- Settings modal -->
    <div class="modal-overlay" v-if="showSettings" @click.self="showSettings = false">
      <div class="modal">
        <div class="modal-header">
          <span>Settings</span>
          <button class="icon-btn" @click="showSettings = false">✕</button>
        </div>

        <div class="modal-body">
          <label class="field">
            <span class="field-label">Target Repository</span>
            <span class="field-hint">Format: owner/repo</span>
            <input
              v-model="configForm.repo"
              class="input"
              placeholder="e.g. profz/my-project"
            />
          </label>

          <label class="field">
            <span class="field-label">LLM Model</span>
            <span class="field-hint">Affects analysis quality vs speed</span>
            <select v-model="configForm.model" class="input">
              <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
            </select>
          </label>
        </div>

        <div class="modal-footer">
          <button class="btn-ghost" @click="showSettings = false">Cancel</button>
          <button class="btn-primary" @click="saveConfig" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
const { reviews, loading, fetchReviews } = useReviews()
const config = useRuntimeConfig()
const base = config.public.apiBase

const showSettings = ref(false)
const saving = ref(false)
const models = ref([])
const configForm = ref({ repo: '', model: 'llama-3.3-70b-versatile' })
const currentRepo = ref('')
const currentModel = ref('')

const completed = computed(() => reviews.value.filter(r => r.status === 'completed').length)
const totalFindings = computed(() => reviews.value.reduce((acc, r) => acc + (r.findings?.length || 0), 0))
const critical = computed(() =>
  reviews.value.flatMap(r => r.findings || []).filter(f => f.severity === 'critical').length
)

const timeAgo = (ts) => {
  const diff = Date.now() - new Date(ts)
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

const loadConfig = async () => {
  const [cfg, mdls] = await Promise.all([
    $fetch(`${base}/api/config/`),
    $fetch(`${base}/api/config/models`),
  ])
  configForm.value = { repo: cfg.repo, model: cfg.model }
  currentRepo.value = cfg.repo
  currentModel.value = cfg.model.split('-').slice(0, 2).join('-')
  models.value = mdls.models
}

const saveConfig = async () => {
  saving.value = true
  await $fetch(`${base}/api/config/`, {
    method: 'PUT',
    body: configForm.value,
  })
  currentRepo.value = configForm.value.repo
  currentModel.value = configForm.value.model.split('-').slice(0, 2).join('-')
  saving.value = false
  showSettings.value = false
}

onMounted(() => {
  fetchReviews()
  loadConfig()
})

const interval = setInterval(fetchReviews, 5000)
onUnmounted(() => clearInterval(interval))
</script>

<style scoped>
.shell { min-height: 100vh; display: flex; flex-direction: column; }

/* Topbar */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.75rem 2rem;
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; background: var(--bg); z-index: 10;
}
.brand { display: flex; align-items: center; gap: 0.5rem; }
.brand-icon { color: var(--accent); font-size: 1.1rem; }
.brand-name { font-weight: 700; letter-spacing: -0.02em; }
.brand-tag {
  font-size: 0.65rem; background: var(--accent); color: var(--bg);
  padding: 1px 5px; border-radius: 3px; font-weight: 700; text-transform: uppercase;
}
.topbar-right { display: flex; align-items: center; gap: 1rem; }
.live-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--muted);
  transition: background 0.3s;
}
.live-dot.active { background: var(--green); box-shadow: 0 0 6px var(--green); }
.icon-btn {
  background: none; border: none; color: var(--muted);
  font-size: 1rem; padding: 4px; border-radius: 4px;
  transition: color 0.2s;
}
.icon-btn:hover { color: var(--text); }

/* Stats bar */
.statsbar {
  display: flex; align-items: center; gap: 1.5rem;
  padding: 0.6rem 2rem;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}
.stat-item { display: flex; align-items: baseline; gap: 0.4rem; }
.stat-val { font-size: 1rem; font-weight: 700; }
.stat-key { font-size: 0.75rem; color: var(--muted); }
.divider { width: 1px; height: 16px; background: var(--border); }
.green { color: var(--green); }
.red { color: var(--red); }
.accent { color: var(--accent); }
.mono { font-family: var(--mono); font-size: 0.8rem; }

/* Main */
.main { flex: 1; padding: 1.5rem 2rem; max-width: 900px; width: 100%; margin: 0 auto; }

.empty { color: var(--muted); padding: 3rem 0; text-align: center; }
.pulse { animation: pulse 1.5s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* Review rows */
.review-list { display: flex; flex-direction: column; gap: 2px; }
.review-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.9rem 1rem;
  border-radius: 6px;
  border: 1px solid transparent;
  transition: background 0.15s, border-color 0.15s;
  cursor: pointer;
}
.review-row:hover {
  background: var(--surface);
  border-color: var(--border);
}
.row-left { display: flex; align-items: center; gap: 0.75rem; min-width: 0; }
.status-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.status-dot.completed { background: var(--green); }
.status-dot.pending { background: var(--yellow); }
.status-dot.processing { background: var(--accent); animation: pulse 1s infinite; }
.status-dot.failed { background: var(--red); }

.row-info { display: flex; flex-direction: column; min-width: 0; }
.row-title { font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.row-meta { font-size: 0.75rem; color: var(--muted); margin-top: 1px; }

.row-right { display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0; }
.badge-findings {
  font-size: 0.72rem; padding: 2px 7px; border-radius: 10px;
  background: rgba(243, 139, 168, 0.15); color: var(--red);
  font-weight: 600;
}
.badge-clean {
  font-size: 0.72rem; padding: 2px 7px; border-radius: 10px;
  background: rgba(166, 227, 161, 0.15); color: var(--green);
  font-weight: 600;
}
.row-time { font-size: 0.75rem; }
.chevron { font-size: 1rem; }
.muted { color: var(--muted); }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.7);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
}
.modal {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; width: 420px; overflow: hidden;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 1.25rem; border-bottom: 1px solid var(--border);
  font-weight: 600;
}
.modal-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 1.25rem; }
.modal-footer {
  padding: 1rem 1.25rem; border-top: 1px solid var(--border);
  display: flex; justify-content: flex-end; gap: 0.75rem;
}

.field { display: flex; flex-direction: column; gap: 0.3rem; }
.field-label { font-size: 0.85rem; font-weight: 500; }
.field-hint { font-size: 0.75rem; color: var(--muted); }
.input {
  background: var(--bg); border: 1px solid var(--border);
  border-radius: 6px; padding: 0.5rem 0.75rem;
  color: var(--text); font-size: 0.875rem; font-family: inherit;
  outline: none; transition: border-color 0.2s;
  width: 100%;
}
.input:focus { border-color: var(--accent); }

.btn-ghost {
  background: none; border: 1px solid var(--border);
  color: var(--muted); padding: 0.45rem 1rem;
  border-radius: 6px; font-size: 0.85rem;
  transition: border-color 0.2s, color 0.2s;
}
.btn-ghost:hover { border-color: var(--text); color: var(--text); }
.btn-primary {
  background: var(--accent); border: none; color: var(--bg);
  padding: 0.45rem 1rem; border-radius: 6px;
  font-size: 0.85rem; font-weight: 600;
  transition: opacity 0.2s;
}
.btn-primary:disabled { opacity: 0.5; }
.btn-primary:hover:not(:disabled) { opacity: 0.85; }
</style>
