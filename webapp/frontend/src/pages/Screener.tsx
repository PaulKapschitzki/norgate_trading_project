import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Paper,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
} from '@mui/material';

import apiClient, { ScreenerResultItem } from '../api/client';
import { ScreenerControl } from '../components/ScreenerControl';

// Screener Parameter Typen
interface Roc130Parameters {
  roc_threshold: number;
}

interface EmaTouchParameters {
  ema_period: number;
  touch_threshold: number;
}

// Vereinter Typ für alle möglichen Parameter
type ScreenerParameters = Roc130Parameters | EmaTouchParameters;

const screenerTypes = [
  {
    value: 'roc130',
    label: 'ROC130 Screener',
    defaultParams: { roc_threshold: 40 },
  },
  {
    value: 'ema_touch',
    label: 'EMA Touch Screener',
    defaultParams: { ema_period: 200, touch_threshold: 0.02 },
  },
];

const Screener: React.FC = () => {
  const [watchlists, setWatchlists] = useState<string[]>([]);
  const [selectedWatchlist, setSelectedWatchlist] = useState<string>('');
  const [selectedScreenerType, setSelectedScreenerType] = useState<string>('');
  const [parameters, setParameters] = useState<ScreenerParameters>({} as ScreenerParameters);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<ScreenerResultItem[] | null>(null);

  // Laden der verfügbaren Watchlists beim Komponenten-Mounting
  useEffect(() => {
    const fetchWatchlists = async () => {
      try {
        const watchlistsData = await apiClient.getWatchlists();
        setWatchlists(watchlistsData);
      } catch (err) {
        setError('Fehler beim Laden der Watchlists.');
        console.error(err);
      }
    };

    fetchWatchlists();
  }, []);

  // Setzen der Standard-Parameter beim Ändern des Screener-Typs
  useEffect(() => {
    if (selectedScreenerType) {
      const screenerType = screenerTypes.find((s) => s.value === selectedScreenerType);
      if (screenerType) {
        setParameters(screenerType.defaultParams);
      }
    }
  }, [selectedScreenerType]);

  // Handler für Parameter-Änderungen
  const handleParameterChange = (param: string, value: any) => {
    setParameters((prev) => ({
      ...prev,
      [param]: value,
    }));
  };

  // Zeigt die Parameter-Eingabefelder basierend auf dem Screener-Typ an
  const renderParameterInputs = () => {
    if (!selectedScreenerType) return null;

    switch (selectedScreenerType) {
      case 'roc130':
        return (
          <TextField
            margin="normal"
            fullWidth
            label="ROC Threshold"
            type="number"
            value={(parameters as Roc130Parameters).roc_threshold}
            onChange={(e) => handleParameterChange('roc_threshold', parseFloat(e.target.value))}
          />
        );
      case 'ema_touch':
        return (
          <>
            <TextField
              margin="normal"
              fullWidth
              label="EMA Period"
              type="number"
              value={(parameters as EmaTouchParameters).ema_period}
              onChange={(e) => handleParameterChange('ema_period', parseInt(e.target.value, 10))}
            />
            <TextField
              margin="normal"
              fullWidth
              label="Touch Threshold"
              type="number"
              inputProps={{ step: 0.01 }}
              value={(parameters as EmaTouchParameters).touch_threshold}
              onChange={(e) => handleParameterChange('touch_threshold', parseFloat(e.target.value))}
            />
          </>
        );
      default:
        return null;
    }
  };

  // Funktion zum Ausführen des Screeners
  const runScreener = async () => {
    if (!selectedWatchlist || !selectedScreenerType) {
      setError('Bitte wählen Sie eine Watchlist und einen Screener-Typ aus.');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await apiClient.runScreener(
        selectedWatchlist,
        selectedScreenerType,
        parameters,
        startDate || undefined,
        endDate || undefined
      );

      if (response.status === 'success' && response.results) {
        setResults(response.results);
      } else {
        setError(response.message || 'Ein unbekannter Fehler ist aufgetreten.');
      }
    } catch (err: any) {
      setError(`Fehler beim Ausführen des Screeners: ${err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Zeigt die Screener-Ergebnisse in einer Tabelle an
  const renderResults = () => {
    if (loading) {
      return (
        <>
          <ScreenerControl />
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        </>
      );
    }

    if (error) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      );
    }

    if (!results) {
      return null;
    }

    return (
      <>
        <ScreenerControl />
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table sx={{ minWidth: 650 }} aria-label="Screener Ergebnisse">
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                {Object.keys(results[0].data).map((key) => (
                  <TableCell key={key}>{key}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {results.map((row) => (
                <TableRow key={row.symbol}>
                  <TableCell component="th" scope="row">
                    {row.symbol}
                  </TableCell>
                  {Object.entries(row.data).map(([key, value]) => (
                    <TableCell key={key}>
                      {typeof value === 'number' ? value.toFixed(2) : String(value)}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </>
    );
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Aktien-Screener
        </Typography>

        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Screener-Einstellungen
          </Typography>          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="watchlist-label">Watchlist</InputLabel>
                <Select
                  labelId="watchlist-label"
                  value={selectedWatchlist}
                  label="Watchlist"
                  onChange={(e) => setSelectedWatchlist(e.target.value as string)}
                >
                  {watchlists.map((watchlist) => (
                    <MenuItem key={watchlist} value={watchlist}>
                      {watchlist}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="screener-type-label">Screener-Typ</InputLabel>
                <Select
                  labelId="screener-type-label"
                  value={selectedScreenerType}
                  label="Screener-Typ"
                  onChange={(e) => setSelectedScreenerType(e.target.value as string)}
                >
                  {screenerTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Start-Datum (YYYY-MM-DD)"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="End-Datum (YYYY-MM-DD)"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ mb: 2 }}>
                {renderParameterInputs()}
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={runScreener}
                disabled={loading}
                fullWidth
                sx={{ mt: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Screener ausführen'}
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            {results && (
              <Box>
                <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
                  Screener-Ergebnisse
                </Typography>
                {renderResults()}
              </Box>
            )}
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default Screener;