import Link from "next/link";
import { LayoutDashboard, Users, Settings, Activity } from "lucide-react";

export function Sidebar() {
  return (
    <div className="w-64 h-screen bg-slate-900 text-white flex flex-col fixed left-0 top-0 border-r border-slate-800">
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <Activity className="text-blue-500" />
        <h1 className="font-bold text-xl tracking-tight">SENTINEL</h1>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        <Link
          href="/"
          className="flex items-center gap-3 px-4 py-3 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors"
        >
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </Link>

                <Link 

                  href="/agents" 

                  className="flex items-center gap-3 px-4 py-3 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors"

                >

                  <Users size={20} />

                  <span>Agents</span>

                </Link>

                

                <Link 

                  href="/security" 

                  className="flex items-center gap-3 px-4 py-3 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors"

                >

                  <Activity size={20} />

                  <span>Security</span>

                </Link>

                

                <Link 

                  href="/settings" 

        
          className="flex items-center gap-3 px-4 py-3 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors"
        >
          <Settings size={20} />
          <span>Settings</span>
        </Link>
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-4 py-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm text-slate-400">System Online</span>
        </div>
      </div>
    </div>
  );
}
