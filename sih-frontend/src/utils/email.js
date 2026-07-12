/** Extrait une adresse email valide d'une saisie (ex: "MASSASSI emmanuel@sghl.com" → "emmanuel@sghl.com") */
export function extractEmail(input) {
  if (!input || typeof input !== 'string') return ''
  const trimmed = input.trim()
  const match = trimmed.match(/[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}/i)
  return match ? match[0].toLowerCase() : trimmed.toLowerCase()
}

export function isValidEmail(email) {
  return /^[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}$/.test(email || '')
}
