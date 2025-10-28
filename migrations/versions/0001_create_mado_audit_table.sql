-- Create mado_audit table
CREATE TABLE IF NOT EXISTS mado_audit (
  id UUID PRIMARY KEY,
  encounter_id TEXT,
  patient_hash TEXT,
  disease TEXT,
  region_id TEXT,
  recipient_fax TEXT,
  transport TEXT,
  provider_job_id TEXT,
  status TEXT,
  s3_key TEXT,
  created_by TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  sent_at TIMESTAMP WITH TIME ZONE,
  notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_mado_audit_encounter ON mado_audit (encounter_id);