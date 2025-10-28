import React from 'react'

export default function MadoPreviewModal({ draft, onClose, onSend }){
  const previewUrl = draft?.preview_url || (draft?.metadata && draft.metadata.s3_key ? draft.metadata_preview_url : null)

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ width: '90%', height: '90%', background: '#fff', borderRadius: 6, padding: 12, display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>MADO Preview — {draft?.draft_id}</h3>
          <div>
            <button onClick={onClose} style={{ marginRight: 8 }}>Close</button>
          </div>
        </div>
        <div style={{ flex: 1, marginTop: 8 }}>
          {previewUrl ? (
            <iframe src={previewUrl} title="MADO preview" style={{ width: '100%', height: '100%', border: '1px solid #ccc' }} />
          ) : (
            <div style={{ padding: 20 }}>Preview not available. Generate mapping and ensure the form PDF is present at backend/mado/mado_form.pdf.</div>
          )}
        </div>
        <div style={{ marginTop: 12, display: 'flex', justifyContent: 'flex-end' }}>
          <button onClick={() => onSend(draft, 'manual')} style={{ marginRight: 8 }}>Download / Print</button>
          <button onClick={() => onSend(draft, 'fax')} style={{ background: '#0b6', border: 'none', padding: '8px 12px', borderRadius: 4 }}>Send Fax</button>
        </div>
      </div>
    </div>
  )
}