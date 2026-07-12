import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPageFlowContext } from '../config/navigation.js'
import { getAutoAdvance } from '../utils/redirectConfig.js'
import { getUser } from '../services/api.js'

export function usePageFlow() {
  const route = useRoute()
  const router = useRouter()

  const flow = computed(() => getPageFlowContext(route.path, getUser()))

  function goPrev() {
    if (flow.value.prev) router.push(flow.value.prev.path)
  }

  function goNext() {
    if (flow.value.next) router.push(flow.value.next.path)
  }

  /** Après une action réussie — avance si l'option admin est activée. */
  function goNextIfAuto() {
    if (getAutoAdvance() && flow.value.next) router.push(flow.value.next.path)
  }

  return { flow, goPrev, goNext, goNextIfAuto }
}
