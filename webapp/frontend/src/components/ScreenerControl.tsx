import React, { useEffect, useState, useCallback } from 'react';
import { Button, Box, Typography, LinearProgress, Alert } from '@mui/material';
import { Stop as StopIcon } from '@mui/icons-material';

interface ScreenerProgress {
  total_symbols: number;
  processed_symbols: number;
  current_symbol: string | null;
  error_message?: string | null;
}

interface ScreenerStatus {
  status: 'idle' | 'initializing' | 'downloading' | 'screening' | 'running' | 'stopping' | 'completed' | 'error';
  progress: ScreenerProgress;
  is_running: boolean;
}

export const ScreenerControl: React.FC = () => {
  const [status, setStatus] = useState<ScreenerStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/screener/status');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setStatus(data);
      setError(null);
    } catch (error) {
      console.error('Fehler beim Abrufen des Status:', error);
      setError('Fehler beim Abrufen des Status');
    }
  }, []);

  const stopScreener = async () => {
    try {
      const response = await fetch('/api/screener/stop', { method: 'POST' });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      await fetchStatus();
    } catch (error) {
      console.error('Fehler beim Stoppen des Screeners:', error);
      setError('Fehler beim Stoppen des Screeners');
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(() => {
      if (status?.status !== 'completed' && status?.status !== 'idle' && status?.status !== 'error') {
        fetchStatus();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [fetchStatus, status?.status]);

  const getProgressValue = () => {
    if (!status || !status.progress.total_symbols) return 0;
    return (status.progress.processed_symbols / status.progress.total_symbols) * 100;
  };

  const getStatusText = () => {
    if (!status) return '';
    switch (status.status) {
      case 'initializing':
        return 'Initialisiere Screener...';
      case 'downloading':
        return 'Lade Marktdaten herunter...';
      case 'screening':
        return 'Führe Screening durch...';
      case 'stopping':
        return 'Stoppe Prozess...';
      case 'completed':
        return 'Screening abgeschlossen';
      case 'error':
        return 'Fehler aufgetreten';
      default:
        return status.status;
    }
  };

  return (
    <Box>
      {(error || status?.progress.error_message) && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || status?.progress.error_message}
        </Alert>
      )}
      
      {status && status.status !== 'idle' && (
        <Box>
          <LinearProgress 
            variant="determinate" 
            value={getProgressValue()} 
            sx={{ mb: 1 }}
            color={status.status === 'error' ? 'error' : 'primary'}
          />
          <Typography variant="body2" gutterBottom>
            Status: {getStatusText()}
          </Typography>
          {status.progress.current_symbol && (
            <Typography variant="body2" gutterBottom>
              Aktuelles Symbol: {status.progress.current_symbol}
            </Typography>
          )}
          <Typography variant="body2" gutterBottom>
            Fortschritt: {status.progress.processed_symbols} von {status.progress.total_symbols} Symbolen
            ({Math.round(getProgressValue())}%)
          </Typography>
          {(status.status === 'running' || status.status === 'downloading' || status.status === 'screening') && (
            <Button
              variant="contained"
              color="secondary"
              onClick={stopScreener}
              startIcon={<StopIcon />}
              sx={{ mt: 1 }}
            >
              Stoppen
            </Button>
          )}
        </Box>
      )}
    </Box>
  );
};
