import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Slider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';

interface ScreenerResult {
  symbol: string;
  data: {
    roc_yesterday: number;
    roc_day_before: number;
  };
}

const Screener: React.FC = () => {
  const [selectedWatchlist, setSelectedWatchlist] = React.useState('');
  const [rocThreshold, setRocThreshold] = React.useState<number>(40);

  // Watchlists abrufen
  const { data: watchlists } = useQuery({
    queryKey: ['watchlists'],
    queryFn: async () => {
      const response = await axios.get('/api/watchlists');
      return response.data;
    },
  });

  // Screener ausführen
  const screenMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post('/api/screener/run', {
        watchlist_name: selectedWatchlist,
        screener_type: 'ROC130',
        parameters: {
          roc_threshold: rocThreshold,
        },
      });
      return response.data;
    },
  });

  const handleScreenerStart = () => {
    if (selectedWatchlist) {
      screenMutation.mutate();
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Screener
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Einstellungen
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Watchlist</InputLabel>
                <Select
                  value={selectedWatchlist}
                  onChange={(e) => setSelectedWatchlist(e.target.value)}
                  label="Watchlist"
                >
                  {watchlists?.map((list: string) => (
                    <MenuItem key={list} value={list}>
                      {list}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Typography gutterBottom>
                ROC130 Schwellenwert: {rocThreshold}%
              </Typography>
              <Slider
                value={rocThreshold}
                onChange={(_, value) => setRocThreshold(value as number)}
                min={0}
                max={100}
                valueLabelDisplay="auto"
              />

              <Button
                variant="contained"
                fullWidth
                onClick={handleScreenerStart}
                disabled={!selectedWatchlist || screenMutation.isPending}
                sx={{ mt: 2 }}
              >
                Screener Starten
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Ergebnisse
              </Typography>

              {screenMutation.data?.results && (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell align="right">ROC (Gestern)</TableCell>
                        <TableCell align="right">ROC (Vorgestern)</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {screenMutation.data.results.map((result: ScreenerResult) => (
                        <TableRow key={result.symbol}>
                          <TableCell component="th" scope="row">
                            {result.symbol}
                          </TableCell>
                          <TableCell align="right">
                            {result.data.roc_yesterday.toFixed(2)}%
                          </TableCell>
                          <TableCell align="right">
                            {result.data.roc_day_before.toFixed(2)}%
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}

              {screenMutation.isPending && (
                <Typography>Screener wird ausgeführt...</Typography>
              )}

              {screenMutation.isError && (
                <Typography color="error">
                  Fehler beim Ausführen des Screeners
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Screener;