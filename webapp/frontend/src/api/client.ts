import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API-Typen
export interface ScreenerParameters {
  [key: string]: any;
}

export interface BacktestParameters {
  [key: string]: any;
}

export interface ScreenerResultItem {
  symbol: string;
  data: any;
}

export interface ScreenerResponse {
  status: string;
  run_id?: number;
  results?: ScreenerResultItem[];
  message?: string;
}

export interface BacktestTradeItem {
  entry_date: string;
  entry_price: number;
  exit_date: string;
  exit_price: number;
  profit_loss: number;
  profit_loss_percent: number;
}

export interface BacktestResultItem {
  symbol: string;
  total_trades: number;
  win_rate: number;
  avg_return: number;
  max_drawdown: number;
  sharpe_ratio?: number;
  trades: BacktestTradeItem[];
}

export interface BacktestResponse {
  status: string;
  run_id?: number;
  results?: BacktestResultItem[];
  message?: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: 'http://localhost:8000/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Watchlists API
  public async getWatchlists(): Promise<string[]> {
    try {
      const response: AxiosResponse<string[]> = await this.client.get('/watchlists');
      return response.data;
    } catch (error) {
      console.error('Fehler beim Abrufen der Watchlists:', error);
      throw error;
    }
  }

  // Screener API
  public async runScreener(
    watchlistName: string,
    screenerType: string,
    parameters: ScreenerParameters,
    startDate?: string,
    endDate?: string
  ): Promise<ScreenerResponse> {
    try {
      const response: AxiosResponse<ScreenerResponse> = await this.client.post('/screener/run', {
        watchlist_name: watchlistName,
        screener_type: screenerType,
        parameters,
        start_date: startDate,
        end_date: endDate,
      });
      return response.data;
    } catch (error) {
      console.error('Fehler beim Ausführen des Screeners:', error);
      throw error;
    }
  }

  public async getScreenerResults(screenerId: number): Promise<ScreenerResponse> {
    try {
      const response: AxiosResponse<ScreenerResponse> = await this.client.get(`/screener/${screenerId}`);
      return response.data;
    } catch (error) {
      console.error(`Fehler beim Abrufen der Screener-Ergebnisse für ID ${screenerId}:`, error);
      throw error;
    }
  }

  // Backtest API
  public async runBacktest(
    strategyType: string,
    parameters: BacktestParameters,
    symbols?: string[],
    watchlistName?: string,
    startDate?: string,
    endDate?: string
  ): Promise<BacktestResponse> {
    try {
      const response: AxiosResponse<BacktestResponse> = await this.client.post('/backtest/run', {
        strategy_type: strategyType,
        parameters,
        symbols,
        watchlist_name: watchlistName,
        start_date: startDate,
        end_date: endDate,
      });
      return response.data;
    } catch (error) {
      console.error('Fehler beim Ausführen des Backtests:', error);
      throw error;
    }
  }

  public async getBacktestResults(backtestId: number): Promise<BacktestResponse> {
    try {
      const response: AxiosResponse<BacktestResponse> = await this.client.get(`/backtest/${backtestId}`);
      return response.data;
    } catch (error) {
      console.error(`Fehler beim Abrufen der Backtest-Ergebnisse für ID ${backtestId}:`, error);
      throw error;
    }
  }
}

// Export einer API-Client-Instanz
export const apiClient = new ApiClient();
export default apiClient;