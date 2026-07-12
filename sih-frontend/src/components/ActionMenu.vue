<template>
  <div class="relative inline-block">
    <button
      ref="btnRef"
      type="button"
      @click.stop="toggle"
      class="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white"
      aria-label="Actions"
    >
      ⋮
    </button>

    <Teleport to="body">
      <div v-if="open" class="fixed inset-0 z-[200]" @click="close" />
      <div
        v-if="open"
        ref="menuRef"
        class="fixed z-[201] min-w-[200px] max-w-[min(280px,calc(100vw-16px))] py-1 rounded-xl bg-slate-800 border border-white/10 shadow-2xl max-h-[min(70vh,320px)] overflow-y-auto"
        :style="menuStyle"
      >
        <button
          v-for="item in items"
          :key="item.key"
          type="button"
          @click="select(item)"
          class="w-full text-left px-4 py-2.5 text-sm hover:bg-white/5 flex items-center gap-2 whitespace-nowrap"
          :class="item.danger ? 'text-red-400' : 'text-slate-300'"
        >
          <span class="shrink-0">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

defineProps({
  items: { type: Array, default: () => [] },
})

const emit = defineEmits(['action'])
const open = ref(false)
const btnRef = ref(null)
const menuRef = ref(null)
const menuStyle = ref({ top: '0px', left: '0px' })

function close() {
  open.value = false
}

function updatePosition() {
  const btn = btnRef.value
  if (!btn) return

  const rect = btn.getBoundingClientRect()
  const menuWidth = 200
  const gap = 6
  const estimatedHeight = Math.min(320, (menuRef.value?.offsetHeight || 140))

  let top = rect.bottom + gap
  let left = rect.right - menuWidth

  if (left < 8) left = 8
  if (left + menuWidth > window.innerWidth - 8) {
    left = window.innerWidth - menuWidth - 8
  }

  if (top + estimatedHeight > window.innerHeight - 8) {
    top = rect.top - estimatedHeight - gap
  }
  if (top < 8) top = 8

  menuStyle.value = {
    top: `${top}px`,
    left: `${left}px`,
  }
}

function toggle() {
  open.value = !open.value
  if (open.value) {
    requestAnimationFrame(() => {
      updatePosition()
      requestAnimationFrame(updatePosition)
    })
  }
}

function select(item) {
  close()
  emit('action', item.key)
}

function onScrollOrResize() {
  if (open.value) updatePosition()
}

onMounted(() => {
  window.addEventListener('scroll', onScrollOrResize, true)
  window.addEventListener('resize', onScrollOrResize)
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScrollOrResize, true)
  window.removeEventListener('resize', onScrollOrResize)
})
</script>
