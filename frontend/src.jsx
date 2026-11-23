import React, { useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const editorRef = useRef(null);
  const [code, setCode] = useState('cout<a[j]<endl');
  const [lineNumber, setLineNumber] = useState(1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  function getLineNumber(editor) {
    const textBeforeCursor = editor.value.slice(0, editor.selectionStart);
    return textBeforeCursor.split('\n').length;
  }

  function handleChange(event) {
    const editor = event.target;
    setCode(editor.value);
    setLineNumber(getLineNumber(editor));
    setResult(null);
    setError('');
  }

  async function submit(event) {
    event.preventDefault();

    const editor = editorRef.current;
    const number = getLineNumber(editor);
    const original = editor.value.split('\n')[number - 1];
    const line = original.trim();

    setError('');
    setResult(null);

    if (!line) {
      setError('Click a line containing C++ code, then try again.');
      return;
    }

    if (line.length > 300) {
      setError('Choose a line with 300 characters or fewer.');
      return;
    }

    setBusy(true);

    try {
      const response = await fetch('/api/repair', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: line }),
      });

      const body = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof body.detail === 'string'
            ? body.detail
            : 'Could not repair this line.'
        );
      }

      const indentation = original.match(/^\s*/)[0];
      setResult({
        number,
        changed: body.suggestion !== line,
        suggestion: indentation + body.suggestion,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <article>
      <h1>C++ syntax repair</h1>
      <p>
        Paste your code, then click the line you want to repair.
        Try an array output statement or an if condition.
      </p>

      <form onSubmit={submit}>
        <label htmlFor="code">C++ code</label>

        <textarea
          ref={editorRef}
          id="code"
          rows={12}
          wrap="off"
          spellCheck={false}
          required
          disabled={busy}
          value={code}
          onChange={handleChange}
          onSelect={(event) => setLineNumber(getLineNumber(event.target))}
        />

        <button type="submit" disabled={busy}>
          {busy ? 'Generating…' : `Suggest a fix for line ${lineNumber}`}
        </button>
      </form>

      <section aria-live="polite">
        {error && <p role="alert">{error}</p>}

        {result && (
          <>
            <h2>
              {result.changed
                ? `Suggested fix for line ${result.number}`
                : `No change suggested for line ${result.number}`}
            </h2>
            <pre>{result.suggestion}</pre>
          </>
        )}
      </section>
    </article>
  );
}

createRoot(document.getElementById('root')).render(<App />);