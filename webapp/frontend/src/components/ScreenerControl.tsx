import React, { useEffect, useState } from 'react';
import { Button, Box, Typography, LinearProgress } from '@mui/material';
import { Stop as StopIcon } from '@mui/icons-material';

interface ScreenerStatus {
  status: 'idle' | 'running' | 'stopping' | 'completed';
  progress: {
    total_symbols: number;
    processed_symbols: number;
    current_symbol: string | null;
  };
  is_running: boolean;
}

export const ScreenerControl: React.FC = () => {
  const [status, setStatus] = useState<ScreenerStatus | null>(null);

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/screener/status');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Fehler beim Abrufen des Status:', error);
    }
  };

  const stopScreener = async () => {
    try {
      await fetch('/api/screener/stop', { method: 'POST' });
      // Status sofort aktualisieren
      fetchStatus();
    } catch (error) {
      console.error('Fehler beim Stoppen des Screeners:', error);
    }
  };

  useEffect(() => {
    // Status initial abrufen
    fetchStatus();

    // Status alle 2 Sekunden aktualisieren, wenn der Screener läuft
    const interval = setInterval(() => {
      if (status?.is_running) {
        fetchStatus();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [status?.is_running]);

  if (!status) {
    return null;
  }

  const progress = status.progress.total_symbols > 0
    ? (status.progress.processed_symbols / status.progress.total_symbols) * 100
    : 0;

  return (
    <Box sx={{ width: '100%', mt: 2, mb: 2 }}>
      {status.status !== 'idle' && (
        <>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
              Status: {status.status}
              {status.progress.current_symbol && ` - ${status.progress.current_symbol}`}
            </Typography>
            {status.is_running && (
              <Button
                variant="contained"
                color="error"
                startIcon={<StopIcon />}
                onClick={stopScreener}
                sx={{ ml: 2 }}
              >
                Stoppen
              </Button>
            )}
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box sx={{ width: '100%', mr: 1 }}>
              <LinearProgress 
                variant="determinate" 
                value={progress} 
                color={status.status === 'stopping' ? 'warning' : 'primary'}
              />
            </Box>
            <Box sx={{ minWidth: 35 }}>
              <Typography variant="body2" color="text.secondary">
                {Math.round(progress)}%
              </Typography>
            </Box>
          </Box>
          <Typography variant="caption" color="text.secondary">
            {status.progress.processed_symbols} von {status.progress.total_symbols} Symbolen verarbeitet
          </Typography>
        </>
      )}
    </Box>
  );
};
