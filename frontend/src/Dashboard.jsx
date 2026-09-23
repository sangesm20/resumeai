import React, { useState, useEffect } from 'react';
import { UploadCloud, FileText, User, CheckCircle, AlertCircle, LogOut, UserPlus, Mail, Phone, Calendar, Briefcase, GraduationCap, Search, Zap, Award } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function Dashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('register');
  
  // Registration States
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [candEmail, setCandEmail] = useState('');
  const [dob, setDob] = useState('');
  const [expYears, setExpYears] = useState(0);
  const [gradYear, setGradYear] = useState('');
  const [regStatus, setRegStatus] = useState('idle');
  const [regMessage, setRegMessage] = useState('');

  // Upload & Scan States
  const [candidateId, setCandidateId] = useState('');
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [uploadMessage, setUploadMessage] = useState('');
  const [scanStatus, setScanStatus] = useState('idle');
  const [scanMessage, setScanMessage] = useState('');
  // 🔴 Puthu state: Scan panna data-va UI-la kaatta
  const [scanResultData, setScanResultData] = useState(null); 

  // Status Check States
  const [isCheckingStatus, setIsCheckingStatus] = useState(false);
  const [candidateExists, setCandidateExists] = useState(null);
  const [hasActiveResume, setHasActiveResume] = useState(null);

  // Search States
  const [jobDesc, setJobDesc] = useState('');
  const [searchMinExp, setSearchMinExp] = useState(0);
  const [searchGradYear, setSearchGradYear] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchStatus, setSearchStatus] = useState('idle');

  const handleLogout = () => {
    localStorage.removeItem('hr_token');
    navigate('/');
  };

  useEffect(() => {
    if (!candidateId || isNaN(candidateId)) {
      setCandidateExists(null);
      setHasActiveResume(null);
      return;
    }

    const checkStatus = async () => {
      setIsCheckingStatus(true);
      try {
        const token = localStorage.getItem('hr_token');
        try {
          await axios.get(`http://localhost:8000/candidate/${candidateId}`, { headers: { 'Authorization': `Bearer ${token}` } });
          setCandidateExists(true);
          
          const resResponse = await axios.get(`http://localhost:8000/resumes/candidate/${candidateId}`, { headers: { 'Authorization': `Bearer ${token}` } });
          if (resResponse.data && resResponse.data.length > 0) {
            setHasActiveResume(true);
          } else {
            setHasActiveResume(false);
          }
        } catch (err) {
          setCandidateExists(false);
          setHasActiveResume(false);
        }
      } finally {
        setIsCheckingStatus(false);
      }
    };

    const delayDebounceFn = setTimeout(() => checkStatus(), 500);
    return () => clearTimeout(delayDebounceFn);
  }, [candidateId]);

  const handleRegister = async (e) => {
    e.preventDefault();
    setRegStatus('loading');
    try {
      const token = localStorage.getItem('hr_token');
      const response = await axios.post('http://localhost:8000/candidate', {
        first_name: firstName, last_name: lastName, phone, email: candEmail, 
        dob, experience_years: parseInt(expYears), graduation_year: parseInt(gradYear)
      }, { headers: { 'Authorization': `Bearer ${token}` } });
      
      const newId = response.data.id || response.data.candidate_id; 
      setRegStatus('success');
      setRegMessage(`Candidate registered successfully! ID: ${newId}`);
      
      setCandidateId(newId);
      setTimeout(() => setActiveTab('upload'), 2000);
    } catch (error) {
      setRegStatus('error');
      setRegMessage(error.response?.data?.detail || "Error registering candidate.");
    }
  };

  const handleUpload = async () => {
    if (!candidateId || !file) return;
    setUploadStatus('uploading');
    setScanStatus('idle'); 
    setScanResultData(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem('hr_token');
      await axios.post(`http://localhost:8000/resumes/upload/${candidateId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data', 'Authorization': `Bearer ${token}` }
      });
      setUploadStatus('success');
      setUploadMessage("Resume uploaded! You can now scan it with AI.");
      setHasActiveResume(true); 
    } catch (error) {
      setUploadStatus('error');
      setUploadMessage(error.response?.data?.detail || "Error uploading resume.");
    }
  };

  const handleScan = async () => {
    if (!candidateId) return;
    setScanStatus('loading');
    setScanResultData(null);
    try {
      const token = localStorage.getItem('hr_token');
      const response = await axios.post(`http://localhost:8000/scan/candidate/${candidateId}`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setScanStatus('success');
      setScanMessage("AI Scan Complete! Data successfully extracted.");
      // 🔴 Backend anuppura extracted data-va save panrom
      setScanResultData(response.data);
    } catch (error) {
      setScanStatus('error');
      setScanMessage(error.response?.data?.detail || "Error during AI scan.");
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setSearchStatus('loading');
    try {
      const token = localStorage.getItem('hr_token');
      const payload = { job_description: jobDesc, min_experience: parseInt(searchMinExp) || 0, top_k: 10 };
      if (searchGradYear) payload.graduation_year = parseInt(searchGradYear);

      const response = await axios.post('http://localhost:8000/search', payload, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setSearchResults(Array.isArray(response.data) ? response.data : response.data.results || []);
      setSearchStatus('success');
    } catch (error) {
      setSearchStatus('error');
      setSearchResults([]);
    }
  };

  // Helper function to extract skills array safely
  const getSkillsArray = (data) => {
    if (!data) return [];
    if (Array.isArray(data.skills)) return data.skills;
    if (Array.isArray(data.extracted_skills)) return data.extracted_skills;
    if (typeof data.skills === 'string') return data.skills.split(',').map(s => s.trim());
    return [];
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <nav className="bg-white shadow-sm border-b border-slate-200 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="bg-blue-600 p-2 rounded-lg"><FileText className="h-6 w-6 text-white" /></div>
          <h1 className="text-2xl font-bold text-slate-800">ResumeAI</h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm font-medium text-slate-500 bg-slate-100 px-4 py-2 rounded-full">HR Dashboard</div>
          <button onClick={handleLogout} className="p-2 text-slate-400 hover:text-red-500 transition-colors"><LogOut className="h-5 w-5" /></button>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto mt-12 p-6">
        
        <div className="flex mb-6 bg-slate-200 p-1 rounded-lg">
          <button onClick={() => setActiveTab('register')} className={`flex-1 py-3 text-sm font-semibold rounded-md transition-all flex justify-center items-center gap-2 ${activeTab === 'register' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}>
            <UserPlus className="h-4 w-4" /> New Candidate
          </button>
          <button onClick={() => setActiveTab('upload')} className={`flex-1 py-3 text-sm font-semibold rounded-md transition-all flex justify-center items-center gap-2 ${activeTab === 'upload' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}>
            <UploadCloud className="h-4 w-4" /> Resume & Scan
          </button>
          <button onClick={() => setActiveTab('search')} className={`flex-1 py-3 text-sm font-semibold rounded-md transition-all flex justify-center items-center gap-2 ${activeTab === 'search' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}>
            <Search className="h-4 w-4" /> Search AI
          </button>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          
          {/* TAB 1: REGISTER */}
          {activeTab === 'register' && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <h2 className="text-xl font-bold mb-6 text-slate-800">Register New Candidate</h2>
              <form onSubmit={handleRegister} className="space-y-5">
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block text-sm font-medium text-slate-700 mb-1">First Name</label><input type="text" required value={firstName} onChange={(e) => setFirstName(e.target.value)} className="w-full px-4 py-2 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></div>
                  <div><label className="block text-sm font-medium text-slate-700 mb-1">Last Name</label><input type="text" required value={lastName} onChange={(e) => setLastName(e.target.value)} className="w-full px-4 py-2 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block text-sm font-medium text-slate-700 mb-1">Email</label><input type="email" required value={candEmail} onChange={(e) => setCandEmail(e.target.value)} className="w-full px-4 py-2 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></div>
                  <div><label className="block text-sm font-medium text-slate-700 mb-1">Phone</label><input type="text" required value={phone} onChange={(e) => setPhone(e.target.value)} className="w-full px-4 py-2 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div><label className="block text-sm font-medium text-slate-700 mb-1">DOB</label><input type="date" required value={dob} onChange={(e) => setDob(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm" /></div>
                  <div><label className="block text-sm font-medium text-slate-700 mb-1">Experience</label><input type="number" min="0" required value={expYears} onChange={(e) => setExpYears(e.target.value)} className="w-full px-4 py-2 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></div>
                  <div><label className="block text-sm font-medium text-slate-700 mb-1">Grad Year</label><input type="number" required value={gradYear} onChange={(e) => setGradYear(e.target.value)} className="w-full px-4 py-2 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></div>
                </div>
                {regStatus === 'success' && <div className="text-green-600 bg-green-50 p-3 rounded-lg flex gap-2"><CheckCircle className="h-5 w-5"/>{regMessage}</div>}
                {regStatus === 'error' && <div className="text-red-600 bg-red-50 p-3 rounded-lg flex gap-2"><AlertCircle className="h-5 w-5"/>{regMessage}</div>}
                <button type="submit" disabled={regStatus === 'loading'} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg mt-2">{regStatus === 'loading' ? 'Registering...' : 'Register Candidate'}</button>
              </form>
            </div>
          )}

          {/* TAB 2: UPLOAD & SCAN */}
          {activeTab === 'upload' && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <h2 className="text-xl font-bold mb-6 text-slate-800">Upload & AI Scan</h2>
              <div className="space-y-6">
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Candidate ID</label>
                  <input type="text" value={candidateId} onChange={(e) => setCandidateId(e.target.value)} placeholder="Enter ID to check status..." className="w-full px-4 py-3 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                  
                  {candidateId && !isNaN(candidateId) && (
                    <div className="mt-3 flex flex-col gap-2 text-sm font-medium">
                      {isCheckingStatus ? (
                        <span className="text-slate-500 animate-pulse">Checking status...</span>
                      ) : (
                        <>
                          {candidateExists === true ? (
                            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-100 text-blue-700 rounded-md w-fit"><User className="h-4 w-4"/> Candidate {candidateId} found</span>
                          ) : candidateExists === false ? (
                            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-red-100 text-red-600 rounded-md w-fit"><AlertCircle className="h-4 w-4"/> No candidate in ID {candidateId}</span>
                          ) : null}

                          {candidateExists !== null && (
                            hasActiveResume ? (
                              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-700 rounded-md w-fit"><CheckCircle className="h-4 w-4"/> active resume - yes</span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-red-100 text-red-600 rounded-md w-fit"><AlertCircle className="h-4 w-4"/> active resume - no</span>
                            )
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Resume File (PDF)</label>
                  <div className={`relative border-2 border-dashed border-slate-300 rounded-xl p-8 flex flex-col items-center bg-slate-50 ${candidateExists === false ? 'opacity-50 cursor-not-allowed' : ''}`}>
                    <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files[0])} disabled={candidateExists === false} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed" />
                    <UploadCloud className={`h-10 w-10 mb-2 ${file ? 'text-green-500' : 'text-blue-500'}`} />
                    <p className="text-sm font-medium">{file ? file.name : "Click to select resume"}</p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <button onClick={handleUpload} disabled={uploadStatus === 'uploading' || !file || !candidateId || candidateExists === false} className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2 transition-all">
                    <UploadCloud className="h-5 w-5" /> Upload File
                  </button>
                  <button onClick={handleScan} disabled={!candidateId || scanStatus === 'loading' || hasActiveResume === false} className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-300 text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2 transition-all">
                    <Zap className="h-5 w-5" /> {scanStatus === 'loading' ? 'Scanning...' : 'Extract Data (AI)'}
                  </button>
                </div>

                {uploadStatus === 'success' && <div className="text-blue-600 bg-blue-50 p-3 rounded-lg flex gap-2"><CheckCircle className="h-5 w-5"/>{uploadMessage}</div>}
                {uploadStatus === 'error' && <div className="text-red-600 bg-red-50 p-3 rounded-lg flex gap-2"><AlertCircle className="h-5 w-5"/>{uploadMessage}</div>}
                
                {/* 🔴 Scan Success and Extracted Data Display */}
                {scanStatus === 'success' && (
                  <div className="border border-green-200 bg-green-50 rounded-xl p-5 mt-4">
                    <div className="flex items-center gap-2 mb-4 border-b border-green-200 pb-3">
                      <Zap className="h-6 w-6 text-green-600" />
                      <h3 className="font-bold text-green-800 text-lg">AI Scan Complete - Extracted Data</h3>
                    </div>
                    
                    {scanResultData ? (
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="bg-white p-3 rounded-lg shadow-sm border border-green-100">
                          <span className="block text-green-600 font-semibold mb-1">Experience</span>
                          <span className="text-slate-800 font-bold text-lg">{scanResultData.experience_years ?? scanResultData.experience ?? 'N/A'} <span className="text-sm font-normal">Years</span></span>
                        </div>
                        <div className="bg-white p-3 rounded-lg shadow-sm border border-green-100">
                          <span className="block text-green-600 font-semibold mb-1">Graduation</span>
                          <span className="text-slate-800 font-bold text-lg">{scanResultData.graduation_year ?? 'N/A'}</span>
                        </div>
                        <div className="col-span-2 bg-white p-3 rounded-lg shadow-sm border border-green-100">
                          <span className="block text-green-600 font-semibold mb-2">Detected Skills</span>
                          <div className="flex flex-wrap gap-2">
                            {getSkillsArray(scanResultData).length > 0 ? (
                              getSkillsArray(scanResultData).map((skill, idx) => (
                                <span key={idx} className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-bold border border-purple-200">
                                  {skill}
                                </span>
                              ))
                            ) : (
                              <span className="text-slate-500 italic">No skills extracted</span>
                            )}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <p className="text-green-700">Data saved to DB successfully!</p>
                    )}
                  </div>
                )}

                {scanStatus === 'error' && <div className="text-red-600 bg-red-50 p-3 rounded-lg flex gap-2"><AlertCircle className="h-5 w-5"/>{scanMessage}</div>}
              </div>
            </div>
          )}

          {/* TAB 3: AI SEARCH */}
          {activeTab === 'search' && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <h2 className="text-xl font-bold mb-6 text-slate-800">Semantic AI Search</h2>
              <form onSubmit={handleSearch} className="space-y-4 mb-8">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Job Description or Required Skills</label>
                  <textarea required value={jobDesc} onChange={(e) => setJobDesc(e.target.value)} rows="3" placeholder="e.g., Looking for a React developer with FastAPI backend experience..." className="w-full px-4 py-3 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"></textarea>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block text-sm font-medium text-slate-700 mb-1">Min Experience (Years)</label><input type="number" min="0" value={searchMinExp} onChange={(e) => setSearchMinExp(e.target.value)} className="w-full px-4 py-2 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></div>
                  <div><label className="block text-sm font-medium text-slate-700 mb-1">Graduation Year (Optional)</label><input type="number" value={searchGradYear} onChange={(e) => setSearchGradYear(e.target.value)} placeholder="e.g., 2024" className="w-full px-4 py-2 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" /></div>
                </div>
                <button type="submit" disabled={searchStatus === 'loading'} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg flex justify-center items-center gap-2">
                  <Search className="h-5 w-5" /> {searchStatus === 'loading' ? 'Searching Database...' : 'Find Best Candidates'}
                </button>
              </form>

              {/* SEARCH RESULTS */}
              {searchStatus === 'success' && (
                <div className="space-y-4">
                  <h3 className="font-bold text-slate-800 border-b pb-2">Top Matches ({searchResults.length})</h3>
                  {searchResults.length === 0 ? (
                    <p className="text-slate-500">No candidates match your criteria.</p>
                  ) : (
                    searchResults.map((cand, idx) => {
                      // Backend might return match_score, score, or similarity
                      const rawScore = cand.match_score || cand.score || cand.similarity || 0;
                      const percentage = Math.round(rawScore * 100);
                      
                      return (
                        <div key={idx} className="p-5 border-2 border-slate-200 rounded-xl bg-white hover:border-indigo-300 hover:shadow-md transition-all">
                          
                          <div className="flex justify-between items-start mb-4">
                            <div>
                              <h4 className="font-bold text-indigo-700 text-xl">{cand.first_name} {cand.last_name}</h4>
                              <p className="text-sm text-slate-500 font-medium">Candidate ID: {cand.id || cand.candidate_id}</p>
                            </div>
                            
                            {/* 🔴 Highlighting Matching % */}
                            {rawScore > 0 && (
                              <div className="flex flex-col items-end">
                                <span className={`flex items-center gap-1 font-bold px-3 py-1.5 rounded-lg text-sm ${percentage >= 75 ? 'bg-green-100 text-green-700' : percentage >= 50 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                                  <Award className="h-4 w-4" /> Match: {percentage}%
                                </span>
                              </div>
                            )}
                          </div>

                          <div className="text-sm text-slate-700 grid grid-cols-2 gap-y-3 bg-slate-50 p-4 rounded-lg">
                            <p><span className="font-semibold block text-slate-500 text-xs uppercase tracking-wider">Email</span> {cand.email}</p>
                            <p><span className="font-semibold block text-slate-500 text-xs uppercase tracking-wider">Phone</span> {cand.phone}</p>
                            <p><span className="font-semibold block text-slate-500 text-xs uppercase tracking-wider">Experience</span> {cand.experience_years ?? 0} Years</p>
                            {cand.graduation_year && <p><span className="font-semibold block text-slate-500 text-xs uppercase tracking-wider">Grad Year</span> {cand.graduation_year}</p>}
                          </div>
                          
                          {/* 🔴 Search Result-layum Skills kaatta (if backend sends it) */}
                          {getSkillsArray(cand).length > 0 && (
                            <div className="mt-4 pt-3 border-t border-slate-100">
                              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 block">Matched Skills</span>
                              <div className="flex flex-wrap gap-2">
                                {getSkillsArray(cand).map((skill, i) => (
                                  <span key={i} className="bg-indigo-50 text-indigo-600 px-2.5 py-1 rounded-md text-xs font-medium border border-indigo-100">
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )
                    })
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}