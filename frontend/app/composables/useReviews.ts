export const useReviews = () => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase

  const reviews = ref([])
  const loading = ref(false)

  const fetchReviews = async () => {
    loading.value = true
    try {
      const data = await $fetch(`${base}/api/reviews`)
      reviews.value = data
    } finally {
      loading.value = false
    }
  }

  const fetchReview = async (id: string) => {
    return await $fetch(`${base}/api/reviews/${id}`)
  }

  return { reviews, loading, fetchReviews, fetchReview }
}
