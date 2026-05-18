import DashboardShell from '@/components/DashboardShell';
import NavBar from '@/components/NavBar';
import KpiStrip from '@/components/KpiStrip';
import StatusBar from '@/components/StatusBar';
import MacroPanel from '@/components/MacroPanel';

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
        <div className="mt-3">
          <MacroPanel />
        </div>
      </main>
      <StatusBar />
    </div>
  );
}
