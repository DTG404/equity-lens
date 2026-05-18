import DashboardShell from '@/components/DashboardShell';
import NavBar from '@/components/NavBar';
import KpiStrip from '@/components/KpiStrip';
import StatusBar from '@/components/StatusBar';

export default function Home() {
  return (
    <div className="relative flex min-h-screen flex-col">
      {/* Cosmic eclipse background */}
      <div className="cosmic-bg" />
      <div className="cosmic-noise" />

      <NavBar />
      <KpiStrip />
      <main className="relative z-10 mx-3 my-2 flex-1">
        <DashboardShell />
      </main>
      <StatusBar />
    </div>
  );
}
