import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('es');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [taskId, setTaskId] = useState(null);

  const handleFileUpload = (event) => {
    setFile(event.target.files[0]);
    setYoutubeUrl('');
  };

  useEffect(() => {
    let intervalId;
    if (taskId && isProcessing) {
      intervalId = setInterval(async () => {
        try {
          const response = await fetch(`http://localhost:5000/api/status/${taskId}`);
          const data = await response.json();
          
          if (data.state === 'SUCCESS') {
            setIsProcessing(false);
            setProgress(100);
            setDownloadUrl(`http://localhost:5000/api/download/${data.result.video_id}`);
            clearInterval(intervalId);
          } else if (data.state === 'FAILURE') {
            setIsProcessing(false);
            alert('Translation failed: ' + data.error);
            clearInterval(intervalId);
          } else if (data.state === 'PROGRESS') {
            setProgress(data.info.progress || 0);
          }
        } catch (error) {
          console.error('Error checking status:', error);
        }
      }, 2000);
    }
    return () => clearInterval(intervalId);
  }, [taskId, isProcessing]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setProgress(0);
    setDownloadUrl(null);
    setTaskId(null);

    const formData = new FormData();
    if (file) {
      formData.append('video', file);
    } else if (youtubeUrl) {
      formData.append('youtube_url', youtubeUrl);
    }
    formData.append('target_language', targetLanguage);

    try {
      const response = await fetch('http://localhost:5000/api/translate', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Translation failed');
      }

      const result = await response.json();
      setTaskId(result.task_id);
    } catch (error) {
      console.error('Error:', error);
      setIsProcessing(false);
      alert('Translation failed. Please try again.');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Video Language Translator</h1>
        <form onSubmit={handleSubmit} className="translation-form">
          <div className="input-group">
            <label>Upload Video File:</label>
            <input
              type="file"
              accept="video/*"
              onChange={handleFileUpload}
              disabled={isProcessing || youtubeUrl !== ''}
            />
          </div>

          <div className="input-group">
            <label>Or Enter YouTube URL:</label>
            <input
              type="text"
              value={youtubeUrl}
              onChange={(e) => {
                setYoutubeUrl(e.target.value);
                setFile(null);
              }}
              disabled={isProcessing || file !== null}
              placeholder="https://www.youtube.com/watch?v=..."
            />
          </div>

          <div className="input-group">
            <label>Target Language:</label>
            <select
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
              disabled={isProcessing}
            >
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="it">Italian</option>
              <option value="ja">Japanese</option>
              <option value="ko">Korean</option>
              <option value="zh">Chinese</option>
              <option value="hi">Hindi</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={isProcessing || (!file && !youtubeUrl)}
          >
            {isProcessing ? 'Processing...' : 'Translate Video'}
          </button>
        </form>

        {isProcessing && (
          <div className="progress-bar">
            <div
              className="progress-bar-fill"
              style={{ width: `${progress}%` }}
            ></div>
            <span>{progress}%</span>
          </div>
        )}

        {downloadUrl && (
          <div className="download-section">
            <p>Translation complete!</p>
            <a
              href={downloadUrl}
              className="download-button"
              download
            >
              Download Translated Video
            </a>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
