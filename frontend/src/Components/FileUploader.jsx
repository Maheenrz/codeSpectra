import React, { useCallback, useState } from 'react';

const FileUploader = ({ 
  onFileSelect, 
  accept = '.c,.cpp,.py,.java,.js,.ts',
  label = 'Upload File',
  helpText = 'Drag and drop or click to browse',
  currentFile = null 
}) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  }, [onFileSelect]);

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const removeFile = (e) => {
    e.stopPropagation();
    onFileSelect(null);
  };

  return (
    <div 
      className={`file-uploader ${isDragging ? 'dragging' : ''} ${currentFile ? 'has-file' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept={accept}
        onChange={handleFileInput}
        id={`file-input-${label}`}
        className="file-input"
      />
      
      <label htmlFor={`file-input-${label}`} className="file-label">
        {currentFile ? (
          <div className="file-selected">
            <span className="file-icon">📄</span>
            <span className="file-name">{currentFile.name}</span>
            <button 
              type="button" 
              className="remove-file-btn"
              onClick={removeFile}
            >
              ✕
            </button>
          </div>
        ) : (
          <div className="file-placeholder">
            <span className="upload-icon">📁</span>
            <span className="upload-text">{label}</span>
            <span className="upload-help">{helpText}</span>
          </div>
        )}
      </label>
    </div>
  );
};

export default FileUploader;