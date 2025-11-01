import React, { useCallback } from 'react'
import './UploadZone.css'

const UploadZone = ({ onFileSelect, selectedFile }) => {
  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      const file = files[0]
      if (file.type.startsWith('image/') || file.type === 'application/pdf') {
        onFileSelect(file)
      } else {
        alert('Veuillez sélectionner une image (JPEG, PNG) ou un PDF')
      }
    }
  }, [onFileSelect])

  const handleFileInput = useCallback((e) => {
    const file = e.target.files?.[0]
    if (file) {
      onFileSelect(file)
    }
  }, [onFileSelect])

  return (
    <div
      className={`upload-zone ${selectedFile ? 'has-file' : ''}`}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {selectedFile ? (
        <div className="file-selected">
          <div className="file-icon">📄</div>
          <div className="file-info">
            <div className="file-name">{selectedFile.name}</div>
            <div className="file-size">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </div>
          </div>
          <button 
            className="remove-file"
            onClick={() => onFileSelect(null)}
            aria-label="Supprimer le fichier"
          >
            ✕
          </button>
        </div>
      ) : (
        <>
          <div className="upload-icon">📤</div>
          <h3>Glissez-déposez votre facture ici</h3>
          <p>ou</p>
          <label className="file-input-label">
            <input
              type="file"
              accept="image/jpeg,image/png,image/jpg,application/pdf"
              onChange={handleFileInput}
              className="file-input"
            />
            <span className="file-input-button">Parcourir les fichiers</span>
          </label>
          <p className="upload-hint">
            Formats supportés : JPEG, PNG, PDF (max 10 MB)
          </p>
        </>
      )}
    </div>
  )
}

export default UploadZone

