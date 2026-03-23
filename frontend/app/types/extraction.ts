
export interface Insight {
  type: 'error' | 'warning' | 'info';
  source_id: string;
  message: string;
  timestamp: string; // Assuming a timestamp for insights
}

export interface Extraction {
  id: string;
  created_at: string;
  status: string; // e.g., 'completed', 'failed', 'running'
  insights?: Insight[]; // Optional insights array
  // Add other properties that are part of the Extraction object if known
}

// Interface for individual extraction results, inferred from extractions/[id].vue
export interface ExtractionResult {
  id: string;
  source: string;
  source_type: string;
  title: string;
  url: string;
  trend_score: number;
  ups: number;
  comments: number;
  created_at: string;
  description?: string;
}

export interface PaginatedResults {
  results: ExtractionResult[];
  total: number;
}
