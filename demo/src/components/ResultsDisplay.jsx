import React from 'react'
import './ResultsDisplay.css'
import ConfidenceBar from './ConfidenceBar'

const ResultsDisplay = ({ results, previewUrl, onReset, onExportJSON, onExportCSV }) => {
  const extractedData = results?.extracted_data || {}
  const confidenceScores = results?.confidence_scores || {}
  const compliance = results?.compliance

  const getConfidenceColor = (score) => {
    if (!score) return '#999'
    if (score >= 0.9) return '#10b981' // vert
    if (score >= 0.7) return '#f59e0b' // orange
    return '#ef4444' // rouge
  }

  const getConfidenceLabel = (score) => {
    if (!score) return 'N/A'
    if (score >= 0.9) return 'Très fiable'
    if (score >= 0.7) return 'Fiable'
    return 'À vérifier'
  }

  return (
    <div className="results-display">
      <div className="results-header">
        <h2>✅ Résultats de l'extraction OCR</h2>
        <div className="results-actions">
          <button onClick={onExportJSON} className="btn-export">
            📥 Export JSON
          </button>
          <button onClick={onExportCSV} className="btn-export">
            📊 Export CSV
          </button>
          <button onClick={onReset} className="btn-new">
            ✨ Nouvelle facture
          </button>
        </div>
      </div>

      <div className="results-grid">
        {/* Colonne gauche : Données extraites */}
        <div className="results-section">
          <h3>📋 Données extraites</h3>
          
          <div className="data-grid">
            <DataField
              label="Numéro de facture"
              value={extractedData.invoice_number}
              confidence={confidenceScores.invoice_number}
            />
            
            <DataField
              label="Date"
              value={extractedData.date}
              confidence={confidenceScores.date}
            />
            
            <DataField
              label="Vendeur"
              value={extractedData.vendor}
              confidence={confidenceScores.vendor}
            />
            
            <DataField
              label="Client"
              value={extractedData.client}
              confidence={confidenceScores.client}
            />
            
            <DataField
              label="Total HT"
              value={extractedData.total_ht ? `${extractedData.total_ht} €` : null}
              confidence={confidenceScores.total_ht}
            />
            
            <DataField
              label="TVA"
              value={extractedData.tva ? `${extractedData.tva} €` : null}
              confidence={confidenceScores.tva}
            />
            
            <DataField
              label="Total TTC"
              value={extractedData.total_ttc ? `${extractedData.total_ttc} €` : null}
              confidence={confidenceScores.total_ttc}
            />
          </div>

          {/* Lignes de facture */}
          {extractedData.items && extractedData.items.length > 0 && (
            <div className="items-section">
              <h4>📦 Lignes de facture</h4>
              <div className="items-table">
                <div className="items-header">
                  <div>Description</div>
                  <div>Qté</div>
                  <div>Prix unit.</div>
                  <div>Total</div>
                </div>
                {extractedData.items.map((item, index) => (
                  <div key={index} className="item-row">
                    <div>{item.description || '-'}</div>
                    <div>{item.quantity || '-'}</div>
                    <div>{item.unit_price ? `${item.unit_price} €` : '-'}</div>
                    <div>{item.total ? `${item.total} €` : '-'}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Colonne droite : Aperçu + Compliance */}
        <div className="results-sidebar">
          {previewUrl && (
            <div className="preview-section">
              <h3>📷 Aperçu</h3>
              <img 
                src={previewUrl} 
                alt="Facture"
                className="result-preview-image"
              />
            </div>
          )}

          {compliance && (
            <div className="compliance-section">
              <h3>✅ Conformité</h3>
              <div className="compliance-status">
                {compliance.compliance_check?.compliant ? (
                  <div className="status-badge success">
                    ✅ Facture conforme
                  </div>
                ) : (
                  <div className="status-badge warning">
                    ⚠️ Facture non conforme
                  </div>
                )}
                {compliance.compliance_check?.score && (
                  <div className="compliance-score">
                    Score : {compliance.compliance_check.score}%
                  </div>
                )}
                {compliance.compliance_check?.missing_fields?.length > 0 && (
                  <div className="missing-fields">
                    <strong>Champs manquants :</strong>
                    <ul>
                      {compliance.compliance_check.missing_fields.map((field, i) => (
                        <li key={i}>{field}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Scores de confiance globaux */}
      <div className="confidence-section">
        <h3>📊 Scores de confiance</h3>
        <div className="confidence-list">
          {Object.entries(confidenceScores).map(([field, score]) => (
            <ConfidenceBar
              key={field}
              field={field}
              score={score}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

const DataField = ({ label, value, confidence }) => {
  if (!value) return null

  return (
    <div className="data-field">
      <div className="data-label">{label}</div>
      <div className="data-value">{value}</div>
      {confidence !== undefined && (
        <ConfidenceBar
          field=""
          score={confidence}
          compact
        />
      )}
    </div>
  )
}

export default ResultsDisplay



