import React, { useState } from 'react';

function App() {
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [vallEAudio, setVallEAudio] = useState(null);
  const [googleAudio, setGoogleAudio] = useState(null);
  const [error, setError] = useState(null);

  let mediaRecorder;
  let audioChunks = [];

  const startRecording = async () => {
    setRecording(true);
    audioChunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    mediaRecorder.ondataavailable = event => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(audioBlob);
      setAudioUrl(audioUrl);
      sendAudioData(audioBlob);
    };
  };

  const stopRecording = () => {
    setRecording(false);
    mediaRecorder.stop();
  };

  const sendAudioData = async (audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob);

    try {
      const response = await fetch('http://localhost:5000/process_audio', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        setVallEAudio(`http://localhost:5000/${data.vall_e_audio}`);
        setGoogleAudio(`http://localhost:5000/${data.google_audio}`);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1>Audio Recorder</h1>
      {recording ? (
        <button onClick={stopRecording}>Stop Recording</button>
      ) : (
        <button onClick={startRecording}>Start Recording</button>
      )}

      {audioUrl && (
        <div>
          <h2>Original Audio</h2>
          <audio src={audioUrl} controls></audio>
        </div>
      )}

      {vallEAudio && (
        <div>
          <h2>Vall-E TTS Audio</h2>
          <audio src={vallEAudio} controls></audio>
        </div>
      )}

      {googleAudio && (
        <div>
          <h2>Google TTS Audio</h2>
          <audio src={googleAudio} controls></audio>
        </div>
      )}

      {error && (
        <div>
          <h2>Error</h2>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
}

export default App;
