"use client";
import Sidebar from '../components/Sidebar';
import PerformanceChart from '../components/PerformanceChart';
import PerformanceMetrics from '../components/OverallScore';
import RecentSessions from './Recents';
import ProfileCard from '../components/ProfileCard';
import { useParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import '../components/bg.css';

export default function Dashboard() {
    const { userId } = useParams();
    const [localUserId, setLocalUserId] = useState('');

    // Fetch userId from local storage when the component mounts
    useEffect(() => {
        const storedUserId = localStorage.getItem('userId');
        if (storedUserId) {
            setLocalUserId(storedUserId);
        }
    }, []);

    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 pl-64">
                <div className="p-6">
                    <div className="w-full">
                        <ProfileCard />
                    </div>
                    
                    {/* Chart and metrics underneath profile */}
                    <div className="w-full mt-4">
                        {/* Chart full width */}
                        <div className="pro-card p-6">
                            <PerformanceChart />
                        </div>

                        {/* Indicators row underneath chart (centered) */}
                        <div className="mt-6 flex justify-center">
                            <div className="flex gap-6 items-center flex-wrap max-w-4xl justify-center">
                                <PerformanceMetrics userId={localUserId} />
                            </div>
                        </div>
                    </div>
                    
                    <div className="w-full mt-6">
                        <RecentSessions />
                    </div>
                </div>
            </main>
        </div>
    );
}