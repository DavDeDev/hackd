// pages/api/getUserRepos.js

import { fetchUserRepositories } from '../../utils/github';

export default async function handler(req, res) {
  const { username } = req.query;

  if (!username) {
    return res.status(400).json({ error: 'Username is required' });
  }

  try {
    const repos = await fetchUserRepositories(username);
    res.status(200).json(repos);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch repositories' });
  }
}
