import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ScreenerControl } from '../../webapp/frontend/src/components/ScreenerControl';

// Mock fetch
global.fetch = jest.fn();

describe('ScreenerControl Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('zeigt Fortschrittsbalken wenn Screening läuft', async () => {
    const mockStatus = {
      status: 'running',
      progress: {
        total_symbols: 100,
        processed_symbols: 50,
        current_symbol: 'AAPL'
      },
      is_running: true
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockStatus
    });

    render(<ScreenerControl />);
    
    await waitFor(() => {
      expect(screen.getByText('50%')).toBeInTheDocument();
      expect(screen.getByText(/AAPL/)).toBeInTheDocument();
    });
  });

  test('Stopp-Button ist klickbar und sendet Request', async () => {
    const mockStatus = {
      status: 'running',
      progress: {
        total_symbols: 100,
        processed_symbols: 50,
        current_symbol: 'AAPL'
      },
      is_running: true
    };

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStatus
      })
      .mockResolvedValueOnce({
        ok: true
      });

    render(<ScreenerControl />);
    
    const stopButton = await screen.findByText('Stoppen');
    fireEvent.click(stopButton);

    expect(global.fetch).toHaveBeenCalledWith('/api/screener/stop', {
      method: 'POST'
    });
  });
});