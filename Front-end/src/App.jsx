// Shahd Elwan
import { useState, useEffect, Suspense, lazy } from 'react'
import './App.css'
import Layout from './Components/Layout/Layout'
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import { AnimatePresence, motion } from 'framer-motion'
const HomePage = lazy(() => import('./Pages/HomePage/HomePage'))
const ProductsPage = lazy(() => import('./Pages/ProductsPage/ProductsPage'))
const NotFound = lazy(() => import('./Pages/NotFound/NotFound'))
const SignIn = lazy(() => import('./Pages/SignIn/SignIn'))
const SignUp = lazy(() => import('./Pages/SignUp/SignUp'))
const AdminDashboard = lazy(() => import('./Pages/Admin/Dashboard'))
const AdminProducts = lazy(() => import('./Pages/Admin/Products/AdminProducts'))
const Account = lazy(() => import('./Pages/Account/Account'))
import ProtectedRoute from './Components/ProtectedRoute/ProtectedRoute'
import ErrorBoundary from './Components/ErrorBoundary/ErrorBoundary'
import AdminUsers from './Pages/Admin/Users/AdminUsers'

// Animated content wrapper
const AnimatedContent = ({ children }) => {
  const pageVariants = {
    initial: {
      opacity: 0,
      y: 5
    },
    in: {
      opacity: 1,
      y: 0
    },
    out: {
      opacity: 0,
      y: -5
    }
  };
  
  const pageTransition = {
    type: "tween",
    ease: "easeOut",
    duration: 0.2
  };

  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={pageTransition}
      className="page-content"
    >
      {children}
    </motion.div>
  );
};

// Main app routes with layout wrapper
const AppRoutes = () => {
  const location = useLocation();
  
  return (
    <Layout>
      <AnimatePresence mode="wait" initial={false}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={
            <AnimatedContent>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <HomePage />
              </Suspense>
            </AnimatedContent>
          } />
          <Route path="/products" element={
            <AnimatedContent>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <ProductsPage />
              </Suspense>
            </AnimatedContent>
          } />
          <Route path="/signin" element={
            <AnimatedContent>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <SignIn />
              </Suspense>
            </AnimatedContent>
          } />
          <Route path="/signup" element={
            <AnimatedContent>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <SignUp />
              </Suspense>
            </AnimatedContent>
          } />
          <Route path="/account" element={
            <AnimatedContent>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <Account />
              </Suspense>
            </AnimatedContent>
          } />
          <Route path="*" element={
            <AnimatedContent>
              <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
                <NotFound />
              </Suspense>
            </AnimatedContent>
          } />
        </Routes>
      </AnimatePresence>
    </Layout>
  );
};

// Admin routes
const AdminRoutes = () => {
  return (
    <Routes>
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/products"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminProducts />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminUsers />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
};

function App() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.text();
        setMessage(data);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching home data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHomeData();
  }, []);

  return (
    <Router>
      <ErrorBoundary>
        <Routes>
          <Route path="/admin/*" element={<AdminRoutes />} />
          <Route path="/*" element={<AppRoutes />} />
        </Routes>
      </ErrorBoundary>
      <ToastContainer position="top-right" autoClose={3000} />
    </Router>
  )
}

export default App
