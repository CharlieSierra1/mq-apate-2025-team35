import { useState } from 'react'
import './App.css'

type Status = 'idle' | 'processing' | 'done' | 'error'

function App() {
  const [files, setFiles] = useState<FileList | null>(null)
  const [status, setStatus] = useState<Status>('idle')
  const [message, setMessage] = useState('')
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files)
    setDownloadUrl(null)
    setMessage('')
    setStatus('idle')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!files || files.length === 0) {
      setMessage('Please select at least one file.')
      setStatus('error')
      return
    }

    setStatus('processing')
    setMessage('Uploading and processing files…')

    const formData = new FormData()
    Array.from(files).forEach((file) => {
      formData.append('files', file)
    })

    try {
      // Backend endpoint that:
      // 1) Runs your clustering pipeline (SentenceTransformer + UMAP + HDBSCAN)
      // 2) Calls the Cloudflare Worker /analyze endpoint
      // 3) Returns the final CSV (e.g. emails_clustered.csv with CF annotations)
      const res = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        throw new Error(`Server returned ${res.status} ${res.statusText}`)
      }

      const blob = await res.blob()
      const url = URL.createObjectURL(blob)

      setDownloadUrl(url)
      setStatus('done')
      setMessage('Processing complete. Download your clustered output below.')
    } catch (err: any) {
      console.error(err)
      setStatus('error')
      setMessage(
        err?.message || 'Something went wrong while processing your files.'
      )
    }
  }

  return (
    <main className='app'>
      <h1>Email Clustering & Scam Archetypes</h1>
      <p className='description'>
        Upload one <strong>CSV / TXT / JSON</strong> files. The backend
        will:
        <br />
        <ol>
          <li>Cluster emails (SentenceTransformer → UMAP → HDBSCAN)</li>
          <li>Return a CSV with cluster + archetype information</li>
        </ol>
      </p>

      <form onSubmit={handleSubmit} className='card'>
        <label className='file-label'>
          <span>Select files (CSV, TXT, JSON)</span>
          <input
            type='file'
            multiple
            accept='.csv,.txt,.json'
            onChange={handleFileChange}
          />
        </label>

        <button
          type='submit'
          disabled={!files || status === 'processing'}
          aria-label='run clustering'
        >
          {status === 'processing' ? 'Processing…' : 'Run clustering'}
        </button>
      </form>

      {message && (
        <p className={`status status-${status}`}>
          {message}
        </p>
      )}

      {downloadUrl && (
        <a
          href={downloadUrl}
          download='emails_clustered_annotated.csv'
          className='download-link'
        >
          Download clustered CSV
        </a>
      )}
    </main>
  )
}

export default App
