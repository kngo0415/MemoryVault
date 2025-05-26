import React, { useState, useEffect } from 'react';
import './App.css';

// Define the backend API URL
const API_URL = 'http://localhost:8000'; // Assuming backend runs on port 8000

function App() {
  const [currentNote, setCurrentNote] = useState('');
  const [notes, setNotes] = useState([]);
  const [error, setError] = useState(null); // For basic error display

  // Fetch notes from the backend when the component mounts
  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const response = await fetch(`${API_URL}/get_notes/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setNotes(data);
      setError(null); // Clear any previous errors
    } catch (e) {
      console.error("Failed to fetch notes:", e);
      setError("Failed to load notes. Make sure the backend is running.");
      // Keep existing notes if fetch fails, or clear them:
      // setNotes([]); 
    }
  };

  const handleSaveNote = async () => {
    if (!currentNote.trim()) {
      alert("Note cannot be empty!");
      return;
    }
    try {
      const response = await fetch(`${API_URL}/add_note/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: currentNote }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      // const newNode = await response.json(); // The backend returns the new note
      setCurrentNote(''); // Clear the input field
      fetchNotes(); // Refresh the notes list from the backend
      setError(null);
    } catch (e) {
      console.error("Failed to save note:", e);
      setError("Failed to save note. Please try again.");
    }
  };

  // Helper to format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'No date';
    try {
      // Attempt to create a Date object. Handle potential invalid date strings.
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) { // Check if date is valid
        return 'Invalid date';
      }
      return date.toLocaleString(); // Converts to local date and time string
    } catch (e) {
      console.error("Error formatting timestamp:", e);
      return 'Error in date';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>MemoryVault</h1>
      </header>
      <main className="App-main">
        <div className="note-input-section">
          <textarea
            value={currentNote}
            onChange={(e) => setCurrentNote(e.target.value)}
            placeholder="Enter your note here..."
            rows="4"
            cols="50"
          />
          <button onClick={handleSaveNote}>Save Note</button>
        </div>

        {error && <p className="error-message">{error}</p>}

        <div className="notes-display-section">
          <h2>Saved Notes</h2>
          {notes.length === 0 && !error && <p>No notes yet. Add one above!</p>}
          {notes.length === 0 && error && <p>Could not load notes.</p>}
          <ul>
            {notes.map((note) => (
              <li key={note.id} className="note-item">
                <p className="note-content">{note.content}</p>
                <p className="note-timestamp">
                  Saved: {formatTimestamp(note.timestamp)}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </main>
      <footer className="App-footer">
        <p>MemoryVault Frontend</p>
      </footer>
    </div>
  );
}

export default App;
