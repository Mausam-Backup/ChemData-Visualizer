import { useState, useEffect } from 'react';
import api from '../api';

export default function Dashboard({ onSelect }) {
    const [datasets, setDatasets] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [file, setFile] = useState(null);

    const fetchDatasets = async () => {
        try {
            const res = await api.get('datasets/');
            setDatasets(res.data.results || res.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchDatasets();
    }, []);

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        setUploading(true);
        try {
            await api.post('upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setFile(null);
            fetchDatasets();
        } catch (err) {
            alert('Upload failed: ' + (err.response?.data?.error || err.message));
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
                <div className="md:grid md:grid-cols-3 md:gap-6">
                    <div className="md:col-span-1">
                        <h3 className="text-lg font-medium leading-6 text-gray-900">Upload New Dataset</h3>
                        <p className="mt-1 text-sm text-gray-500">
                            Upload a CSV file containing equipment data.
                        </p>
                    </div>
                    <div className="mt-5 md:mt-0 md:col-span-2">
                        <form onSubmit={handleUpload} className="space-y-4">
                            <div>
                                <input
                                    type="file"
                                    accept=".csv"
                                    onChange={(e) => setFile(e.target.files[0])}
                                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={!file || uploading}
                                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none disabled:bg-gray-400"
                            >
                                {uploading ? 'Uploading...' : 'Upload'}
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Uploads</h3>
                </div>
                <ul className="divide-y divide-gray-200">
                    {datasets.map((ds) => (
                        <li key={ds.id}>
                            <a href="#" onClick={(e) => { e.preventDefault(); onSelect(ds.id); }} className="block hover:bg-gray-50">
                                <div className="px-4 py-4 sm:px-6">
                                    <div className="flex items-center justify-between">
                                        <p className="text-sm font-medium text-indigo-600 truncate">
                                            Dataset #{ds.id}
                                        </p>
                                        <div className="ml-2 flex-shrink-0 flex">
                                            <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                                {new Date(ds.uploaded_at).toLocaleString()}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="mt-2 sm:flex sm:justify-between">
                                        <div className="sm:flex">
                                            <p className="flex items-center text-sm text-gray-500">
                                                {ds.file.split('/').pop()}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </a>
                        </li>
                    ))}
                    {datasets.length === 0 && (
                        <li className="px-4 py-4 sm:px-6 text-center text-gray-500">No datasets found.</li>
                    )}
                </ul>
            </div>
        </div>
    );
}
