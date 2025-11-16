"use client";
import React, { useEffect, useState } from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import Link from 'next/link';
import '../components/bg.css';
import { useRouter } from 'next/navigation';

const RecentSessions = ({ sessions }) => {
  const router = useRouter();
  const [userReports, setUserReports] = useState([]); // State to store user reports
  // we'll show only the recent 5 sessions
  const reportsPerPage = 5; // Number of reports to display

  // Fetch user reports from the backend
  useEffect(() => {
    const fetchUserReports = async () => {
      const rawUserId = localStorage.getItem('userId');
      const userId = rawUserId && rawUserId !== 'undefined' && rawUserId !== 'null' && rawUserId.trim() !== '' ? rawUserId : null;
      if (!userId) {
        console.debug('Recents: no valid userId, skipping reports fetch');
        return;
      }

      try {
  const API = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:5000` : 'http://127.0.0.1:5000');
  const response = await fetch(`${API}/user-reports-list?userId=${encodeURIComponent(userId)}`);
        if (!response.ok) {
          // try to parse backend error message for debugging
          let err = `Status ${response.status}`;
          try { const j = await response.json(); err = j.error || JSON.stringify(j); } catch(e){}
          throw new Error(`Failed to fetch reports: ${err}`);
        }
        const data = await response.json();
        setUserReports(data); // Set the fetched reports in state
      } catch (error) {
        console.error('Error fetching reports:', error);
      }
    };

    fetchUserReports();
  }, []);

  // recent 5
  const currentReports = userReports.slice(0, reportsPerPage);

  // Handle click to navigate to full report page
  const handleRowClick = (report) => {
    // navigate to report page and pass report id or serialized report
    router.push(`/report?report=${encodeURIComponent(JSON.stringify(report))}`);
  };


  return (
    <>
    <div className='flex flex-col w-full items-center justify-center '>
    <div className="w-full overflow-hidden rounded-lg"> 
      <div className="max-h-[360px] overflow-y-auto">
        <table className="w-full text-center text-gray-500">
          <thead className="uppercase text-white bg-transparent"> 
            <tr>
              <th scope="col" className="pr-1 py-2 text-[12px] sm:text-sm">Session<br />Name</th>
              <th scope="col" className="px-1 py-2 text-[12px] sm:text-sm">Voice</th>
              <th scope="col" className="px-1 py-2 text-[12px] sm:text-sm">Body Language</th>
              <th scope="col" className="pr-2 py-2 text-[12px] sm:text-sm">Vocabulary</th>
            </tr>
          </thead>
          <tbody>
            {currentReports.map((report) => (
              <tr
                key={report._id}
                onClick={() => handleRowClick(report)}
                className="bg-transparent border-b border-slate-700 hover:bg-[rgba(255,255,255,0.02)] text-white cursor-pointer transition-all duration-300"
              >
                <td className="px-4 py-3 text-left text-[12px] sm:text-sm">
                  <div className="font-medium">{report.title || 'Untitled Session'}</div>
                  <div className="muted-text text-sm">{report.context || ''}</div>
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="w-12 h-12 mx-auto">
                    <CircularProgressbar
                      value={report.scores?.voice || 0}
                      text={`${report.scores?.voice || 0}%`}
                      styles={buildStyles({
                        pathColor: 'var(--accent)',
                        textColor: '#ffffff',
                        trailColor: 'rgba(255,255,255,0.04)'
                      })}
                    />
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="w-12 h-12 mx-auto">
                    <CircularProgressbar
                      value={report.scores?.expressions || 0}
                      text={`${report.scores?.expressions || 0}%`}
                      styles={buildStyles({
                        pathColor: 'var(--accent-2)',
                        textColor: '#ffffff',
                        trailColor: 'rgba(255,255,255,0.04)'
                      })}
                    />
                  </div>
                </td>
                <td className="px-4 py-3 text-center">
                  <div className="w-12 h-12 mx-auto">
                    <CircularProgressbar
                      value={report.scores?.vocabulary || 0}
                      text={`${report.scores?.vocabulary || 0}%`}
                      styles={buildStyles({
                        pathColor: 'var(--danger)',
                        textColor: '#ffffff',
                        trailColor: 'rgba(255,255,255,0.04)'
                      })}
                    />
                  </div>
                </td>
              </tr>
            ))}
            {currentReports.length === 0 && (
              <tr className="h-full">
                <td colSpan="4">
                  <div className="flex justify-center items-center my-6">
                    <div className="pro-card p-6 w-full md:w-3/4 text-center">
                      <h3 className="text-2xl text-white mb-2">No Records</h3>
                      <p className="muted-text mb-4">You don't have any recorded sessions yet. Record your first session to see insights and reports here.</p>
                      <Link href="/session">
                        <button className="bg-[var(--primary)] text-white px-5 py-2 rounded-lg">Record Session</button>
                      </Link>
                    </div>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      </div>
      </div>
      </>
  );
};

export default RecentSessions;