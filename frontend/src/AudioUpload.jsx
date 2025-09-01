import React, { useState } from 'react';

function AudioUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select an audio file.');
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append('audio', file);
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setMessage('Upload successful! Audio ID: ' + data.id);
      } else {
        setMessage(data.error || 'Upload failed.');
      }
    } catch (err) {
      setMessage('Error uploading file.');
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 400, margin: '2rem auto', padding: 20, border: '1px solid #ccc', borderRadius: 8 }}>
      <h2>Upload Audio File</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="audio/*" onChange={handleFileChange} />
        <button type="submit" disabled={loading} style={{ marginLeft: 10 }}>
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
      {message && <p style={{ marginTop: 20 }}>{message}</p>}
    </div>
  );
}

export default AudioUpload;
