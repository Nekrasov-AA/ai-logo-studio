export interface LogoVariant {
  index: number;
  palette: {
    colors: string[];
    icon: string;
    font_heading: string;
    font_body: string;
    layout: string;
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

export type JobStatus = 'queued' | 'processing' | 'done' | 'error';

export interface JobProgress {
  status: JobStatus;
  progress: number;
  message?: string;
}
