// pages/api/getUserRepos.js

import axios from 'axios';

export default async function handler(req, res) {
  const { username } = req.query;

  if (!username) {
    return res.status(400).json({ error: 'Username is required' });
  }

  const token = process.env.GITHUB_TOKEN;

  try {
    const response = await axios.get(
      `https://api.github.com/users/${JaynouOliver}/repos`,
      {
        headers: {
          Authorization: `token ${token}`,
        },
      }
    );

    res.status(200).json(response.data);
  } catch (error) {
    console.error(error.response.data);
    res
      .status(error.response.status)
      .json({ error: error.response.data.message });
  }
}
