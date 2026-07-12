/**
 * Image de fond par page (Unsplash — thème hospitalier).
 * Utilisé par App.vue via la variable CSS --page-bg-image.
 */
const U = (id, w = 1920) =>
  `https://images.unsplash.com/${id}?w=${w}&q=80&auto=format&fit=crop`

const DEFAULT_BG = U('photo-1519494026892-80bbd2d6fd0d')

export const PAGE_BACKGROUNDS = {
  '/': U('photo-1576091160399-112ba8d25d1f'),
  '/admin': U('photo-1551288049-bebda4e38f71'),
  '/users': U('photo-1551836022-d5d88e9c7269'),
  '/reports': U('photo-1551288049-bebda4e38f71'),
  '/journal': U('photo-1454165804606-c3d57bc86b40'),
  '/settings': U('photo-1519494026892-80bbd2d6fd0d'),
  '/personnel': U('photo-1576091160399-112ba8d25d1f'),
  '/mon-espace': U('photo-1579684385127-eb371025b023'),
  '/patients': U('photo-1631217868264-e1b98b5938d1'),
  '/reception': U('photo-1516576228448-0f4c2d4c8d4e'),
  '/waiting-room': U('photo-1581594693702-7994383e021e'),
  '/urgence': U('photo-1579154200461-988b9d0ffed6'),
  '/consultations': U('photo-1559839734-2b71ea197ec2'),
  '/doctors': U('photo-1629909613654-28e377c01b9d'),
  '/nurses': U('photo-1579684385127-eb371025b023'),
  '/agenda': U('photo-1506784365847-1b12f28a8b27'),
  '/ordonnances': U('photo-1584308666744-24d5c474f2ae'),
  '/departments': U('photo-1486304879800-b36687bb0b7a'),
  '/admissions': U('photo-1516549656594-ffeb4e8081f0'),
  '/rooms': U('photo-1551190822-959c6b750f9a'),
  '/localisation': U('photo-1524661135-423995f22d0b'),
  '/lab': U('photo-1532187863486-abf9fa341ca7'),
  '/blood-bank': U('photo-1615485924510-b6e8f3d61be7'),
  '/pharmacy': U('photo-1587854697752-949d3e7a7e8f'),
  '/bills': U('photo-1554224155-6726b3ff858f'),
  '/payments': U('photo-1563013544-824ae1b704d3'),
  '/insurance': U('photo-1450101499163-c8848c66ca85'),
  '/privileged': U('photo-1560472354-b33ff0c44a43'),
  '/bank': U('photo-1601597111158-87fce6a97c39'),
  '/about': U('photo-1486312338219-ce68d2c6f44d'),
  '/login': U('photo-1559839734-2b71ea197ec2'),
}

/** Préfixes pour routes dynamiques (ex. /patients/12) */
const PREFIX_BACKGROUNDS = [
  { prefix: '/patients/', image: U('photo-1576091160550-0b757a68bb9e') },
]

export function getPageBackground(path) {
  if (!path) return DEFAULT_BG
  if (PAGE_BACKGROUNDS[path]) return PAGE_BACKGROUNDS[path]
  for (const { prefix, image } of PREFIX_BACKGROUNDS) {
    if (path.startsWith(prefix) && path !== '/patients') return image
  }
  return DEFAULT_BG
}
