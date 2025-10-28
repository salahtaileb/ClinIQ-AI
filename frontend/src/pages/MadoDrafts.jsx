import React, { useState } from 'react'
import MadoPreviewModal from '../components/MadoPreviewModal'
import { generateMado, sendMado } from '../api/mado'

export default function MadoDrafts(){
  const [patientName, setPatientName] = useState('Jean Dupont')
  const [dob, setDob] = useState('1980-01-01')
  const [phn, setPhn] = useState('1234567890')
  const [address, setAddress] = useState('1 Rue Exemple')
  const [phone, setPhone] = useState('418-555-1212')
  const [disease, setDisease] = useState('Syphilis')
  const [regionId, setRegionId] = useState('06')
  const [drafts, setDrafts] = useState([])
  const [selectedDraft, setSelectedDraft] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  async function onGenerate(e){
    e.preventDefault()
    setLoading(true)
    const payload = {
      encounter_id: `enc-${Date.now()}`,
      patient: { name: patientName, dob, address, phone, phn, region_id: regionId },
      extracted: { disease_name: disease, clinician_name: 'Dr Demo', clinician_id: 'dr-demo' },
      region_id: regionId
    }
    try{
      const res = await generateMado(payload)
      setDrafts(prev => [res, ...prev])
    }catch(err){
      alert('Generation failed: ' + err.message)
    }finally{
      setLoading(false)
    }
  }

  function openPreview(draft){
    setSelectedDraft(draft)
    setModalOpen(true)
  }

  async function onSend(draft, transport='fax'){
    setLoading(true)
    try{
      const res = await sendMado({ draft_id: draft.draft_id, approve_by: 'dr-demo', transport })
      alert('Send result: ' + JSON.stringify(res))
      // update draft status locally
      setDrafts(prev => prev.map(d => d.draft_id === draft.draft_id ? { ...d, sent: res.sent, provider_job_id: res.provider_job_id } : d))
    }catch(err){
      alert('Send failed: ' + err.message)
    }finally{
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>MADO Drafts (Demo)</h2>
      <form onSubmit={onGenerate} style={{ marginBottom: 20 }}>
        <div>
          <label>Patient name: <input value={patientName} onChange={e=>setPatientName(e.target.value)} /></label>
        </div>
        <div>
          <label>DOB: <input value={dob} onChange={e=>setDob(e.target.value)} /></label>
        </div>
        <div>
          <label>PHN: <input value={phn} onChange={e=>setPhn(e.target.value)} /></label>
        </div>
        <div>
          <label>Address: <input value={address} onChange={e=>setAddress(e.target.value)} /></label>
        </div>
        <div>
          <label>Phone: <input value={phone} onChange={e=>setPhone(e.target.value)} /></label>
        </div>
        <div>
          <label>Disease: <input value={disease} onChange={e=>setDisease(e.target.value)} /></label>
        </div>
        <div>
          <label>Region ID: <input value={regionId} onChange={e=>setRegionId(e.target.value)} /></label>
        </div>
        <div style={{ marginTop: 10 }}>
          <button type="submit" disabled={loading}>Generate Draft</button>
        </div>
      </form>

      <h3>Generated drafts</h3>
      <ul>
        {drafts.map(d => (
          <li key={d.draft_id} style={{ marginBottom: 8 }}>
            <strong>{d.draft_id}</strong> — disease: {d.metadata?.disease || d.metadata?.disease}
            {d.sent ? ` (sent, job=${d.provider_job_id})` : ' (draft)'}
            {' — '}
            <button onClick={()=>openPreview(d)}>Preview</button>
            {' '}
            <button onClick={()=>onSend(d,'fax')} disabled={d.sent || loading}>Send Fax</button>
            {' '}
            <button onClick={()=>onSend(d,'manual')} disabled={loading}>Download/Print</button>
          </li>
        ))}
      </ul>

      {modalOpen && selectedDraft && (
        <MadoPreviewModal draft={selectedDraft} onClose={()=>setModalOpen(false)} onSend={onSend} />
      )}
    </div>
  )
}