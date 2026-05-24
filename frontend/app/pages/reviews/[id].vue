<template>
  <div class="shell">
    <header class="topbar">
      <NuxtLink to="/" class="back">‹ back</NuxtLink>
      <div class="pr-head" v-if="review">
        <span class="mono muted">{{ review.repo_full_name }} · #{{ review.pr_number }}</span>
        <span class="status-pill" :class="review.status">{{ review.status }}</span>
      </div>
    </header>

    <div v-if="loading" class="empty">loading...</div>

    <main class="main" v-else-if="review">
      <h1 class="pr-title">{{ review.pr_title }}</h1>
      <div class="pr-meta mono muted">by {{ review.pr_author }}</div>

      <!-- Severity summary strip -->
      <div class="severity-strip">
        <div class="sev-block critical" v-if="bySeverity.critical">
          <span class="sev-count">{{ bySeverity.critical }}</span>
          <span class="sev-label">critical</span>
        </div>
        <div class="sev-block high" v-if="bySeverity.high">
          <span class="sev-count">{{ bySeverity.high }}</span>
          <span class="sev-label">high</span>
        </div>
        <div class="sev-block medium" v-if="bySeverity.medium">
          <span class="sev-count">{{ bySeverity.medium }}</span>
          <span class="sev-label">medium</span>
        </div>
        <div class="sev-block low" v-if="bySeverity.low">
          <span class="sev-count">{{ bySeverity.low }}</span>
          <span class="sev-label">low</span>
        </div>
        <div class="sev-clean" v-if="!review.findings?.length">✓ no issues found</div>
      </div>

      <!-- Summary -->
      <section class="section" v-if="review.summary">
        <div class="section-label">summary</div>
        <div class="summary-box" v-html="renderedSummary" />
      </section>

      <!-- Findings grouped by category -->
      <section class="section" v-for="cat in activeCats" :key="cat">
        <div class="section-label">{{ catIcon(cat) }} {{ cat }}</div>
        <div class="finding-list">
          <div class="finding" v-for="f in byCategory(cat)" :key="f.id">
            <div class="finding-top">
              <span class="sev-tag" :class="f.severity">{{ f.severity }}</span>
              <span class="filepath mono">{{ f.file_path }}<span class="line" v-if="f.line_number">:{{ f.line_number }}</span></span>
            </div>
            <div class="finding-msg">{{ f.message }}</div>
            <div class="finding-fix">→ {{ f.suggestion }}</div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { marked } from 'marked'
const route = useRoute()
const { fetchReview } = useReviews()

const review = ref(null)
const loading = ref(true)

onMounted(async () => {
  review.value = await fetchReview(route.params.id)
  loading.value = false
})

const renderedSummary = computed(() =>
  review.value?.summary ? marked(review.value.summary) : ''
)

const categories = ['bug', 'security', 'performance', 'smell']
const activeCats = computed(() =>
  categories.filter(c => byCategory(c).length > 0)
)
const byCategory = (cat) =>
  review.value?.findings?.filter(f => f.category === cat) || []

const bySeverity = computed(() => {
  const f = review.value?.findings || []
  return {
    critical: f.filter(x => x.severity === 'critical').length,
    high:     f.filter(x => x.severity === 'high').length,
    medium:   f.filter(x => x.severity === 'medium').length,
    low:      f.filter(x => x.severity === 'low').length,
  }
})

const catIcon = (c) => ({ bug: '🐛', security: '🔒', performance: '⚡', smell: '🧹' })[c]
</script>

<style scoped>
.shell { min-height: 100vh; }
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.75rem 2rem; border-bottom: 1px solid var(--border);
  position: sticky; top: 0; background: var(--bg); z-index: 10;
}
.back { color: var(--muted); font-size: 0.9rem; transition: color 0.2s; }
.back:hover { color: var(--text); }
.pr-head { display: flex; align-items: center; gap: 0.75rem; }

.main { max-width: 820px; margin: 0 auto; padding: 2rem; }
.pr-title { font-size: 1.4rem; font-weight: 700; margin-bottom: 0.25rem; }
.pr-meta { font-size: 0.8rem; margin-bottom: 1.5rem; }

/* Severity strip */
.severity-strip {
  display: flex; gap: 0.5rem; margin-bottom: 2rem; flex-wrap: wrap;
}
.sev-block {
  display: flex; align-items: baseline; gap: 0.3rem;
  padding: 0.4rem 0.75rem; border-radius: 6px; border: 1px solid;
}
.sev-block.critical { background: rgba(243,139,168,0.08); border-color: rgba(243,139,168,0.3); color: var(--red); }
.sev-block.high { background: rgba(250,179,135,0.08); border-color: rgba(250,179,135,0.3); color: var(--orange); }
.sev-block.medium { background: rgba(137,180,250,0.08); border-color: rgba(137,180,250,0.3); color: var(--accent); }
.sev-block.low { background: rgba(108,112,134,0.1); border-color: var(--border); color: var(--muted); }
.sev-count { font-size: 1.1rem; font-weight: 700; }
.sev-label { font-size: 0.75rem; }
.sev-clean { color: var(--green); padding: 0.4rem 0; }

/* Sections */
.section { margin-bottom: 2rem; }
.section-label {
  font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em;
  color: var(--muted); margin-bottom: 0.75rem; font-weight: 600;
}

/* Summary */
.summary-box {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 1.25rem; font-size: 0.875rem; line-height: 1.7;
}
.summary-box :deep(h2) { font-size: 0.95rem; margin: 0.75rem 0 0.4rem; }
.summary-box :deep(h3) { font-size: 0.85rem; margin: 0.5rem 0 0.3rem; color: var(--muted); }
.summary-box :deep(ul) { padding-left: 1.25rem; }
.summary-box :deep(li) { margin-bottom: 0.25rem; }
.summary-box :deep(table) { width: 100%; border-collapse: collapse; margin: 0.5rem 0; }
.summary-box :deep(td), .summary-box :deep(th) { padding: 4px 8px; border: 1px solid var(--border); font-size: 0.8rem; }
.summary-box :deep(strong) { color: var(--text); }

/* Findings */
.finding-list { display: flex; flex-direction: column; gap: 6px; }
.finding {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 6px; padding: 0.9rem 1rem;
  transition: border-color 0.15s;
}
.finding:hover { border-color: var(--border-hover); }
.finding-top { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.4rem; }
.filepath { font-size: 0.78rem; color: var(--muted); }
.line { color: var(--accent); }
.finding-msg { font-size: 0.875rem; margin-bottom: 0.35rem; }
.finding-fix { font-size: 0.8rem; color: var(--muted); }

/* Severity tags */
.sev-tag {
  font-size: 0.68rem; padding: 2px 6px; border-radius: 4px;
  font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;
  flex-shrink: 0;
}
.sev-tag.critical { background: rgba(243,139,168,0.15); color: var(--red); }
.sev-tag.high { background: rgba(250,179,135,0.15); color: var(--orange); }
.sev-tag.medium { background: rgba(137,180,250,0.15); color: var(--accent); }
.sev-tag.low { background: rgba(108,112,134,0.12); color: var(--muted); }

/* Status pill */
.status-pill {
  font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; font-weight: 600;
}
.status-pill.completed { background: rgba(166,227,161,0.15); color: var(--green); }
.status-pill.pending { background: rgba(249,226,175,0.15); color: var(--yellow); }
.status-pill.processing { background: rgba(137,180,250,0.15); color: var(--accent); }
.status-pill.failed { background: rgba(243,139,168,0.15); color: var(--red); }

.empty { color: var(--muted); text-align: center; padding: 3rem; }
.mono { font-family: var(--mono); }
.muted { color: var(--muted); }
</style>
