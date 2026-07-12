<template>
  <div class="map-wrapper relative">
    <div ref="mapEl" class="hospital-map" :style="{ height }"></div>
    <div v-if="loading" class="map-loading">
      <div class="map-spinner"></div>
      <span>Chargement de la carte...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  markers: { type: Array, default: () => [] },
  center: { type: Array, default: () => [-4.7692, 11.8664] },
  zoom: { type: Number, default: 18 },
  height: { type: String, default: '520px' },
  selectedId: { type: [Number, String, null], default: null },
  animate: { type: Boolean, default: true },
})

const emit = defineEmits(['marker-click'])

const mapEl = ref(null)
const loading = ref(true)

let map = null
let tileLayer = null
const markerRegistry = new Map()
let animFrame = null

function pinHtml(color, selected = false) {
  const size = selected ? 48 : 40
  const pulse = selected ? `<div class="pin-pulse" style="background:${color}"></div>` : ''
  return `
    <div class="pin-wrap" style="width:${size}px;height:${size}px">
      ${pulse}
      <svg viewBox="0 0 24 36" width="${size}" height="${size * 1.2}" style="filter:drop-shadow(0 4px 8px rgba(0,0,0,.35))">
        <path fill="${color}" stroke="#fff" stroke-width="1.5"
          d="M12 0C5.4 0 0 5.4 0 12c0 9 12 24 12 24s12-15 12-24C24 5.4 18.6 0 12 0z"/>
        <circle fill="#fff" cx="12" cy="12" r="5"/>
      </svg>
    </div>`
}

function makeIcon(color, selected) {
  const size = selected ? 48 : 40
  return L.divIcon({
    className: 'gmaps-pin',
    html: pinHtml(color, selected),
    iconSize: [size, size * 1.2],
    iconAnchor: [size / 2, size * 1.2],
    popupAnchor: [0, -size * 1.1],
  })
}

function easeInOut(t) {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2
}

function animateLatLng(from, to, duration, onUpdate, onDone) {
  const start = performance.now()
  if (animFrame) cancelAnimationFrame(animFrame)
  function step(now) {
    const t = Math.min((now - start) / duration, 1)
    const e = easeInOut(t)
    const lat = from.lat + (to.lat - from.lat) * e
    const lng = from.lng + (to.lng - from.lng) * e
    onUpdate({ lat, lng })
    if (t < 1) animFrame = requestAnimationFrame(step)
    else onDone?.()
  }
  animFrame = requestAnimationFrame(step)
}

function popupContent(m) {
  return `
    <div class="gmaps-popup">
      <strong>${m.patient_nom || 'Patient'}</strong>
      <span class="sub">${m.patient_sgl_id || ''}</span>
      <span class="badge">${m.statut_label || m.statut || ''}</span>
      <p>${m.batiment || ''} · ${m.etage || ''}</p>
      <p>${m.salle || ''}</p>
    </div>`
}

function initMap() {
  if (!mapEl.value || map) return

  map = L.map(mapEl.value, {
    center: props.center,
    zoom: props.zoom,
    zoomControl: false,
    attributionControl: true,
  })

  L.control.zoom({ position: 'bottomright' }).addTo(map)

  tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; CARTO',
    maxZoom: 20,
    subdomains: 'abcd',
  }).addTo(map)

  loading.value = false
  syncMarkers(false)
  setTimeout(() => map?.invalidateSize(), 300)
}

function markerColor(m) {
  if (props.selectedId != null && m.id === props.selectedId) return '#ea4335'
  const colors = { EN_CONSULTATION: '#4285f4', HOSPITALISE: '#9334e6', EXAMEN: '#fbbc04', EN_ATTENTE: '#34a853' }
  return colors[m.statut] || '#0d9488'
}

function syncMarkers(animated = true) {
  if (!map) return

  const seen = new Set()
  const bounds = []

  props.markers.forEach((m) => {
    const lat = m.latitude ?? props.center[0]
    const lng = m.longitude ?? props.center[1]
    const target = L.latLng(lat, lng)
    bounds.push(target)
    seen.add(m.id)

    const selected = props.selectedId != null && m.id === props.selectedId
    const color = markerColor(m)
    const icon = makeIcon(color, selected)

    if (markerRegistry.has(m.id)) {
      const entry = markerRegistry.get(m.id)
      entry.data = m
      entry.marker.setIcon(icon)
      entry.marker.setPopupContent(popupContent(m))

      const current = entry.marker.getLatLng()
      if (animated && props.animate && (Math.abs(current.lat - lat) > 0.00001 || Math.abs(current.lng - lng) > 0.00001)) {
        animateLatLng(current, target, 900, (pos) => entry.marker.setLatLng(pos))
      } else {
        entry.marker.setLatLng(target)
      }
    } else {
      const marker = L.marker(target, { icon })
      marker.bindPopup(popupContent(m), { className: 'gmaps-popup-wrap', maxWidth: 260 })
      marker.on('click', () => emit('marker-click', m))
      marker.addTo(map)
      markerRegistry.set(m.id, { marker, data: m })
    }
  })

  markerRegistry.forEach((entry, id) => {
    if (!seen.has(id)) {
      map.removeLayer(entry.marker)
      markerRegistry.delete(id)
    }
  })

  if (props.selectedId != null) {
    const sel = props.markers.find(m => m.id === props.selectedId)
    if (sel) {
      flyTo(sel.latitude ?? props.center[0], sel.longitude ?? props.center[1], props.zoom)
      const entry = markerRegistry.get(sel.id)
      entry?.marker.openPopup()
    }
  } else if (bounds.length > 1) {
    map.fitBounds(L.latLngBounds(bounds), { padding: [50, 50], maxZoom: 18, animate: true, duration: 1 })
  }
}

function flyTo(lat, lng, zoom = props.zoom) {
  if (!map) return
  map.flyTo([lat, lng], zoom, { animate: true, duration: 1.2, easeLinearity: 0.25 })
}

watch(() => props.markers, () => syncMarkers(true), { deep: true })
watch(() => props.selectedId, () => syncMarkers(true))

onMounted(initMap)

onUnmounted(() => {
  if (animFrame) cancelAnimationFrame(animFrame)
  markerRegistry.forEach(({ marker }) => map?.removeLayer(marker))
  markerRegistry.clear()
  map?.remove()
  map = null
})

defineExpose({ flyTo, syncMarkers })
</script>

<style>
.map-wrapper { position: relative; border-radius: 1rem; overflow: hidden; }
.hospital-map {
  width: 100%;
  background: #e8eaed;
  font-family: 'Google Sans', system-ui, sans-serif;
  z-index: 0;
}
.map-loading {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 0.75rem;
  background: rgba(30,41,59,.85); color: #94a3b8; font-size: 0.875rem; z-index: 10;
}
.map-spinner {
  width: 32px; height: 32px; border: 3px solid rgba(255,255,255,.15);
  border-top-color: #0d9488; border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.gmaps-pin { background: transparent !important; border: none !important; }
.pin-wrap { position: relative; display: flex; align-items: center; justify-content: center; }
.pin-pulse {
  position: absolute; width: 100%; height: 100%; border-radius: 50%;
  opacity: 0.35; animation: pinPulse 1.8s ease-out infinite;
}
@keyframes pinPulse {
  0% { transform: scale(0.6); opacity: 0.5; }
  100% { transform: scale(2.2); opacity: 0; }
}

.gmaps-popup-wrap .leaflet-popup-content-wrapper {
  border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,.18); padding: 0;
}
.gmaps-popup-wrap .leaflet-popup-content { margin: 12px 14px; }
.gmaps-popup strong { display: block; font-size: 14px; color: #202124; }
.gmaps-popup .sub { font-size: 11px; color: #5f6368; }
.gmaps-popup .badge {
  display: inline-block; margin-top: 6px; padding: 2px 8px; border-radius: 999px;
  background: #e6f4ea; color: #137333; font-size: 11px; font-weight: 500;
}
.gmaps-popup p { margin: 4px 0 0; font-size: 12px; color: #3c4043; }

.leaflet-control-zoom {
  border: none !important; box-shadow: 0 2px 8px rgba(0,0,0,.2) !important; border-radius: 8px !important;
}
.leaflet-control-zoom a {
  background: #fff !important; color: #3c4043 !important; border: none !important;
  width: 36px !important; height: 36px !important; line-height: 36px !important; font-size: 18px !important;
}
.leaflet-control-zoom a:first-child { border-radius: 8px 8px 0 0 !important; }
.leaflet-control-zoom a:last-child { border-radius: 0 0 8px 8px !important; }
</style>
