import React, { useState } from 'react'
import axios from 'axios'
import './App.css'
import UploadZone from './components/UploadZone'
import PreviewImage from './components/PreviewImage'
import ResultsDisplay from './components/ResultsDisplay'
import LoadingSpinner from './components/LoadingSpinner'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://ocr-facture-api-production.up.railway.app'
const API_SECRET = import.meta.env.VITE_API_SECRET || ''

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [language, setLanguage] = useState('fra')
  const [checkCompliance, setCheckCompliance] = useState(false)
  const [apiKey, setApiKey] = useState(() => {
    // Récupérer depuis localStorage si disponible
    return localStorage.getItem('ocr_facture_api_key') || ''
  })

  const handleFileSelect = (file) => {
    if (file) {
      setSelectedFile(file)
      setResults(null)
      setError(null)
      
      // Créer l'URL de prévisualisation
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
    }
  }

  const handleProcess = async () => {
    if (!selectedFile) {
      setError('Veuillez sélectionner un fichier')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('language', language)
      formData.append('check_compliance', checkCompliance.toString())

      // Préparer les headers avec la clé API
      const secretToUse = apiKey || API_SECRET
      if (!secretToUse) {
        setError('Veuillez entrer votre clé API RapidAPI')
        setLoading(false)
        return
      }
      
      // Sauvegarder dans localStorage
      if (apiKey) {
        localStorage.setItem('ocr_facture_api_key', apiKey)
      }

      // Configurer les headers explicitement
      const headersConfig = {
        'X-RapidAPI-Proxy-Secret': secretToUse.trim()
      }

      console.log('=== DEBUG ===')
      console.log('URL:', `${API_BASE_URL}/v1/ocr/upload`)
      console.log('Header config:', headersConfig)
      console.log('Secret length:', secretToUse.length)
      console.log('Secret preview:', secretToUse.substring(0, 15) + '...')

      const response = await axios.post(
        `${API_BASE_URL}/v1/ocr/upload`,
        formData,
        {
          headers: headersConfig
        }
      )

      setResults(response.data)
    } catch (err) {
      console.error('=== ERREUR ===')
      console.error('Message:', err.message)
      console.error('Status:', err.response?.status)
      console.error('Response data:', err.response?.data)
      console.error('Request URL:', err.config?.url)
      console.error('Request headers:', err.config?.headers)
      console.error('Full error:', err)
      setError(
        err.response?.data?.detail || 
        err.response?.data?.error || 
        err.response?.data?.message ||
        err.message || 
        'Une erreur est survenue lors du traitement'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setResults(null)
    setError(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
  }

  const handleExportJSON = () => {
    if (!results) return
    
    const dataStr = JSON.stringify(results, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `ocr_result_${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const handleExportCSV = () => {
    if (!results?.extracted_data) return

    const data = results.extracted_data
    const csvRows = [
      ['Champ', 'Valeur', 'Confiance'],
      ['Numéro de facture', data.invoice_number || '', results.confidence_scores?.invoice_number || ''],
      ['Date', data.date || '', results.confidence_scores?.date || ''],
      ['Total HT', data.total_ht || '', results.confidence_scores?.total_ht || ''],
      ['TVA', data.tva || '', results.confidence_scores?.tva || ''],
      ['Total TTC', data.total_ttc || '', results.confidence_scores?.total_ttc || ''],
      ['Vendeur', data.vendor || '', results.confidence_scores?.vendor || ''],
      ['Client', data.client || '', results.confidence_scores?.client || ''],
    ]

    const csv = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `ocr_result_${Date.now()}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>📄 OCR Facture API - Démonstration</h1>
          <p>Testez l'extraction automatique de données de factures</p>
        </header>

        <div className="api-key-section">
          <label htmlFor="api-key">🔑 Clé API RapidAPI :</label>
          <input
            id="api-key"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Entrez votre clé X-RapidAPI-Proxy-Secret"
            className="api-key-input"
          />
          <a 
            href="https://rapidapi.com/provider/dashboard" 
            target="_blank" 
            rel="noopener noreferrer"
            className="api-key-help"
          >
            Où trouver ma clé ?
          </a>
        </div>

        {!results ? (
          <div className="upload-section">
            <UploadZone 
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
            />

            {previewUrl && (
              <PreviewImage 
                previewUrl={previewUrl}
                fileName={selectedFile?.name}
              />
            )}

            {selectedFile && (
              <div className="options-panel">
                <div className="option-group">
                  <label htmlFor="language">Langue :</label>
                  <select 
                    id="language"
                    value={language} 
                    onChange={(e) => setLanguage(e.target.value)}
                  >
                    <option value="fra">Français</option>
                    <option value="eng">Anglais</option>
                    <option value="deu">Allemand</option>
                    <option value="spa">Espagnol</option>
                    <option value="ita">Italien</option>
                    <option value="por">Portugais</option>
                  </select>
                </div>

                <div className="option-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={checkCompliance}
                      onChange={(e) => setCheckCompliance(e.target.checked)}
                    />
                    Validation conformité FR
                  </label>
                </div>

                <div className="actions">
                  <button 
                    onClick={handleProcess} 
                    disabled={loading || !apiKey}
                    className="btn btn-primary"
                    title={!apiKey ? 'Veuillez entrer votre clé API' : ''}
                  >
                    {loading ? <LoadingSpinner /> : '🚀 Traiter la facture'}
                  </button>
                  <button 
                    onClick={handleReset}
                    className="btn btn-secondary"
                  >
                    ✨ Nouveau fichier
                  </button>
                </div>
                
                {!apiKey && (
                  <div className="warning-message">
                    ⚠️ Veuillez entrer votre clé API RapidAPI pour tester l'API
                  </div>
                )}
              </div>
            )}

            {error && (
              <div className="error-message">
                <strong>❌ Erreur :</strong> {error}
              </div>
            )}
          </div>
        ) : (
          <ResultsDisplay 
            results={results}
            previewUrl={previewUrl}
            onReset={handleReset}
            onExportJSON={handleExportJSON}
            onExportCSV={handleExportCSV}
          />
        )}
      </div>

      <footer className="footer">
        <p>
          API OCR Facture France - 
          <a href="https://github.com/RailsNft/OCR-Facture-API" target="_blank" rel="noopener noreferrer">
            Documentation GitHub
          </a>
        </p>
      </footer>
    </div>
  )
}

export default App

