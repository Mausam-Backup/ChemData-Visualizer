import { useState, useEffect } from 'react';
import api from '../api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  ArcElement
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function Analysis({ datasetId }) {
    const [stats, setStats] = useState(null);
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        Promise.all([
            api.get(`datasets/${datasetId}/stats/`),
            api.get(`datasets/${datasetId}/data/`)
        ]).then(([statsRes, dataRes]) => {
            setStats(statsRes.data);
            setRecords(dataRes.data.results || dataRes.data);
            setLoading(false);
        }).catch(err => {
            console.error(err);
            setLoading(false);
        });
    }, [datasetId]);

    const downloadPDF = async () => {
        try {
            const response = await api.get(`datasets/${datasetId}/pdf/`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `report_${datasetId}.pdf`);
            document.body.appendChild(link);
            link.click();
        } catch (error) {
           console.error("PDF Download failed", error);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (!stats) return <div>Error loading data.</div>;

    const barData = {
        labels: Object.keys(stats.type_distribution),
        datasets: [
            {
                label: 'Equipment Count by Type',
                data: Object.values(stats.type_distribution),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
            },
        ],
    };

    return (
        <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
                <div className="bg-white overflow-hidden shadow rounded-lg p-5 text-center">
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Count</dt>
                    <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.total_count}</dd>
                </div>
                <div className="bg-white overflow-hidden shadow rounded-lg p-5 text-center">
                    <dt className="text-sm font-medium text-gray-500 truncate">Avg Flowrate</dt>
                    <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.average_flowrate?.toFixed(2)}</dd>
                </div>
                <div className="bg-white overflow-hidden shadow rounded-lg p-5 text-center">
                    <dt className="text-sm font-medium text-gray-500 truncate">Avg Pressure</dt>
                    <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.average_pressure?.toFixed(2)}</dd>
                </div>
                <div className="bg-white overflow-hidden shadow rounded-lg p-5 text-center">
                    <dt className="text-sm font-medium text-gray-500 truncate">Avg Temperature</dt>
                    <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.average_temperature?.toFixed(2)}</dd>
                </div>
            </div>

            {/* Charts */}
            <div className="bg-white shadow rounded-lg p-6">
                 <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Equipment Distribution</h3>
                 <div className="h-64">
                    <Bar data={barData} options={{ maintainAspectRatio: false }} />
                 </div>
            </div>

            {/* Table */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Raw Data</h3>
                    <button onClick={downloadPDF} className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
                        Download PDF
                    </button>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Flowrate</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pressure</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Temp</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {records.map((record) => (
                                <tr key={record.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{record.equipment_name}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.equipment_type}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.flowrate}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.pressure}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.temperature}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
