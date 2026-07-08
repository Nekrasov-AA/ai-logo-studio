import React from 'react';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download, RefreshCw } from 'lucide-react';
import { LogoVariant, JobProgress } from '@/types/logo';
import { Progress } from '@/components/ui/progress';

interface ResultsScreenProps {
  onBack: () => void;
  onGenerateAgain: () => void;
  progress: JobProgress;
  variants: LogoVariant[];
  onDownload: (variant: LogoVariant) => void;
}

const layoutLabel: Record<string, string> = {
  centered: 'Centered',
  horizontal: 'Horizontal',
  badge: 'Badge',
  minimal: 'Minimal',
};

const ResultsScreen: React.FC<ResultsScreenProps> = ({
  onBack,
  onGenerateAgain,
  progress,
  variants,
  onDownload,
}) => {
  const isLoading = progress.status !== 'done' && progress.status !== 'error';

  return (
    <div className="min-h-[calc(100vh-80px)] py-12 px-6">
      <div className="max-w-4xl mx-auto space-y-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Start over</span>
        </button>

        {isLoading && (
          <div className="max-w-2xl space-y-6">
            <div className="space-y-1">
              <h2 className="text-4xl font-light">Generating your logo</h2>
              <p className="text-muted-foreground text-sm">
                Building variations — this takes just a moment
              </p>
            </div>
            <div className="space-y-2">
              <Progress value={progress.progress} className="h-1.5" />
              <span className="text-xs text-muted-foreground">{progress.progress}%</span>
            </div>
          </div>
        )}

        {progress.status === 'error' && (
          <div className="max-w-2xl space-y-6">
            <h2 className="text-4xl font-light">Something went wrong</h2>
            <p className="text-muted-foreground">
              {progress.message ?? 'Unable to generate logos.'}
            </p>
            <Button onClick={onGenerateAgain}>Try again</Button>
          </div>
        )}

        {progress.status === 'done' && variants.length > 0 && (
          <div className="space-y-8">
            <div className="space-y-1">
              <h2 className="text-4xl font-light">Your logo variations</h2>
              <p className="text-muted-foreground text-sm">
                {variants.length} options — download any as SVG
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {variants.map((variant) => (
                <div
                  key={variant.index}
                  className="bg-card rounded-lg border border-border overflow-hidden flex flex-col"
                >
                  <div className="bg-white flex items-center justify-center h-48 p-6">
                    <img
                      src={variant.svg.url}
                      alt={`Logo variant ${variant.index + 1}`}
                      className="max-h-full max-w-full object-contain"
                    />
                  </div>
                  <div className="p-4 flex items-center justify-between border-t border-border">
                    <div className="space-y-1.5">
                      <span className="text-sm font-medium">
                        {layoutLabel[variant.palette.layout] ?? variant.palette.layout}
                      </span>
                      <div className="flex gap-1.5">
                        {variant.palette.colors.map((color, i) => (
                          <div
                            key={i}
                            className="w-4 h-4 rounded-full border border-border"
                            style={{ backgroundColor: color }}
                            title={color}
                          />
                        ))}
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onDownload(variant)}
                      className="gap-1.5 shrink-0"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Download SVG
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-4 pt-2">
              <Button onClick={onGenerateAgain} variant="outline" className="gap-2">
                <RefreshCw className="w-4 h-4" />
                Generate again
              </Button>
              <span className="text-sm text-muted-foreground">
                Try different colors, style, or industry
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsScreen;
