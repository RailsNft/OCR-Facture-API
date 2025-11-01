import React from 'react'
import './PreviewImage.css'

const PreviewImage = ({ previewUrl, fileName }) => {
  return (
    <div className="preview-container">
      <h3>📷 Aperçu</h3>
      <div className="preview-wrapper">
        {fileName?.toLowerCase().endsWith('.pdf') ? (
          <div className="pdf-preview">
            <div className="pdf-icon">📄</div>
            <p>{fileName}</p>
            <p className="pdf-note">Le PDF sera traité par l'API</p>
          </div>
        ) : (
          <img 
            src={previewUrl} 
            alt="Aperçu de la facture"
            className="preview-image"
          />
        )}
      </div>
    </div>
  )
}

export default PreviewImage

