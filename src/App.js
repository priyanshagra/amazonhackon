import React, { useState } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Box, Paper, Grid } from '@mui/material';

const QuestionForm = () => {
  const [question, setQuestion] = useState('');
  const [responses, setResponses] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/process_question', { question });
      setResponses(response.data);
    } catch (error) {
      console.error('Error fetching response:', error);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 5 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Amazon Customer Service
        </Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            label="Enter your question"
            variant="outlined"
            fullWidth
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            margin="normal"
          />
          <Box textAlign="center" sx={{ mt: 2 }}>
            <Button variant="contained" color="primary" type="submit">
              Ask
            </Button>
          </Box>
        </form>
        {responses.response_sampling && (
          <Box mt={4}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="h6">Response (Sampling):</Typography>
              <Typography>{responses.response_sampling}</Typography>
            </Paper>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default QuestionForm;
