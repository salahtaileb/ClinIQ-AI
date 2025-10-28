export async function generateMado(payload){
  const res = await fetch('/mado/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if(!res.ok){
    const txt = await res.text()
    throw new Error(txt || 'generate failed')
  }
  return res.json()
}

export async function sendMado(payload){
  const res = await fetch('/mado/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if(!res.ok){
    const txt = await res.text()
    throw new Error(txt || 'send failed')
  }
  return res.json()
}