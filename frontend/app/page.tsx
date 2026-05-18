import DashboardShell from '@/components/DashboardShell';
import NavBar from '@/components/NavBar';
import KpiStrip from '@/components/KpiStrip';
import StatusBar from '@/components/StatusBar';

export default function Home() {
  return (
    <div className="relative flex min-h-screen flex-col bg-[#050510]">
      {/* Background effects */}
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute -right-40 -top-40 h-[400px] w-[400px] rounded-full bg-cyan-400/5 blur-[120px]" />
        <div className="absolute -bottom-40 -left-40 h-[300px] w-[300px] rounded-full bg-green-400/4 blur-[100px]" />
      </div>

      {/* Grid overlay */}
      <div
        className="pointer-events-none fixed inset-0 opacity-[0.15]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }}
      />

      <NavBar />
      <KpiStrip />
      <main className="relative z-10 mx-3 my-2 flex-1">
        <DashboardShell />
      </main>
      <StatusBar />
    </div>
  );
}
