</div>
              </div>
            </div>
          </div>
          
          {/* Navigation */}
          <nav className="flex space-x-8 pb-4">
            {[
              { id: 'marketplace', label: 'Marketplace', icon: ShoppingCart },
              { id: 'portfolio', label: 'Portfolio', icon: Wallet },
              { id: 'trade', label: 'Trade', icon: TrendingUp },
              { id: 'analytics', label: 'Analytics', icon: BarChart3 }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setCurrentView(id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
              import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { Leaf, TrendingUp, DollarSign, Recycle, ShoppingCart, Wallet, BarChart3, Building2, Globe, Award } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const CarbonMarketplace = () => {
  const [currentView, setCurrentView] = useState('marketplace');
  const [currentUser, setCurrentUser] = useState('user1');
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [portfolio, setPortfolio] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);

  // API calls
  const fetchData = async (endpoint) => {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`);
      if (!response.ok) throw new Error('API call failed');
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      // Fallback to mock data if API is not available
      return getMockData(endpoint);
    }
  };

  const postData = async (endpoint, data) => {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('API call failed');
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      return { error: 'API not available - using mock mode' };
    }
  };

  // Mock data fallback
  const getMockData = (endpoint) => {
    const mockData = {
      '/users': [
        { id: 'user1', name: 'GreenCorp Inc.', balance: 100000, retired_credits: 30 },
        { id: 'user2', name: 'EcoStart Ltd.', balance: 50000, retired_credits: 12 },
        { id: 'user3', name: 'Sustainable Dynamics', balance: 75000, retired_credits: 18 },
        { id: 'user4', name: 'Carbon Neutral Co.', balance: 120000, retired_credits: 25 }
      ],
      '/projects': [
        { id: 'proj1', name: 'Amazon Reforestation', project_type: 'Forestry', location: 'Brazil', available_credits: 10000, price_per_credit: 42.50, verification_standard: 'VCS', description: 'Large-scale reforestation project in the Amazon rainforest' },
        { id: 'proj2', name: 'Wind Power Texas', project_type: 'Renewable Energy', location: 'USA', available_credits: 15000, price_per_credit: 38.75, verification_standard: 'Gold Standard', description: 'Wind farm generating clean electricity' },
        { id: 'proj3', name: 'Methane Capture', project_type: 'Waste Management', location: 'Germany', available_credits: 8000, price_per_credit: 52.30, verification_standard: 'VCS', description: 'Landfill methane capture system' },
        { id: 'proj4', name: 'Solar Farm India', project_type: 'Renewable Energy', location: 'India', available_credits: 12000, price_per_credit: 35.60, verification_standard: 'CDM', description: 'Utility-scale solar installation' },
        { id: 'proj5', name: 'Ocean Cleanup', project_type: 'Nature-based', location: 'Pacific Ocean', available_credits: 5000, price_per_credit: 65.80, verification_standard: 'Blue Carbon', description: 'Marine ecosystem restoration project' }
      ],
      [`/portfolio/${currentUser}`]: [
        { project_id: 'proj1', project_name: 'Amazon Reforestation', project_type: 'Forestry', credits: 25, avg_purchase_price: 42.50, current_price: 42.50 },
        { project_id: 'proj2', project_name: 'Wind Power Texas', project_type: 'Renewable Energy', credits: 15, avg_purchase_price: 38.75, current_price: 38.75 }
      ],
      '/transactions': [
        { id: '1', user_name: 'GreenCorp Inc.', project_name: 'Amazon Reforestation', transaction_type: 'BUY', quantity: 25, price_per_credit: 42.50, total_amount: 1062.50, timestamp: new Date().toISOString() },
        { id: '2', user_name: 'EcoStart Ltd.', project_name: 'Solar Farm India', transaction_type: 'BUY', quantity: 20, price_per_credit: 35.60, total_amount: 712.00, timestamp: new Date(Date.now() - 86400000).toISOString() }
      ],
      '/analytics': {
        market_stats: { total_trades: 45, total_volume: 1250, avg_price: 42.30, total_retired: 85 },
        project_distribution: [
          { project_type: 'Renewable Energy', count: 4, total_credits: 45000 },
          { project_type: 'Forestry', count: 2, total_credits: 30000 },
          { project_type: 'Waste Management', count: 1, total_credits: 8000 }
        ]
      }
    };
    return mockData[endpoint] || [];
  };

  // Load data on component mount and user change
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      const [usersData, projectsData, portfolioData, transactionsData, analyticsData] = await Promise.all([
        fetchData('/users'),
        fetchData('/projects'),
        fetchData(`/portfolio/${currentUser}`),
        fetchData(`/transactions?user_id=${currentUser}&limit=20`),
        fetchData('/analytics')
      ]);
      
      setUsers(usersData);
      setProjects(projectsData);
      setPortfolio(portfolioData);
      setTransactions(transactionsData);
      setAnalytics(analyticsData);
      setLoading(false);
    };
    
    loadData();
  }, [currentUser]);

  // Trading functions
  const buyCredits = async (projectId, quantity, price) => {
    const result = await postData('/buy', {
      user_id: currentUser,
      project_id: projectId,
      quantity: parseInt(quantity),
    });
    
    if (result.error) {
      showAlert(result.error, 'error');
    } else {
      showAlert(`Successfully purchased ${quantity} credits`, 'success');
      // Reload data
      window.location.reload();
    }
  };

  const retireCredits = async (projectId, quantity) => {
    const result = await postData('/retire', {
      user_id: currentUser,
      project_id: projectId,
      quantity: parseInt(quantity)
    });
    
    if (result.error) {
      showAlert(result.error, 'error');
    } else {
      showAlert(`Successfully retired ${quantity} credits - ${quantity} tons CO₂ offset!`, 'success');
      window.location.reload();
    }
  };

  const showAlert = (message, type) => {
    setAlert({ message, type });
    setTimeout(() => setAlert(null), 5000);
  };

  // Component helpers
  const getCurrentUserData = () => users.find(u => u.id === currentUser) || {};
  const getTotalCredits = () => portfolio.reduce((sum, item) => sum + item.credits, 0);
  const getTotalValue = () => portfolio.reduce((sum, item) => sum + (item.credits * item.current_price), 0);

  const COLORS = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4', '#795548'];

  // Main render
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      {/* Header */}
      <div className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <Leaf className="h-10 w-10 text-green-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">CarbonTrade Pro</h1>
                <p className="text-gray-600">Professional Carbon Offset Marketplace</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <select 
                value={currentUser} 
                onChange={(e) => setCurrentUser(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                {users.map(user => (
                  <option key={user.id} value={user.id}>{user.name}</option>
                ))}
              </select>
              
              <div className="text-right">
                <div className="text-sm text-gray-600">Balance</div>
                <div className="text-xl font-bold text-green-600">
                  ${getCurrentUserData().balance?.toLocaleString() || '0'}
