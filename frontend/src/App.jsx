
import { useState } from "react";
import "./App.css";

const API = "/api";

function App() {
  // const [url, setUrl] = useState("http://localhost:8000/test-form/");
  const [url, setUrl] = useState("http://localhost:8000/api/test-form/");
  const [instruction, setInstruction] = useState(
    "Fill my name as Somesh Jaiswal, email as somesh@example.com, select India, subscribe to the newsletter, and choose email as contact preference."
  );

  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);

  async function inspectWebsite(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setJob(null);
    setResults(null);

    try {
      const response = await fetch(`${API}/jobs/inspect/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, instruction }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Website inspection failed");
      }

      setJob(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function approveFill() {
    if (!job?.job_id) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API}/jobs/${job.job_id}/fill/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ approved: true }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Form filling failed");
      }

      setResults(data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setJob(null);
    setResults(null);
    setError("");
  }

  return (
    <main className="app">
      <header className="header">
        <div className="logo">WF</div>
        <div>
          <h1>WebForm Agent</h1>
          <p>AI-powered browser form automation</p>
        </div>
        <span className="status">Local Agent</span>
      </header>

      <section className="panel">
        <h2>Configure your task</h2>
        <p className="muted">
          Provide a website and tell the agent what information to enter.
        </p>

        <form onSubmit={inspectWebsite}>
          <label>Website URL</label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/form"
            required
          />

          <label>Natural-language instruction</label>
          <textarea
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="Tell the agent what to fill..."
            rows={5}
            required
          />

          <div className="actions">
            <button type="submit" disabled={loading}>
              {loading ? "Inspecting website..." : "Inspect Website"}
            </button>
            <button
              type="button"
              className="secondary"
              onClick={reset}
              disabled={loading}
            >
              Reset
            </button>
          </div>
        </form>
      </section>

      {error && <div className="error">{error}</div>}

      {job && (
        <section className="panel">
          <div className="section-heading">
            <div>
              <h2>Proposed field mappings</h2>
              <p className="muted">
                Review the agent's suggestions before approving.
              </p>
            </div>
            <span className="badge">{job.fields?.length || 0} fields</span>
          </div>

          {job.plan?.mappings?.length > 0 ? (
            <div className="mapping-list">
              {job.plan.mappings.map((mapping, index) => (
                <div className="mapping" key={`${mapping.field_key}-${index}`}>
                  <div>
                    <strong>{mapping.field_name}</strong>
                    <p className="muted">{mapping.field_key}</p>
                    <p className="reason">{mapping.reason}</p>
                  </div>
                  <div className="mapping-value">
                    {mapping.value === null
                      ? <em>Not provided</em>
                      : typeof mapping.value === "boolean"
                        ? mapping.value ? "Yes" : "No"
                        : String(mapping.value)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No proposed mappings were returned.</p>
          )}

          {!results && (
            <div className="approval">
              <p>
                <strong>Human approval required.</strong> The agent will fill
                the fields only after you approve.
              </p>
              <button onClick={approveFill} disabled={loading}>
                {loading ? "Filling form..." : "Approve & Fill Form"}
              </button>
            </div>
          )}
        </section>
      )}

      {results && (
        <section className="panel">
          <h2>Execution results</h2>
          {Object.entries(results).map(([field, result]) => (
            <div className="result-row" key={field}>
              <span>{field}</span>
              <span className={result.success ? "success" : "failure"}>
                {result.success
                  ? result.verified ? "Verified" : "Filled"
                  : result.error || "Failed"}
              </span>
            </div>
          ))}
          <p className="muted">
            The agent has filled and verified the form. It has not submitted it.
          </p>
        </section>
      )}

      <footer>
        WebForm Agent · React + Django + LangGraph + Playwright + Ollama
      </footer>
    </main>
  );
}

export default App;
