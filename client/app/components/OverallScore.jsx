"use client";
import React, { useEffect, useState } from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import './bg.css';

const PerformanceMetrics = () => {
    const [scores, setScores] = useState({ pace: 0, modulation: 0, clarity: 0 });
    const [reports, setReports] = useState({
        voice_report: '',
        expressions_report: '',
        vocabulary_report: ''
    });

    useEffect(() => {
        const fetchOverallScores = async () => {
            const rawUserId = localStorage.getItem('userId');
                const userId = rawUserId && rawUserId !== 'undefined' && rawUserId !== 'null' && rawUserId.trim() !== '' ? rawUserId : null;
                if (!userId) {
                    console.debug('OverallScore: no valid userId, skipping overall scores fetch');
                    return;
                }

            try {
                    const API = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:5000` : 'http://127.0.0.1:5000');
                    const response = await fetch(`${API}/user-reports?userId=${encodeURIComponent(userId)}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch overall scores');
                }
                const data = await response.json();
                
                // Map the fetched data to the scores and reports state
                setScores({
                    pace: data.avg_voice,
                    modulation: data.avg_expressions,
                    clarity: data.avg_vocabulary
                });

                setReports(data.overall_reports);
            } catch (error) {
                console.error('Error fetching overall scores:', error);
            }
        };

        fetchOverallScores();
    }, []);

    const colors = {
        pace: "#00C853",
        modulation: "#FFB300",
        clarity: "#D32F2F"
    };

    return (
        <div className="flex flex-col md:flex-row justify-center items-center gap-6 w-full p-4">
            {/* Pace Metric */}
            <div className="w-full md:w-1/3 pro-card text-white p-6 flex flex-col items-center gap-4">
                <div className="w-40 h-40">
                    <CircularProgressbar
                        value={scores.pace}
                        text={`${scores.pace}%`}
                        styles={buildStyles({
                            pathColor: colors.pace,
                            textColor: '#ffffff',
                            trailColor: 'rgba(255,255,255,0.06)',
                        })}
                    />
                </div>
                <p className="text-lg text-center card-title">
                    Voice
                </p>
            </div>

            {/* Modulation Metric */}
            <div className="w-full md:w-1/3 pro-card text-white p-6 flex flex-col items-center gap-4">
                <div className="w-40 h-40">
                    <CircularProgressbar
                        value={scores.modulation}
                        text={`${scores.modulation}%`}
                        styles={buildStyles({
                            pathColor: colors.modulation,
                            textColor: '#ffffff',
                            trailColor: 'rgba(255,255,255,0.06)',
                        })}
                    />
                </div>
                <p className="text-lg text-center card-title">
                    Expressions
                </p>
            </div>

            {/* Clarity Metric */}
            <div className="w-full md:w-1/3 pro-card text-white p-6 rounded-lg flex flex-col items-center gap-4">
                <div className="w-40 h-40">
                    <CircularProgressbar
                        value={scores.clarity}
                        text={`${scores.clarity}%`}
                        styles={buildStyles({
                            pathColor: colors.clarity,
                            textColor: '#ffffff',
                            trailColor: 'rgba(255,255,255,0.06)',
                        })}
                    />
                </div>
                <p className="text-lg text-center card-title">
                    Vocabulary
                    </p>
            </div>
        </div>
    );
};

export default PerformanceMetrics;