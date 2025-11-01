import React from 'react'
import './ConfidenceBar.css'

const ConfidenceBar = ({ field, score, compact = false }) => {
  if (score === undefined || score === null) return null

  const percentage = Math.round(score * 100)
  const getColor = () => {
    if (score >= 0.9) return '#10b981'
    if (score >= 0.7) return '#f59e0b'
    return '#ef4444'
  }

  const getLabel = () => {
    if (score >= 0.9) return 'Très fiable'
    if (score >= 0.7) return 'Fiable'
    return 'À vérifier'
  }

  if (compact) {
    return (
      <div className="confidence-bar-compact">
        <div className="confidence-bar-fill" style={{ width: `${percentage}%`, backgroundColor: getColor() }} />
        <span className="confidence-text">{percentage}%</span>
      </div>
    )
  }

  return (
    <div className="confidence-item">
      <div className="confidence-header">
        <span className="confidence-field">{field || 'Confiance'}</span>
        <span className="confidence-percentage">{percentage}%</span>
      </div>
      <div className="confidence-bar-wrapper">
        <div 
          className="confidence-bar" 
          style={{ width: `${percentage}%`, backgroundColor: getColor() }}
        />
      </div>
      <span className="confidence-label">{getLabel()}</span>
    </div>
  )
}

export default ConfidenceBar

