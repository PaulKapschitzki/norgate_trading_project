/// <reference types="jest" />
/// <reference types="@testing-library/jest-dom" />
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
// import { act } from 'react-dom/test-utils';
import { act } from 'react';
import { ScreenerControl } from '../components/ScreenerControl';
import '@testing-library/jest-dom';
import { describe, expect, test, jest, beforeEach } from '@jest/globals';

interface ScreenerProgress {
  total_symbols: number;
  processed_symbols: number;
  current_symbol: string;
}

interface ScreenerStatus {
  status: 'idle' | 'running' | 'stopping' | 'completed';
  progress: {
    total_symbols: number;
    processed_symbols: number;
    current_symbol: string | null;
  };
  is_running: boolean;
}

const mockFetchResponse = (data: Partial<ScreenerStatus>): Promise<Response> => {
  const defaultResponse: ScreenerStatus = {
    status: 'idle',
    progress: {
      total_symbols: 0,
      processed_symbols: 0,
      current_symbol: null
    },
    is_running: false
  };
  
  return Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ ...defaultResponse, ...data })
  } as Response);
};

describe('ScreenerControl Component', () => {  beforeEach(() => {
    jest.clearAllMocks();
    // Mock fetch vor jedem Test mit Standardantwort
    global.fetch = jest.fn().mockImplementation(() => 
      mockFetchResponse({
        status: 'idle',
        progress: {
          total_symbols: 0,
          processed_symbols: 0,
          current_symbol: null
        },
        is_running: false
      })
    ) as jest.MockedFunction<typeof fetch>;
  });  test('zeigt Fortschrittsbalken wenn Screening läuft', async () => {
    const mockStatus: ScreenerStatus = {
      status: 'running',
      progress: {
        total_symbols: 100,
        processed_symbols: 50,
        current_symbol: 'AAPL'
      },
      is_running: true
    };

    // Mock den initialen Status-Abruf
    (global.fetch as jest.Mock).mockImplementation(() => 
      mockFetchResponse(mockStatus)
    );

    render(<ScreenerControl />);
    
    // Warten auf die asynchrone Statusaktualisierung
    await waitFor(() => {
      expect(screen.getByText(/50%/)).toBeInTheDocument();
    });
    
    // Prüfen auf weitere UI-Elemente
    expect(screen.getByText(/AAPL/)).toBeInTheDocument();
    expect(screen.getByText(/running/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /stoppen/i })).toBeInTheDocument();
  });  test('Stopp-Button ist klickbar und sendet Request', async () => {
    const runningStatus: ScreenerStatus = {
      status: 'running',
      progress: {
        total_symbols: 100,
        processed_symbols: 50,
        current_symbol: 'AAPL'
      },
      is_running: true
    };

    const stoppingStatus: ScreenerStatus = {
      status: 'stopping',
      progress: {
        total_symbols: 100,
        processed_symbols: 50,
        current_symbol: 'AAPL'
      },
      is_running: false
    };

    // Setze den initialen Status auf 'running'
    (global.fetch as jest.Mock).mockImplementationOnce(() => 
      mockFetchResponse(runningStatus)
    );

    render(<ScreenerControl />);
    
    // Warten auf den Stop-Button
    const stopButton = await waitFor(() => 
      screen.getByRole('button', { name: /stoppen/i })
    );
    expect(stopButton).toBeInTheDocument();

    // Mock für den Stop-Request
    (global.fetch as jest.Mock).mockImplementationOnce(() => 
      Promise.resolve({ ok: true })
    );

    // Mock für den Status-Request nach dem Stoppen
    (global.fetch as jest.Mock).mockImplementationOnce(() => 
      mockFetchResponse(stoppingStatus)
    );

    // Button klicken
    fireEvent.click(stopButton);

    // Überprüfen, ob der Stop-Request gesendet wurde
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/screener/stop', { method: 'POST' });
    });
  });
});
