import React from 'react'
import './LoadingSpinner.css'

const LoadingSpinner = () => {
  return (
    <div className="loading-spinner">
      <div className="spinner"></div>
      <span>Traitement en cours...</span>
    </div>
  )
}

export default LoadingSpinner



