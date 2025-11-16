import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Grid, 
  BarChart, 
  Plus, 
  User, 
  LogOut, 
  ChevronRight 
} from "lucide-react";
import "./bg.css";

// NavItem Component
const NavItem = ({ href, icon, label, active = false }) => (
  <Link href={href} className="block">
    <div className={`group relative overflow-hidden rounded-xl transition-all duration-300 ${
      active 
        ? 'bg-gray-800/50' 
        : 'hover:bg-gray-800/30'
    }`}>
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <div className="relative flex items-center p-3 space-x-3">
        <div className={`p-2 rounded-lg ${
          active 
            ? 'bg-purple-500/20 text-purple-400' 
            : 'bg-gray-700/50 text-gray-400 group-hover:bg-purple-500/20 group-hover:text-purple-300'
        } transition-colors duration-200`}>
          {React.cloneElement(icon, { 
            className: `w-5 h-5 transition-transform duration-200 ${
              active ? 'scale-110' : 'group-hover:scale-110'
            }`,
            strokeWidth: active ? 2.5 : 2
          })}
        </div>
        <span className={`text-sm font-medium ${
          active ? 'text-white' : 'text-gray-300 group-hover:text-white'
        } transition-colors duration-200`}>
          {label}
        </span>
        {active && (
          <div className="absolute right-4 w-1.5 h-6 bg-purple-400 rounded-full" />
        )}
      </div>
    </div>
  </Link>
);

export default function Sidebar() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  // Fetch user data from local storage
  useEffect(() => {
    const storedUsername = localStorage.getItem("username") || "";
    const storedEmail = localStorage.getItem("email") || "";
    setUsername(storedUsername);
    setEmail(storedEmail);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('email');
    localStorage.removeItem('userId');
    window.location.href = '/login';
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isProfileOpen && !event.target.closest('.profile-dropdown')) {
        setIsProfileOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isProfileOpen]);

  return (
    <div className="h-full">
      <aside className="fixed w-64 h-screen p-4 text-white bg-gradient-to-b from-gray-900 to-gray-800 border-r border-gray-700/50 shadow-2xl z-30 flex flex-col" style={{ left: 0, top: 0 }}>
        {/* Logo */}
        <Link href="/" className="group block py-4 px-2">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <img 
                src="/logo1.png" 
                alt="Eloquence Logo" 
                className="h-8 w-auto transition-all duration-300 group-hover:scale-110" 
              />
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-500" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">
              Eloquence
            </span>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="mt-6 flex-1 space-y-1.5 px-2">
          <NavItem 
            href="/dashboard" 
            icon={<Grid size={20} />} 
            label="Dashboard"
            active={true}
          />
          <NavItem 
            href="/allreports" 
            icon={<BarChart size={20} />} 
            label="Reports"
          />
          
          <div className="pt-6 pb-2">
            <Link href="/session" className="block">
              <button className="w-full group relative overflow-hidden rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white py-3 px-4 text-sm font-medium transition-all duration-300 shadow-lg hover:shadow-purple-500/30">
                <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <div className="relative z-10 flex items-center justify-center space-x-2">
                  <Plus size={18} className="text-white" />
                  <span>New Session</span>
                </div>
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
              </button>
            </Link>
          </div>
        </nav>
        {/* Profile Section */}
        <div className="mt-auto pt-4 px-2">
          <div className="relative group">
            <button 
              onClick={() => setIsProfileOpen(!isProfileOpen)}
              className="w-full flex items-center justify-between p-2 rounded-xl hover:bg-gray-700/50 transition-all duration-300"
              aria-expanded={isProfileOpen}
              aria-label="User profile"
            >
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold text-lg shadow-lg transition-all duration-300 group-hover:shadow-purple-500/40">
                    {username ? username.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-400 rounded-full border-2 border-gray-800 shadow-sm"></div>
                </div>
                <div className="text-left overflow-hidden">
                  <p className="text-sm font-medium text-white truncate max-w-[120px] group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-purple-300 group-hover:to-pink-300 transition-all duration-300">
                    {username || 'Guest'}
                  </p>
                  <p className="text-xs text-gray-400 font-normal truncate max-w-[120px]">
                    {email ? `${email.split('@')[0]}` : ''}
                  </p>
                </div>
              </div>
              <svg 
                className={`h-4 w-4 text-gray-500 transition-transform duration-200 ${isProfileOpen ? 'transform rotate-180 text-purple-400' : 'group-hover:text-gray-300'}`} 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown Menu */}
            {isProfileOpen && (
              <div className="absolute bottom-full left-0 right-0 mb-2 w-full bg-gray-800/95 backdrop-blur-xl rounded-xl shadow-xl z-50 overflow-hidden border border-gray-700/50 transform transition-all duration-200 origin-bottom">
                <div className="p-2">
                  <Link 
                    href="/profile"
                    className="flex items-center px-3 py-2.5 text-sm text-gray-300 hover:bg-gray-700/50 rounded-lg transition-all duration-200 group"
                    onClick={() => setIsProfileOpen(false)}
                  >
                    <div className="p-1.5 mr-3 rounded-lg bg-gray-700/50 group-hover:bg-purple-500/20 transition-colors">
                      <User size={16} className="text-gray-400 group-hover:text-purple-400" />
                    </div>
                    <span>Profile Settings</span>
                    <ChevronRight size={16} className="ml-auto text-gray-500 group-hover:text-gray-300" />
                  </Link>
                  
                  <button 
                    onClick={handleLogout}
                    className="w-full flex items-center px-3 py-2.5 text-sm text-red-400 hover:bg-red-500/10 rounded-lg transition-all duration-200 group"
                  >
                    <div className="p-1.5 mr-3 rounded-lg bg-gray-700/50 group-hover:bg-red-500/20 transition-colors">
                      <LogOut size={16} className="text-red-400 group-hover:text-red-300" />
                    </div>
                    <span>Sign Out</span>
                    <ChevronRight size={16} className="ml-auto text-gray-500 group-hover:text-red-300/70" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </aside>
    </div>
  );
}