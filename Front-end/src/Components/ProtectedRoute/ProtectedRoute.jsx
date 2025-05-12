import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, requiredRole }) => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    console.log('User from localStorage:', userStr);

    const user = JSON.parse(userStr || '{}');

    console.log('Parsed user:', user);
    console.log('User role:', user.role);
    console.log('Required role:', requiredRole);

    if (!token) {
        console.log('No token found, redirecting to signin');
        return <Navigate to="/signin" replace />;
    }

    if (requiredRole && user.role?.toLowerCase() !== requiredRole.toLowerCase()) {
        console.log('Role mismatch, redirecting to home');
        return <Navigate to="/" replace />;
    }

    console.log('Access granted to protected route');
    return children;
};

export default ProtectedRoute;

{/* <Shahd></Shahd> */ }

