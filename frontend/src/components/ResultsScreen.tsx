import React from 'react';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download } from 'lucide-react';
import { LogoVariant, JobProgress } from '@/types/logo';
import { Progress } from '@/components/ui/progress';

interface ResultsScreenProps {
  onBack: () => void;
  progress: JobProgress;
  variants: LogoVariant[];
  onDownload: (variant: LogoVariant) => void;
}

const statusLabels: Record<string, string> = {
  queued: 'Queued',
  generating: 'Generating designs',
  vectorizing: 'Creating vectors',
  exporting: 'Finalizing',
  done: 'Complete'
};

const ResultsScreen: React.FC<ResultsScreenProps> = ({ 
  onBack, 
  progress, 
  variants,
  onDownload 
}) => {
  const isLoading = progress.status !== 'done' && progress.status !== 'error';

  return (
    <div className="min-h-[calc(100vh-80px)] py-12 px-6">
      <div className="max-w-6xl mx-auto space-y-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Start over</span>
        </button>

        {isLoading ? (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="space-y-2">
              <h2 className="text-4xl font-light">Creating your logos</h2>
              <p className="text-muted-foreground">
                {progress.message || 'Processing your request...'}
              </p>
            </div>

            <div className="space-y-3">
              <Progress value={progress.progress} className="h-2" />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>{statusLabels[progress.status] || progress.status}</span>
                <span>{Math.round(progress.progress)}%</span>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-2 pt-4">
              {['queued', 'generating', 'vectorizing', 'exporting'].map((status, index) => (
                <div
                  key={status}
                  className={`h-1 rounded-full transition-all ${
                    progress.progress > index * 25
                      ? 'bg-foreground'
                      : 'bg-muted'
                  }`}
                />
              ))}
            </div>
          </div>
        ) : progress.status === 'error' ? (
          <div className="max-w-2xl mx-auto text-center space-y-6">
            <div className="space-y-2">
              <h2 className="text-4xl font-light">Something went wrong</h2>
              <p className="text-muted-foreground">
                {progress.message || 'Unable to generate logos. Please try again.'}
              </p>
            </div>
            <Button onClick={onBack}>Try Again</Button>
          </div>
        ) : (
          <div className="space-y-8">
            <div className="space-y-2">
              <h2 className="text-4xl font-light">Your logo variations</h2>
              <p className="text-muted-foreground">
                Click on any logo to download the SVG file
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {variants.map((variant) => (
                <button
                  key={variant.index}
                  onClick={() => onDownload(variant)}
                  className="group bg-card rounded-lg overflow-hidden border border-border hover:border-foreground transition-all"
                >
                  <div className="aspect-square bg-background flex items-center justify-center p-8">
                    <img 
                      src={variant.svg.url} 
                      alt={`Logo variant ${variant.index + 1}`}
                      className="w-full h-full object-contain"
                    />
                  </div>
                  <div className="p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        {variant.palette.name}
                      </span>
                      <Download className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <div className="flex gap-2">
                      {variant.palette.colors.map((color, i) => (
                        <div
                          key={i}
                          className="w-6 h-6 rounded-full border border-border"
                          style={{ backgroundColor: color }}
                        />
                      ))}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsScreen;
