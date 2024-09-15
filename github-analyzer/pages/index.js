// pages/index.js

import { useState } from 'react';

export default function Home() {
  const [username, setUsername] = useState('');
  const [analysisResults, setAnalysisResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setAnalysisResults([]);

    try {
      // Fetch repositories
      const reposResponse = await fetch(`/api/getUserRepos?username=${username}`);
      const repos = await reposResponse.json();

      // Iterate through repositories and fetch code
      for (const repo of repos) {
        const codeResponse = await fetch(`/api/getRepoCode?owner=${username}&repo=${repo.name}`);
        const { codeContents } = await codeResponse.json();

        // Analyze each code snippet
        for (const code of codeContents) {
          const analysisResponse = await fetch('/api/analyzeCode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
          });
          const { analysis } = await analysisResponse.json();

          setAnalysisResults((prev) => [...prev, { repo: repo.name, code, analysis }]);
        }
      }
    } catch (err) {
      console.error(err);
      setError('An error occurred during analysis.');
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Cohere GitHub Code Analyzer</h1>
      <input
        type="text"
        placeholder="Enter GitHub username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        style={{ padding: '8px', marginRight: '8px', width: '300px' }}
      />
      <button onClick={handleAnalyze} style={{ padding: '8px' }}>
        Analyze
      </button>

      {loading && <p>Analyzing...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {analysisResults.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h2>Analysis Results for {username}</h2>
          {analysisResults.map((result, index) => (
            <div key={index} style={{ marginBottom: '20px' }}>
              <h3>Repository: {result.repo}</h3>
              <pre>{result.code.substring(0, 200)}...</pre>
              <p><strong>Analysis:</strong> {result.analysis}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
