export interface LogoVariant {
  index: number;
  palette: {
    name: string;
    colors: string[];
  };
  svg: {
    s3_key: string;
    url: string;
  };
}

export interface FormData {
  businessName: string;
  industry: string;
  style: string;
  colors: string[];
  description: string;
}

export type JobStatus = 'queued' | 'generating' | 'vectorizing' | 'exporting' | 'done' | 'error';

export interface JobProgress {
  status: JobStatus;
  progress: number;
  message?: string;
}
