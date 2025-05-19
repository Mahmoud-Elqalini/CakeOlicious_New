import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, requiredRole }) => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    console.log('User from localStorage:', userStr);

    // Parse user data safely
    let user = {};
    try {
        user = JSON.parse(userStr || '{}');
    } catch (error) {
        console.error('Error parsing user data:', error);
    }

    console.log('Parsed user:', user);
    console.log('User role:', user.role);
    console.log('Required role:', requiredRole);

    if (!token) {
        console.log('No token found, redirecting to signin');
        return <Navigate to="/signin" replace />;
    }

    // Check if the user role matches the required role (case-insensitive)
    // Check both role and user_role fields
    const userRole = user.role || user.user_role;
    if (requiredRole && (!userRole || userRole.toLowerCase() !== requiredRole.toLowerCase())) {
        console.log('Role mismatch, redirecting to home');
        console.log(`User role: ${userRole}, Required role: ${requiredRole}`);
        return <Navigate to="/" replace />;
    }

    console.log('Access granted to protected route');
    return children;
};

export default ProtectedRoute;

{/* <Shahd></Shahd> */ }

