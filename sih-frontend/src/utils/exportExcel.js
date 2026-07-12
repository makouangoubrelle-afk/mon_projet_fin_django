import * as XLSX from 'xlsx'
import { jsPDF } from 'jspdf'

function formatFcPdf(n) {
  return `${new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(n || 0)} FC`
}

function pdfHeader(doc, title, subtitle) {
  doc.setFontSize(18)
  doc.setTextColor(15, 118, 110)
  doc.text(title, 14, 20)
  doc.setFontSize(10)
  doc.setTextColor(100)
  doc.text(subtitle, 14, 28)
  doc.setTextColor(0)
}

function pdfFooter(doc) {
  doc.setFontSize(8)
  doc.setTextColor(120)
  doc.text('Document généré par SGHL — Système de Gestion Hospitalière', 14, 285)
}

export function exportToExcel(rows, filename, sheetName = 'Données') {
  const ws = XLSX.utils.json_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, sheetName)
  XLSX.writeFile(wb, filename)
}

export function exportFactureExcel(facture) {
  const lignes = [
    { Champ: 'Référence', Valeur: facture.reference },
    { Champ: 'Patient', Valeur: facture.patient_nom },
    { Champ: 'Société', Valeur: facture.societe || '—' },
    { Champ: 'Date', Valeur: facture.date_facture },
    { Champ: 'Total brut', Valeur: facture.montant_total_brut },
    { Champ: 'Part assurance', Valeur: facture.part_assurance },
    { Champ: 'Réduction privilège', Valeur: facture.reduction_privilege },
    { Champ: 'Net patient', Valeur: facture.montant_patient_net },
    { Champ: 'Payé', Valeur: facture.montant_paye },
    { Champ: 'Reste', Valeur: facture.montant_reste },
    { Champ: 'Statut', Valeur: facture.statut },
  ]
  facture.lignes?.forEach((l, i) => {
    lignes.push({ Champ: `Service ${i + 1}`, Valeur: `${l.service} — ${l.montant} FC` })
  })
  facture.paiements?.forEach((p) => {
    lignes.push({ Champ: `Paiement ${p.mode_label}`, Valeur: p.montant })
  })
  exportToExcel(lignes, `facture-${facture.reference}.xlsx`, 'Reçu facturation')
}

export function exportFacturePdf(facture) {
  const doc = new jsPDF()
  pdfHeader(doc, 'SGHL — Reçu de facturation', `Réf. ${facture.reference}  ·  ${facture.date_facture || '—'}`)

  let y = 40
  doc.setFontSize(11)
  doc.text(`Patient : ${facture.patient_nom}`, 14, y)
  y += 8
  if (facture.societe) {
    doc.text(`Société : ${facture.societe}`, 14, y)
    y += 8
  }
  doc.text(`Statut : ${facture.statut}`, 14, y)
  y += 12

  doc.setFontSize(10)
  doc.setFont(undefined, 'bold')
  doc.text('Services', 14, y)
  doc.text('Montant', 160, y)
  doc.setFont(undefined, 'normal')
  y += 6
  doc.line(14, y, 196, y)
  y += 6

  ;(facture.lignes || []).forEach((l, i) => {
    if (y > 250) {
      doc.addPage()
      y = 20
    }
    const lines = doc.splitTextToSize(`${i + 1}. ${l.service}`, 130)
    doc.text(lines, 14, y)
    doc.text(formatFcPdf(l.montant), 160, y)
    y += lines.length * 6 + 2
  })

  y += 4
  doc.line(14, y, 196, y)
  y += 8
  doc.text(`Total brut : ${formatFcPdf(facture.montant_total_brut)}`, 14, y)
  y += 7
  if (facture.part_assurance) {
    doc.text(`Part assurance : ${formatFcPdf(facture.part_assurance)}`, 14, y)
    y += 7
  }
  if (facture.reduction_privilege) {
    doc.text(`Réduction privilège : ${formatFcPdf(facture.reduction_privilege)}`, 14, y)
    y += 7
  }
  doc.text(`Net patient : ${formatFcPdf(facture.montant_patient_net)}`, 14, y)
  y += 7
  doc.setTextColor(22, 163, 74)
  doc.text(`Payé : ${formatFcPdf(facture.montant_paye)}`, 14, y)
  y += 7
  doc.setTextColor(217, 119, 6)
  doc.text(`Reste : ${formatFcPdf(facture.montant_reste)}`, 14, y)
  doc.setTextColor(0)

  if (facture.paiements?.length) {
    y += 10
    doc.setFont(undefined, 'bold')
    doc.text('Paiements enregistrés', 14, y)
    doc.setFont(undefined, 'normal')
    y += 7
    facture.paiements.forEach((p) => {
      doc.text(`• ${p.mode_label} : ${formatFcPdf(p.montant)}`, 14, y)
      y += 6
    })
  }

  pdfFooter(doc)
  doc.save(`facture-${facture.reference}.pdf`)
}

export function exportPatientsExcel(patients) {
  exportToExcel(
    patients.map(p => ({
      'N° identité': p.numero_identite || p.sgl_id,
      'Nom et prénom': `${p.nom} ${p.prenom}`,
      Sexe: p.genre_label,
      GSM: p.telephone,
      Âge: p.age,
      Situation: p.situation_familiale,
      Statut: p.statut_label,
      Adresse: p.adresse,
      Assurance: p.assurance_nom,
      'Groupe sanguin': p.groupe_sanguin,
      Produits: p.nb_produits,
      'Code QR': p.qr_code,
    })),
    `patients-${new Date().toISOString().slice(0, 10)}.xlsx`,
    'Patients',
  )
}

export function exportPatientsPdf(patients) {
  const doc = new jsPDF('landscape')
  const date = new Date().toLocaleDateString('fr-FR')
  pdfHeader(doc, 'SGHL — Liste des patients', `Export du ${date}  ·  ${patients.length} patient(s)`)

  let y = 38
  const cols = [
    { label: 'N° ID', w: 28 },
    { label: 'Nom', w: 45 },
    { label: 'Sexe', w: 18 },
    { label: 'Âge', w: 14 },
    { label: 'Statut', w: 32 },
    { label: 'Téléphone', w: 35 },
    { label: 'Produits', w: 18 },
  ]
  let x = 14
  doc.setFontSize(8)
  doc.setFont(undefined, 'bold')
  cols.forEach((c) => {
    doc.text(c.label, x, y)
    x += c.w
  })
  doc.setFont(undefined, 'normal')
  y += 4
  doc.line(14, y, 283, y)
  y += 6

  patients.forEach((p) => {
    if (y > 190) {
      doc.addPage()
      y = 20
    }
    x = 14
    const row = [
      (p.numero_identite || p.sgl_id || '—').slice(0, 14),
      `${p.nom} ${p.prenom}`.slice(0, 28),
      (p.genre_label || '—').slice(0, 8),
      String(p.age ?? '—'),
      (p.statut_label || '—').slice(0, 18),
      (p.telephone || '—').slice(0, 16),
      String(p.nb_produits ?? 0),
    ]
    row.forEach((val, i) => {
      doc.text(val, x, y)
      x += cols[i].w
    })
    y += 6
  })

  pdfFooter(doc)
  doc.save(`patients-${new Date().toISOString().slice(0, 10)}.pdf`)
}

export function exportOrdonnanceExcel(o) {
  exportToExcel(
    [
      { Champ: 'Patient', Valeur: o.patient_nom },
      { Champ: 'Médecin', Valeur: o.medecin_nom || '—' },
      { Champ: 'Date', Valeur: new Date(o.date_ordonnance).toLocaleString('fr-FR') },
      { Champ: 'Code QR patient', Valeur: o.patient_qr_code || '—' },
      { Champ: 'Médicaments', Valeur: o.medicaments },
      { Champ: 'Instructions', Valeur: o.instructions || '—' },
    ],
    `ordonnance-${o.id}.xlsx`,
    'Ordonnance',
  )
}

export function exportOrdonnancePdf(o) {
  const doc = new jsPDF()
  const dateStr = new Date(o.date_ordonnance).toLocaleString('fr-FR')
  pdfHeader(doc, 'SGHL — Ordonnance médicale', `Réf. ORD-${o.id}  ·  ${dateStr}`)
  doc.setFontSize(12)
  doc.text(`Patient : ${o.patient_nom}`, 14, 42)
  doc.text(`Médecin : ${o.medecin_nom || '—'}`, 14, 50)
  if (o.patient_qr_code) {
    doc.setFontSize(9)
    doc.text(`QR : ${o.patient_qr_code}`, 14, 58)
  }
  doc.setFontSize(11)
  doc.text('Médicaments prescrits :', 14, 72)
  doc.setFontSize(10)
  const medLines = doc.splitTextToSize(o.medicaments || '—', 180)
  doc.text(medLines, 14, 80)
  let y = 80 + medLines.length * 6 + 8
  if (o.instructions) {
    doc.text('Instructions :', 14, y)
    y += 8
    doc.text(doc.splitTextToSize(o.instructions, 180), 14, y)
  }
  doc.setFontSize(8)
  doc.setTextColor(120)
  pdfFooter(doc)
  doc.save(`ordonnance-${o.id}.pdf`)
}

export function exportOrdonnancesListPdf(list) {
  const doc = new jsPDF()
  const date = new Date().toLocaleDateString('fr-FR')
  pdfHeader(doc, 'SGHL — Liste des ordonnances', `Export du ${date}  ·  ${list.length} ordonnance(s)`)

  let y = 38
  doc.setFontSize(8)
  doc.setFont(undefined, 'bold')
  doc.text('Patient', 14, y)
  doc.text('Médecin', 70, y)
  doc.text('Date', 120, y)
  doc.text('Médicaments', 150, y)
  doc.setFont(undefined, 'normal')
  y += 4
  doc.line(14, y, 196, y)
  y += 6

  list.forEach((o) => {
    if (y > 265) {
      doc.addPage()
      y = 20
    }
    const med = (o.medicaments || '—').slice(0, 80)
    doc.text((o.patient_nom || '—').slice(0, 28), 14, y)
    doc.text((o.medecin_nom || '—').slice(0, 24), 70, y)
    doc.text(new Date(o.date_ordonnance).toLocaleDateString('fr-FR'), 120, y)
    const medLines = doc.splitTextToSize(med, 45)
    doc.text(medLines, 150, y)
    y += Math.max(medLines.length * 5, 6) + 2
  })

  pdfFooter(doc)
  doc.save(`ordonnances-${new Date().toISOString().slice(0, 10)}.pdf`)
}

export function exportOrdonnancesListExcel(list) {
  exportToExcel(
    list.map(o => ({
      ID: o.id,
      Patient: o.patient_nom,
      Médecin: o.medecin_nom || '—',
      Date: new Date(o.date_ordonnance).toLocaleString('fr-FR'),
      Médicaments: (o.medicaments || '').slice(0, 120),
      'Code QR': o.patient_qr_code,
    })),
    `ordonnances-${new Date().toISOString().slice(0, 10)}.xlsx`,
    'Ordonnances',
  )
}
