import React, { useState } from 'react';
import Header from '@/components/Header';
import WelcomeScreen from '@/components/WelcomeScreen';
import LogoForm from '@/components/LogoForm';
import ResultsScreen from '@/components/ResultsScreen';
import { FormData, LogoVariant, JobProgress } from '@/types/logo';
import { useToast } from '@/hooks/use-toast';

type AppState = 'welcome' | 'form' | 'results';

const API = import.meta.env.VITE_API_URL as string;

const Index = () => {
  const [appState, setAppState] = useState<AppState>('welcome');
  const [progress, setProgress] = useState<JobProgress>({ status: 'queued', progress: 0 });
  const [variants, setVariants] = useState<LogoVariant[]>([]);
  const { toast } = useToast();

  const handleFormSubmit = async (formData: FormData) => {
    setAppState('results');
    setProgress({ status: 'queued', progress: 10 });
    setVariants([]);

    try {
      const res = await fetch(`${API}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          business_type: formData.industry || formData.businessName,
          preferences: {
            business_name: formData.businessName,
            industry: formData.industry,
            style: formData.style,
            colors: formData.colors,
            description: formData.description,
          },
        }),
      });

      if (!res.ok) throw new Error('Failed to start generation');
      const { job_id } = await res.json();
      setProgress({ status: 'processing', progress: 30 });

      // Poll every 500 ms, max 30 attempts (15 s)
      for (let i = 0; i < 30; i++) {
        await new Promise(r => setTimeout(r, 500));
        setProgress({ status: 'processing', progress: Math.min(35 + i * 2, 90) });

        const poll = await fetch(`${API}/api/result/${job_id}`);
        if (!poll.ok) continue;
        const result = await poll.json();

        if (result.status === 'done') {
          const parsed: LogoVariant[] = (result.variants ?? []).map((v: LogoVariant) => ({
            ...v,
            svg: { ...v.svg, url: `${API}${v.svg.url}` },
          }));
          setVariants(parsed);
          setProgress({ status: 'done', progress: 100 });
          toast({
            title: 'Logos ready!',
            description: `${parsed.length} variations generated.`,
          });
          return;
        }

        if (result.status === 'failed' || result.status === 'error') {
          throw new Error('Generation failed on server');
        }
      }

      throw new Error('Timed out — please try again');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setProgress({ status: 'error', progress: 0, message });
      toast({ title: 'Generation failed', description: message, variant: 'destructive' });
    }
  };

  const handleDownload = async (variant: LogoVariant) => {
    try {
      const res = await fetch(variant.svg.url);
      if (!res.ok) throw new Error('Download failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `logo-${variant.palette.layout}-${variant.index + 1}.svg`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      toast({ title: 'Download failed', description: 'Please try again.', variant: 'destructive' });
    }
  };

  const handleBack = () => {
    setAppState('welcome');
    setVariants([]);
    setProgress({ status: 'queued', progress: 0 });
  };

  const handleGenerateAgain = () => {
    setAppState('form');
    setVariants([]);
    setProgress({ status: 'queued', progress: 0 });
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header status="online" />

      {appState === 'welcome' && (
        <WelcomeScreen onGetStarted={() => setAppState('form')} />
      )}

      {appState === 'form' && (
        <LogoForm onBack={handleBack} onSubmit={handleFormSubmit} />
      )}

      {appState === 'results' && (
        <ResultsScreen
          onBack={handleBack}
          onGenerateAgain={handleGenerateAgain}
          progress={progress}
          variants={variants}
          onDownload={handleDownload}
        />
      )}
    </div>
  );
};

export default Index;
